from datetime import datetime
from dataclasses import dataclass
from typing import List, TypedDict, Optional
from supabase import create_client, Client
from dotenv import load_dotenv
import json
import os
import logging
from rcs import Pinnacle, Card, Action
import openai
import random
import database
from const import RANDOM_CATEGORIES

load_dotenv()

client = Pinnacle(api_key=os.environ["PINNACLE_API_KEY"])


@dataclass
class FunFactsSubscriber:
    created_at: datetime
    phone_number: str
    name: str
    is_subscribed: bool


class FunFact(TypedDict):
    factTitle: str
    fact: str
    imgSrc: str


def send_fun_facts(to: str, fun_facts: List[FunFact]):
    cards = []
    for fact in fun_facts:
        card = Card(
            title=fact["factTitle"],
            subtitle=fact["fact"],
            media_url=fact["imgSrc"],
        )
        cards.append(card)

    quick_replies: List[Action] = [
        Action(title=f"About this Project", payload=f"ABOUT", type="trigger"),
        Action(title="More Fun Facts 🦝", payload="SEE_MORE", type="trigger"),
        Action(title="Opt out", payload="OPT_OUT", type="trigger"),
    ]

    try:
        res = client.send.rcs(
            from_="test",
            to=to,
            cards=cards,
            quick_replies=quick_replies,
            request_options={
                "additional_headers": {
                    "ROCKET-RACCOON-FLOW-CHANGE": "fun_facts",
                }
            },
        )
        print(f"res {res}")
        logging.info(f"Successfully sent {len(fun_facts)} facts to {to}")
        print(f"Successfully sent {len(fun_facts)} facts to {to}")
    except Exception as e:
        logging.error(f"Failed to send facts to {to}: {str(e)}")
        print(f"Failed to send facts to {to}: {str(e)}")


def send_about_project(to: str):
    quick_replies: List[Action] = [
        Action(title="More Fun Facts 🦝", payload="SEE_MORE", type="trigger"),
        Action(title="Opt out", payload="OPT_OUT", type="trigger"),
    ]

    try:
        res = client.send.rcs(
            from_="test",
            to=to,
            text="This project shares fun and interesting facts with you daily. Stay curious and enjoy learning new things!",
            quick_replies=quick_replies,
        )
        print(f"res {res}")
        logging.info(f"Successfully sent about project to {to}")
        print(f"Successfully sent about project to {to}")
    except Exception as e:
        logging.error(f"Failed to send about project to {to}: {str(e)}")
        print(f"Failed to send about project to {to}: {str(e)}")


# Initialize Supabase client
supabase_url = os.environ["SUPABASE_URL"]
supabase_key = os.environ["SUPABASE_KEY"]
supabase: Client = create_client(supabase_url, supabase_key)


def send_more(to: str):
    logging.info("Sending more fun facts to %s...", to)
    client.send.rcs(
        from_="test",
        to=to,
        text="Generating more fun facts. Please wait...",
        request_options={
            "additional_headers": {
                "ROCKET-RACCOON-FLOW-CHANGE": "fun_facts",
            }
        },
    )
    send_fun_facts(to, get_fun_facts(5, to))
    logging.info("More fun facts sent to %s!", to)


def get_fun_facts(count: int, to: Optional[str] = None) -> List[FunFact]:
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"You will provide me with {count} completely random and great fun facts in JSON format. I want you to provide me with fun facts that are educational and interesting and different from one another. Also provide a title for each fun fact. Make sure these fun facts are FULLY compliant with OpenAI's safety policy. Make sure to provide different fun facts every day based on the date and a random seed. Here are the fun facts for {datetime.now().strftime('%Y-%m-%d')} based on the random seed {random.randint(0, 100000000)}:",
            },
            (
                {
                    "role": "user",
                    "content": f"Make sure there are no duplicates. Here are the last few fun facts: {database.get(to)}",
                }
                if to
                else {
                    "role": "user",
                    "content": f"I want to learn something new today. Give me some fun facts about {','.join(random.sample(RANDOM_CATEGORIES, 3))}",
                }
            ),
        ],
        temperature=1,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "fun_facts_schema",
                "description": f"A list of {count} fun facts",
                "schema": {
                    "type": "object",
                    "properties": {
                        "fun_facts": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "factTitle": {"type": "string"},
                                    "fact": {"type": "string"},
                                },
                                "required": ["factTitle", "fact"],
                            },
                            "minItems": count,
                            "maxItems": count,
                        },
                    },
                    "additionalProperties": False,
                },
            },
        },
    )

    if response.choices[0].message.content:
        fun_facts = json.loads(response.choices[0].message.content)["fun_facts"]
    else:
        fun_facts = {}

    def generate_image(fact):
        return openai.images.generate(
            model="dall-e-3",
            prompt=f"Design an educational and realistic image for the following fun fact. Do not include text. Here is the fun fact: {fact['fact']}",
            n=1,
            size="1024x1024",
        )

    image_responses = [generate_image(fact) for fact in fun_facts]

    images = [image_response.data[0].url or "" for image_response in image_responses]

    if to:
        database.set(to, [fact["factTitle"] for fact in fun_facts])

    return [
        FunFact(fact=fact["fact"], factTitle=fact["factTitle"], imgSrc=imgSrc)
        for fact, imgSrc in zip(fun_facts, images)
    ]


def daily_send_fun_facts():
    logging.info("Generating fun facts...")
    print("Generating fun facts...")

    fun_facts = get_fun_facts(5)

    if fun_facts:
        print("Fun facts:", fun_facts)
        logging.info("Found fun facts: %s", fun_facts)
        subscribers = get_all_subscribers()

        for subscriber in subscribers:
            if subscriber.is_subscribed:
                try:
                    send_fun_facts(subscriber.phone_number, fun_facts)
                    logging.info(
                        f"Sent fun facts to {subscriber.name} ({subscriber.phone_number})"
                    )
                    print(
                        f"Sent fun facts to {subscriber.name} ({subscriber.phone_number})"
                    )
                except Exception as e:
                    logging.error(
                        f"Failed to send fun facts to {subscriber.phone_number}: {str(e)}"
                    )
                    print(
                        f"Failed to send fun facts to {subscriber.phone_number}: {str(e)}"
                    )
            else:
                logging.info(
                    f"Subscriber {subscriber.name} ({subscriber.phone_number}) is not currently subscribed"
                )
                print(
                    f"Subscriber {subscriber.name} ({subscriber.phone_number}) is not currently subscribed"
                )

    else:
        logging.error("Failed to generate fun facts.")
        print("Failed to generate fun facts.")
        logging.info("Fun facts sent!")


def get_all_subscribers() -> List[FunFactsSubscriber]:
    """
    Fetch all subscribers from the Supabase 'Subscriber' table.

    :return: List of FunFactsSubscriber objects
    """
    result = (
        supabase.table("HackathonSubscribers")
        .select("*")
        .filter("fun_facts", "eq", "true")
        .execute()
    )

    subscribers = []
    for row in result.data:
        try:
            # Try parsing the datetime string directly
            created_at = datetime.fromisoformat(row["created_at"])
        except ValueError:
            # If direct parsing fails, remove microseconds and try again
            created_at_str = row["created_at"].split(".")[0]
            created_at = datetime.fromisoformat(created_at_str)

        subscriber = FunFactsSubscriber(
            created_at=created_at,
            phone_number=row["phone_number"],
            name=row["name"],
            is_subscribed=row["fun_facts"],
        )
        subscribers.append(subscriber)

    return subscribers
