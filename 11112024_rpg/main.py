from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, List, Set, Optional, Union
from time import sleep
import anthropic
from anthropic.types.message import Message, ContentBlock
from anthropic.types.message_create_params import MessageParam
from rcs import Pinnacle, Card, Action, SendRcsResponse
from dotenv import load_dotenv
import os
from fastapi import FastAPI, Request
import uvicorn
from pydantic import BaseModel
import json

load_dotenv()  # Load environment variables from .env file


class ItemType(Enum):
    ESSENTIAL = "essential"
    QUEST = "quest"
    COLLECTIBLE = "collectible"


@dataclass
class Item:
    name: str
    description: str
    item_type: ItemType
    can_be_taken: bool = True


@dataclass
class GameAction:
    name: str
    shortcode: str
    description: str


@dataclass
class Mastery:
    coffee: int
    tech_cred: int
    dating_life: int


@dataclass
class Location:
    name: str
    description: str
    items: Dict[str, Item]
    available_actions: List[Action]


KEY: Union[str, None] = os.getenv("PINNACLE_API_KEY")
if not KEY:
    raise ValueError("No key provided")

ANTHROPIC_API_KEY: Union[str, None] = os.getenv("ANTHROPIC_API_KEY")
if not ANTHROPIC_API_KEY:
    raise ValueError("No ANTHROPIC_API_KEY provided")

client = Pinnacle(
    api_key=KEY,
)

TO_NUM = "+16287261512"

# Add this near the top of the file with other global variables
CONVERSATION_HISTORY: List[MessageParam] = []


def start() -> None:
    client.send.rcs(
        from_="test",
        to=TO_NUM,
        cards=[
            Card(
                title="Your alarm clock goes off. You wake up.",
                media_url="https://www.dropbox.com/scl/fi/2qmgffyru7bnj7vcc0u7j/Dream-Alarm-Anytunz-Remix.mp4?rlkey=5h6e7jc1vq0sougfppbghk1hi&st=ehseoi1s&raw=1",
            )
        ],
    )
    client.send.rcs(
        from_="test",
        to=TO_NUM,
        text="Not in the AI-powered utopia the pitch decks promised, but in your 400 sqft San Francisco apartment that costs more than a mansion in Texas.",
    )

    client.send.rcs(
        from_="test",
        to=TO_NUM,
        text="Your Alexa misinterprets your existential sigh as a command to order more oat milk.",
    )

    client.send.rcs(
        from_="test",
        to=TO_NUM,
        media_url="https://www.dropbox.com/scl/fi/7h4k765xidwooknp1967t/Screen-Recording-Nov-11-2024.mp4?rlkey=xhtw48jmgu7sfpzuuhtmm8jwv&st=evr3u4w8&dl=0",
    )

    client.send.rcs(
        from_="test",
        to=TO_NUM,
        cards=[
            Card(
                title="Overpriced Studio Apartment",
                subtitle="""Your MacBook Pro glows ominously in the corner. A dead plant judges you silently.""",
                media_url="https://dnznrvs05pmza.cloudfront.net/4f452f0e-acf1-43dd-aaeb-2761942459f2.mp4?_jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXlIYXNoIjoiNGQyYWExNTIyZmY3NDE2MSIsImJ1Y2tldCI6InJ1bndheS10YXNrLWFydGlmYWN0cyIsInN0YWdlIjoicHJvZCIsImV4cCI6MTczMTU0MjQwMH0.LRHhXD9OWs5krfPbXx-ZFnJlpJINC6n4liYSAbDkQe4&raw=1",
            )
        ],
        quick_replies=[
            Action(title="👀 Look Around", type="trigger", payload="LOOK_AROUND"),
            Action(
                title="🏦 Check Bank Account", type="trigger", payload="CHECK_BANK_ACC"
            ),
            Action(title="🪴 Water Plant", type="trigger", payload="WATER_PLANT"),
            Action(
                title="🏃 Leave apartment", type="trigger", payload="LEAVE_APARTMENT"
            ),
        ],
    )


start()


# def test() -> None:
#     client.send.rcs(
#         from_="test",
#         to=TO_NUM,
#         text="testing",
#         quick_replies=[
#             Action(
#                 title="Talk to the bros",
#                 type="trigger",
#                 payload="TALK_WITH_BROS",
#             )
#         ],
#     )


# test()

anthropic_client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)


def tech_bro_conversation() -> None:
    message: Message = anthropic_client.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=1000,
        temperature=0,
        messages=CONVERSATION_HISTORY,
    )

    textblock: ContentBlock = message.content[0]
    print(textblock)
    if hasattr(textblock, "text"):
        # Parse the text as a dictionary
        response_dict = json.loads(textblock.text)

        # Send each response line separately
        for i, response in enumerate(response_dict["responses"]):
            line = f"{response['name']}: {response['text']}"

            # Only add quick replies on the last message
            if i == len(response_dict["responses"]) - 1:
                quick_replies = [
                    Action(
                        title="Stop talking to them",
                        type="trigger",
                        payload="STOP_TALKING_BROS",
                    )
                ]

                # Add conditional quick replies based on flags
                if response_dict.get("chad_location"):
                    quick_replies.append(
                        Action(
                            title="Go to Sand Hill Capital",
                            type="trigger",
                            payload="GO_TO_SAND_HILL",
                        )
                    )
                if response_dict.get("joins_them"):
                    quick_replies.append(
                        Action(
                            title="Join startup", type="trigger", payload="JOIN_STARTUP"
                        )
                    )
                if response_dict.get("invests"):
                    quick_replies.append(
                        Action(
                            title="Invest in startup",
                            type="trigger",
                            payload="INVEST_STARTUP",
                        )
                    )
                if response_dict.get("bought_product"):
                    quick_replies.append(
                        Action(
                            title="Buy product", type="trigger", payload="BUY_PRODUCT"
                        )
                    )

                client.send.rcs(
                    from_="test", to=TO_NUM, text=line, quick_replies=quick_replies
                )
            else:
                client.send.rcs(from_="test", to=TO_NUM, text=line)

            # Store the conversation history
            CONVERSATION_HISTORY.append(
                {"role": "assistant", "content": [{"type": "text", "text": line}]}
            )
    else:
        client.send.rcs(
            from_="test", to=TO_NUM, text="Whatever dude, we don't have time for this."
        )


# Define the message model
class ActionMessage(BaseModel):
    messageType: str
    actionTitle: str
    payload: Union[str, None] = None
    actionMetadata: Union[str, None] = None


class TextMessage(BaseModel):
    messageType: str
    text: str


app = FastAPI()

# Initialize the global variable at module level
TALKING_ACTIVE: bool = False  # tech bro talk
ITEMS_FOUND: List[str] = []


@app.post("/")
async def webhook(message: Union[ActionMessage, TextMessage]) -> Dict[str, str]:
    # Add global keyword to modify the global variable
    global TALKING_ACTIVE
    global CONVERSATION_HISTORY
    global ITEMS_FOUND

    if isinstance(message, ActionMessage):
        if message.payload == "WATER_PLANT":
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                cards=[
                    Card(
                        title="You water the plant. It doesn't look any happier.",
                        media_url="https://dnznrvs05pmza.cloudfront.net/2d7aa9e2-8094-4e6b-9ff3-fc32a22ed587.mp4?_jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXlIYXNoIjoiMWQwODczYjFkYjQ4OGZhZSIsImJ1Y2tldCI6InJ1bndheS10YXNrLWFydGlmYWN0cyIsInN0YWdlIjoicHJvZCIsImV4cCI6MTczMTU0MjQwMH0.E1_C2y5YJj8yG5IL7BaaBPjj-Fu3RdrHoJYGt8NCLeo&raw=1",
                    )
                ],
                quick_replies=[
                    Action(title="Look around", type="trigger", payload="LOOK_AROUND"),
                    Action(
                        title="Check bank account",
                        type="trigger",
                        payload="CHECK_BANK_ACC",
                    ),
                    Action(
                        title="Leave apartment",
                        type="trigger",
                        payload="LEAVE_APARTMENT",
                    ),
                ],
            )
        if message.payload == "CHECK_BANK_ACC":
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                cards=[
                    Card(
                        media_url="https://dnznrvs05pmza.cloudfront.net/018f769d-f0c5-4810-a5e3-2f0ab5be4554.mp4?_jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXlIYXNoIjoiZDRiOWJiNGYyYzUyYjFjMiIsImJ1Y2tldCI6InJ1bndheS10YXNrLWFydGlmYWN0cyIsInN0YWdlIjoicHJvZCIsImV4cCI6MTczMTU0MjQwMH0.I_tQuoug--Tec-G2FUBZV31c2YVcZqreiW3YwpeUt6I&raw=1",
                        title="You check your bank account balance: $8.42. Perhaps you shouldn't have ordered that $25 avocado toast yesterday.",
                    )
                ],
            )
            if "Existential Dread" not in ITEMS_FOUND:
                ITEMS_FOUND.append("Existential Dread")
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                text="ITEM DISCOVERED: Existential Dread",
                quick_replies=[
                    Action(title="Water plant", type="trigger", payload="WATER_PLANT"),
                    Action(title="Look around", type="trigger", payload="LOOK_AROUND"),
                    Action(
                        title="Leave apartment",
                        type="trigger",
                        payload="LEAVE_APARTMENT",
                    ),
                ],
            )

        if message.payload == "LEAVE_ALLEY":
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                cards=[
                    Card(
                        title="You leave the alley.",
                        media_url="https://dnznrvs05pmza.cloudfront.net/fdee9a19-4ebf-4a73-b1ef-448621161860.mp4?_jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXlIYXNoIjoiMjBlOWRjZmFlMThhODM1YyIsImJ1Y2tldCI6InJ1bndheS10YXNrLWFydGlmYWN0cyIsInN0YWdlIjoicHJvZCIsImV4cCI6MTczMTU0MjQwMH0.Im3Kg9hWcC6lp48_6Fue0MKDCUivMKwuPC6IsqQtNYQ&raw=1",
                    )
                ],
                quick_replies=[
                    Action(
                        title="Follow the tech bros",
                        type="trigger",
                        payload="FOLLOW_TECH_BROS",
                    ),
                    Action(title="Go back to alley", type="trigger", payload="ALLEY"),
                ],
            )

        if message.payload == "ALLEY":
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                cards=[
                    Card(
                        title="Dark Alleyway",
                        media_url="https://dnznrvs05pmza.cloudfront.net/a5c6de9f-6202-45be-8f43-6d3160fbb400.mp4?_jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXlIYXNoIjoiNDljNDIwODZjYjBkOTRjNCIsImJ1Y2tldCI6InJ1bndheS10YXNrLWFydGlmYWN0cyIsInN0YWdlIjoicHJvZCIsImV4cCI6MTczMTU0MjQwMH0.qTTLfuk3eG1pijZT8wN61i4XmBHYzxYW0tgtRmI1Mdk&raw=1",
                    )
                ],
            )
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                text="You're in the alleyway outside your apartment building. Through the smoke of a dumpster fire, you spot a mysterious figure in a black hoodie. They appear to be debugging Python code on a MacBook Pro. Could it be... the mythical 10x engineer?",
                quick_replies=[
                    Action(
                        title="Talk to the man", type="trigger", payload="TALK_WITH_MAN"
                    ),
                    Action(
                        title="Leave the alley", type="trigger", payload="LEAVE_ALLEY"
                    ),
                ],
            )

        if message.payload == "TALK_WITH_MAN":
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                cards=[
                    Card(
                        title="You approach the mysterious figure. They look up at you, their eyes gleaming with the intensity of a thousand suns.",
                        media_url="https://dnznrvs05pmza.cloudfront.net/f0be7a49-bc19-4df8-a3d8-2c1c7420c128.mp4?_jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXlIYXNoIjoiOGM0NDdhNDJjY2M4ZmJmYiIsImJ1Y2tldCI6InJ1bndheS10YXNrLWFydGlmYWN0cyIsInN0YWdlIjoicHJvZCIsImV4cCI6MTczMTU0MjQwMH0.746MNlmsiyCabuaTpOWdzpXWtl-sWO8rrYhn37n0H6A&raw=1",
                    )
                ],
            )

            client.send.rcs(
                from_="test",
                to=TO_NUM,
                text="The mysterious figure silently hands you an OpenAI sticker. You feel your credibility increasing by at least 47.3%. This will look great next to your Rust and Kubernetes stickers on your macbook pro.",
                quick_replies=[
                    Action(
                        title="Thank the man",
                        type="trigger",
                        payload="THANK_THE_MAN",
                    ),
                    Action(
                        title="Reject the stickers",
                        type="trigger",
                        payload="REJECT_STICKERS",
                    ),
                ],
            )

        if message.payload == "THANK_THE_MAN":
            client.send.rcs(
                from_="test", to=TO_NUM, text="ITEM DISCOVERED: OpenAI Sticker"
            )
            if "OpenAI Sticker" not in ITEMS_FOUND:
                ITEMS_FOUND.append("OpenAI Sticker")

            client.send.rcs(
                from_="test",
                to=TO_NUM,
                text="You thank the man with a solemn 'This is the way' while making the Vulcan peace sign. As you leave the alley, you can't help but feel that your GitHub contributions graph will be significantly greener this week.",
                quick_replies=[
                    Action(
                        title="Leave the alley",
                        type="trigger",
                        payload="LEAVE_ALLEY",
                    ),
                ],
            )

        if message.payload == "REJECT_STICKERS":
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                text="You reject the stickers with a firm 'I'm not interested' while making the Vulcan death glare. As you leave the alley, you can't help but feel that your GitHub contributions graph will be significantly redder this week.",
                quick_replies=[
                    Action(
                        title="Leave the alley",
                        type="trigger",
                        payload="LEAVE_ALLEY",
                    ),
                ],
            )

        if message.payload == "LOOK_AROUND":
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                cards=[
                    Card(
                        media_url="https://dnznrvs05pmza.cloudfront.net/1ffd92a6-b02c-41a0-8f2f-c53671d4a6aa.mp4?_jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXlIYXNoIjoiZmZlOWFlYzYwMDNmZmQwNyIsImJ1Y2tldCI6InJ1bndheS10YXNrLWFydGlmYWN0cyIsInN0YWdlIjoicHJvZCIsImV4cCI6MTczMTU0MjQwMH0.arTTnoxBvuNBTR9k1NFDZfmBBv6YyqP3pXeZsMv7iXs&raw=1",
                        title="Your studio apartment is a masterclass in expensive minimalism. The dead plant continues its silent judgment.",
                    )
                ],
                quick_replies=[
                    Action(title="Water plant", type="trigger", payload="WATER_PLANT"),
                    Action(
                        title="Check bank account",
                        type="trigger",
                        payload="CHECK_BANK_ACC",
                    ),
                    Action(
                        title="Leave apartment",
                        type="trigger",
                        payload="LEAVE_APARTMENT",
                    ),
                ],
            )

        if message.payload == "LEAVE_APARTMENT":
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                cards=[
                    Card(
                        media_url="https://dnznrvs05pmza.cloudfront.net/17bd4d52-010a-4cb5-a12d-c2e73dc4781b.mp4?_jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXlIYXNoIjoiY2ZhZDU1Yjc5YjYzMmIzNSIsImJ1Y2tldCI6InJ1bndheS10YXNrLWFydGlmYWN0cyIsInN0YWdlIjoicHJvZCIsImV4cCI6MTczMTU0MjQwMH0.CiMOJX8Ln6HXkc5KMwREqYW2XFX0DsGUfY5RaFc66VQ&raw=1",
                        title="The sun burns - your circadian rhythm has been optimized for 'GitHub dark mode' for the past three sprints.",
                        subtitle="Two tech bros mistake your pained hiss at the sun for a new meditation technique and immediately start a wellness startup around it.",
                    )
                ],
                quick_replies=[
                    Action(title="Go to the alley", type="trigger", payload="ALLEY"),
                    Action(
                        title="Follow the tech bros",
                        type="trigger",
                        payload="FOLLOW_TECH_BROS",
                    ),
                ],
            )

        if message.payload == "ASSHOLE":
            print("PLay music")
            res: SendRcsResponse = client.send.rcs(
                from_="test",
                to=TO_NUM,
                cards=[
                    Card(
                        media_url="https://www.dropbox.com/scl/fi/jo64xb389jet1iqd1p90o/AssHole-Music-Video-by-Mike-Sherm.mp4?rlkey=23mwtvydtr7mmbam0osif2esz&st=w7vrsqs2&raw=1",
                        title='Now playing "ASSHOLE" by Mike Sherm',
                    )
                ],
                quick_replies=[
                    Action(
                        title="Trap",
                        type="trigger",
                        payload="OVERSEAS",
                    ),
                    Action(
                        title="Edm",
                        type="trigger",
                        payload="ATMOSPHERE",
                    ),
                ],
            )
            print(res.message)

        if message.payload == "OVERSEAS":
            print("Play music")
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                cards=[
                    Card(
                        media_url="https://www.dropbox.com/scl/fi/k9lbdveh38sahn7cebee7/ken.mp4?rlkey=my5mt2zhlozho3e5ryb9kgm2i&st=rhu7p4ji&raw=1",
                        title='Now playing "Overseas" by Ken Carson',
                    )
                ],
                quick_replies=[
                    Action(title="Rap", type="trigger", payload="ASSHOLE"),
                    Action(
                        title="Edm",
                        type="trigger",
                        payload="ATMOSPHERE",
                    ),
                ],
            )

        if message.payload == "ATMOSPHERE":
            print("Play music")
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                cards=[
                    Card(
                        media_url="https://www.dropbox.com/scl/fi/1sv31dqs2ugqzqf6t7u1k/Fisher-x-Kita-Alexander-Atmosphere-Lyric-Video.mp4?rlkey=i515rv6pf2q8kauo87ksxs9tn&st=2k6zy8xt&raw=1",
                        title='Now playing "Atmosphere" by Fisher',
                    )
                ],
                quick_replies=[
                    Action(
                        title="Eavesdrop on bros",
                        type="trigger",
                        payload="EAVESDROP_TECH_BROS",
                    ),
                    # Action(
                    #     title="Rage",
                    #     type="trigger",
                    #     payload="OVERSEAS",
                    # ),
                ],
            )

        if message.payload == "FOLLOW_TECH_BROS":
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                cards=[
                    Card(
                        media_url="https://i.ibb.co/cx0s07Q/DALL-E-Pixel-Art-Scene.webp",
                        title="You start to follow the tech bros to their favorite 'authentic third-wave coffee experience'",
                        subtitle="It's just a Starbucks where they've renamed all the sizes to programming terms. A Venti is now called a 'Runtime Exception'.",
                    )
                ],
                quick_replies=[
                    Action(
                        title="Eavesdrop", type="trigger", payload="EAVESDROP_TECH_BROS"
                    ),
                    Action(
                        title="Put in airpods", type="trigger", payload="ATMOSPHERE"
                    ),
                ],
            )

        if message.payload == "EAVESDROP_TECH_BROS":
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                cards=[
                    Card(
                        media_url="https://i.ibb.co/cx0s07Q/DALL-E-Pixel-Art-Scene.webp",
                        title="You start listening in",
                    )
                ],
            )

            client.send.rcs(
                from_="test",
                to=TO_NUM,
                text="Oh yeah dude, they're disrupting the disruptive disruption space",
            )
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                text="Their Series A was like $50 million - all in dogecoin obviously. So based.",
            )
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                text="Bro we should totally build a Web4 dApp that uses machine learning to optimize your morning affirmations.",
            )
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                text="I would kill for a term sheet from Chad Brosephson at Sand Hill Capital...",
            )

            client.send.rcs(
                from_="test",
                to=TO_NUM,
                cards=[
                    Card(
                        title="They're going into OxCAFE. I should ask them if they know where chad is at.",
                        media_url="https://i.ibb.co/Ttd49YG/DALL-E-Coffee-Shop-Pixel-Art-Nov-11-2024.webp",
                        subtitle="You wonder what they'd be doing here.",
                    )
                ],
                quick_replies=[
                    Action(
                        title="Talk to the bros",
                        type="trigger",
                        payload="TALK_WITH_BROS",
                    )
                ],
            )

        if message.payload == "TALK_WITH_BROS":
            TALKING_ACTIVE = True
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                cards=[
                    Card(
                        title="What do you want? Can't you see we're busy?",
                        media_url="https://i.ibb.co/Rp55LDg/DALL-E-Coffee-Shop-Scene.webp",
                    )
                ],
            )
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                text="Hmmm...maybe these guys know something about Chad from Sand Hill Capital... I've been stalking his LinkedIn for months. I bet they're just trying to get close to him. I should ask them about him. If only I could get a term sheet from him...",
            )

        if message.payload == "STOP_TALKING_BROS":
            TALKING_ACTIVE = False
            client.send.rcs(from_="test", to=TO_NUM, text="Hmmm...")

            client.send.rcs(
                from_="test",
                to=TO_NUM,
                cards=[
                    Card(
                        title="Catch you later dude",
                        media_url="https://i.ibb.co/Rp55LDg/DALL-E-Coffee-Shop-Scene.webp",
                    )
                ],
                quick_replies=[
                    Action(
                        title="Talk with them",
                        type="trigger",
                        payload="TALK_WITH_BROS",
                    )
                ],
            )

        if message.payload == "ENTER_SAND_HILL":
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                cards=[
                    Card(
                        title="You enter the building. You can feel the energy of Silicon Valley vibrating through the air.",
                        media_url="https://dnznrvs05pmza.cloudfront.net/392c04e5-be1e-468a-88b3-97ad27dc054e.mp4?_jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXlIYXNoIjoiYWU3ODY4MjA2ZGUxMjJiYSIsImJ1Y2tldCI6InJ1bndheS10YXNrLWFydGlmYWN0cyIsInN0YWdlIjoicHJvZCIsImV4cCI6MTczMTU0MjQwMH0.bgwPWtyewn1zAfi9oa4GdIP8A-Z2N9HAYZBATeMN7eY&raw=1",
                    )
                ],
                quick_replies=[
                    Action(
                        title="Where's Chad?",
                        type="trigger",
                        payload="ASK_RECEPTIONIST",
                    ),
                ],
            )

        if message.payload == "ASK_RECEPTIONIST":
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                cards=[
                    Card(
                        title="You ask the receptionist where Chad is. She looks at you like you're an idiot",
                        media_url="https://dnznrvs05pmza.cloudfront.net/480bd913-77eb-4347-82a2-1cfd7cce84d6.mp4?_jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXlIYXNoIjoiYTA0NDVhMTNlZTJmNWI3ZCIsImJ1Y2tldCI6InJ1bndheS10YXNrLWFydGlmYWN0cyIsInN0YWdlIjoicHJvZCIsImV4cCI6MTczMTU0MjQwMH0.RMv8HKHEVMOsuEb9gpJQ_5MV7IdBKUt2aLe_0jMmCSc&raw=1",
                    )
                ],
                quick_replies=[
                    Action(title="He's my uncle", type="trigger", payload="UNCLE_LINE"),
                ],
            )

        if message.payload == "UNCLE_LINE":
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                cards=[
                    Card(
                        title="'He's my uncle,' you say. The receptionist raises an eyebrow, clearly not buying it.",
                        subtitle="'Sure, and I'm Elon Musk's personal barista.'",
                        media_url="https://dnznrvs05pmza.cloudfront.net/480bd913-77eb-4347-82a2-1cfd7cce84d6.mp4?_jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXlIYXNoIjoiYTA0NDVhMTNlZTJmNWI3ZCIsImJ1Y2tldCI6InJ1bndheS10YXNrLWFydGlmYWN0cyIsInN0YWdlIjoicHJvZCIsImV4cCI6MTczMTU0MjQwMH0.RMv8HKHEVMOsuEb9gpJQ_5MV7IdBKUt2aLe_0jMmCSc&raw=1",
                    )
                ],
                quick_replies=[
                    Action(title="I have proof", type="trigger", payload="HAVE_PROOF"),
                    Action(
                        title="Ok, he's not but please",
                        type="trigger",
                        payload="BEG_LINE",
                    ),
                ],
            )

        if message.payload == "HAVE_PROOF":
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                cards=[
                    Card(
                        title="You show them your LinkedIn profile with Chad in the background at a Sand Hill Capital event",
                        subtitle="The receptionist doesn't buy it...",
                        media_url="https://dnznrvs05pmza.cloudfront.net/7b62d4da-b62a-4e83-adf4-2b196c524a8e.mp4?_jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXlIYXNoIjoiYjczMzYzOGZjNWU5MzFmYSIsImJ1Y2tldCI6InJ1bndheS10YXNrLWFydGlmYWN0cyIsInN0YWdlIjoicHJvZCIsImV4cCI6MTczMTU0MjQwMH0.G1QvGPekKXcYbGB41XrJSuXNHZN30tCZICag1ZlR-1E&raw=1",
                    )
                ],
            )

            client.send.rcs(
                from_="test",
                to=TO_NUM,
                text="GAME OVER: You failed! No funding was received.",
            )

        if message.payload == "BEG_LINE":
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                text="You beg the receptionist to let you in. 'Fine, but don't say I didn't warn you.'",
                quick_replies=[
                    Action(title="See Chad", type="trigger", payload="SEE_CHAD"),
                ],
            )

        if message.payload == "SEE_CHAD":
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                cards=[
                    Card(
                        title="Chad's Office",
                        subtitle="He's doing one-handed pushups while dictating an email about synergistic blockchain paradigms to his AI assistant.'",
                        media_url="https://dnznrvs05pmza.cloudfront.net/8f67e823-15fa-45c4-9ef1-24800af90fc6.mp4?_jwt=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJrZXlIYXNoIjoiNDliMGZmMzQwY2I4ZGZmZiIsImJ1Y2tldCI6InJ1bndheS10YXNrLWFydGlmYWN0cyIsInN0YWdlIjoicHJvZCIsImV4cCI6MTczMTU0MjQwMH0.gOrakPtzvWVXva1YvDZURLoW7IamrykmtmID8YNiIE0&raw=1",
                    )
                ],
                quick_replies=[
                    Action(
                        title="Ask for a term sheet",
                        type="trigger",
                        payload="ASK_FOR_TERM_SHEET",
                    ),
                    Action(
                        title="Ask what that robot is",
                        type="trigger",
                        payload="ASK_ABOUT_ROBOT",
                    ),
                ],
            )

        if message.payload == "ASK_FOR_TERM_SHEET":
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                text="You ask for a term sheet. Chad laughs and kicks you out of his office.",
            )
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                text="GAME OVER: You failed! No funding was received.",
            )

        if message.payload == "TOO_MUCH":
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                text="You can't handle the grind. GAME OVER: You failed! No funding was received.",
            )

        if message.payload == "ASK_ABOUT_ROBOT":
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                text='"Oh, that\'s just my AI trading bot. It\'s made me billions in crypto by analyzing Twitter sentiment and lunar cycles," Chad explains while doing one-handed clapping pushups. "Also makes a killer cold brew."',
                quick_replies=[
                    Action(
                        title="Ask for a term sheet",
                        type="trigger",
                        payload="ASK_FOR_TERM_SHEET",
                    ),
                    Action(
                        title="Ask about his life", type="trigger", payload="CHAD_LIFE"
                    ),
                ],
            )

        if message.payload == "CHAD_LIFE":
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                text="Chad laughs. 'I'm a simple man. I like to code and make money.'",
            )
            sleep(1)  # Add small delay between messages
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                text="'Started coding when I was 2 years old. Built my first unicorn by 5. Now I just invest in visionaries who understand the quantum blockchain metaverse paradigm.'",
            )
            sleep(1)
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                text="'I think it's my morning routine.Wake up at 2AM. Cold plunge in liquid nitrogen. Meditate while running ultramarathons. Then I start my actual workout.'",
            )
            sleep(1)
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                text="'You know what separates the unicorns from the ponies? It's all about the grindset. Are you ready to disrupt the disruption?'",
                quick_replies=[
                    Action(
                        title="I'm ready", type="trigger", payload="READY_FOR_GRIND"
                    ),
                    Action(
                        title="This is too much", type="trigger", payload="TOO_MUCH"
                    ),
                ],
            )

        if message.payload == "READY_FOR_GRIND":
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                text="If you're ready to grind, I think I can get you a term sheet. You just need to check out this one thing...",
                quick_replies=[
                    Action(
                        title="Check it out", type="trigger", payload="CHECK_IT_OUT"
                    ),
                ],
            )

        if message.payload == "CHECK_IT_OUT":
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                text="'It's called Pinnacle RCS, bro. *takes aggressive sip of mushroom coffee* This is what separates the 10x developers from the code monkeys. Rich cards, quick replies, user interactions - it's like the Tesla of messaging APIs. I actually pitched this exact idea to Elon in his sensory deprivation tank last week. He said it was too disruptive even for him. *does one-handed handstand while typing on MacBook Pro with nose*'",
                quick_replies=[
                    Action(
                        title="Try pinnacle",
                        type="openUrl",
                        payload="https://www.trypinnacle.app",
                    ),
                    Action(title="Thank Chad", type="trigger", payload="WIN"),
                ],
            )

        if message.payload == "WIN":
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                text="GAME OVER: You won! Funding was received.",
            )
            if len(ITEMS_FOUND) > 0:
                client.send.rcs(
                    from_="test",
                    to=TO_NUM,
                    text="Here are all the items you've collected:",
                )
                # Create a list of cards for all collected items
                item_cards = []
                for item in ITEMS_FOUND:
                    if item == "Existential Dread":
                        item_cards.append(
                            Card(
                                title="Existential Dread",
                                subtitle="A constant companion in the tech industry. Pairs well with cold brew and equity packages.",
                                media_url="https://i.pinimg.com/originals/7d/90/9d/7d909d18f584085b507457c4fd0bc94d.jpg",
                            )
                        )
                    if item == "OpenAI Sticker":
                        item_cards.append(
                            Card(
                                title="OpenAI Sticker",
                                subtitle="A sacred artifact that grants +10 to credibility when placed on a MacBook Pro.",
                                media_url="https://ih1.redbubble.net/image.4794079437.9113/st,small,507x507-pad,600x600,f8f8f8.jpg",
                            )
                        )
                    if item == "Quantum Chakra Alignment Wallet":
                        item_cards.append(
                            Card(
                                title="Quantum Chakra Alignment Wallet",
                                subtitle="Stores both your crypto and spiritual energy. Warning: May cause temporal paradoxes.",
                                media_url="https://www.blessthisstuff.com/imagens/listagem/2021/grande/grande_corazon-crypto-hardware-wallet.jpg",
                            )
                        )
                    if item == "Web3 NFT":
                        item_cards.append(
                            Card(
                                title="Web3 Mindfulness Warrior NFT",
                                subtitle="Proof that you invested your life savings ($8.42) into a startup. Currently worth 0.0000001 ETH.",
                                media_url="https://nftcalendar.io/storage/uploads/2022/05/01/ezgif_com-gif-maker__6__05012022202208626eebf05fb82.gif",
                            )
                        )
                    if item == "Quantum Mindfulness Plus Pro Max":
                        item_cards.append(
                            Card(
                                title="Quantum Mindfulness Plus Pro Max",
                                subtitle="A subscription service that burns your money faster than a Silicon Valley startup. Features unknown.",
                                media_url="https://cdn.openart.ai/published/1TSpitnPUSquFfX8EdYH/pz5uNB68_mt8q_1024.webp",
                            )
                        )

                # Send all cards in a single request if there are any items
                if item_cards:
                    client.send.rcs(from_="test", to=TO_NUM, cards=item_cards)
            else:
                client.send.rcs(
                    from_="test",
                    to=TO_NUM,
                    text="You didn't collect any items along the way, though.",
                )

        if message.payload == "GO_TO_SAND_HILL":
            TALKING_ACTIVE = False
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                cards=[
                    Card(
                        title="Sand Hill Capital - Menlo Park",
                        subtitle="The gleaming temple of venture capital rises before you. You can taste the liquidity.",
                        media_url="https://i.ibb.co/smc4sH6/DALL-E-Sand-Hill-Road-Pixel-Art.webp",
                    )
                ],
                quick_replies=[
                    Action(
                        title="Enter building",
                        type="trigger",
                        payload="ENTER_SAND_HILL",
                    ),
                ],
            )

        if message.payload == "JOIN_STARTUP":
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                text="You've joined the startup as CFO (Chief Feng-Shui Officer). Your equity package is 0.0001% with a 4-year cliff and an 84-year vesting schedule. They've given you a 'Quantum Chakra Alignment Wallet' that supposedly stores both your crypto and your spiritual energy.",
            )
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                text="ITEM UNLOCKED: QUANTUM CHAKRA ALIGNMENT WALLET",
            )
            if "Quantum Chakra Alignment Wallet" not in ITEMS_FOUND:
                ITEMS_FOUND.append("Quantum Chakra Alignment Wallet")

        if message.payload == "INVEST_STARTUP":
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                text="You invest your life savings ($8.42) into their startup. They give you a 'Web3 Mindfulness Warrior' NFT as proof of investment.",
            )
            if "Web3 NFT" not in ITEMS_FOUND:
                ITEMS_FOUND.append("Web3 NFT")
                client.send.rcs(
                    from_="test",
                    to=TO_NUM,
                    text="ITEM DISCOVERED: Web3 Mindfulness Warrior NFT",
                    quick_replies=[
                        Action(
                            title="Back to bros",
                            type="trigger",
                            payload="TALK_WITH_BROS",
                        ),
                        Action(title="Leave", type="trigger", payload="LEAVE_CAFE"),
                    ],
                )
            if "Web3 Mindfulness Warrior NFT" not in ITEMS_FOUND:
                ITEMS_FOUND.append("Web3 Mindfulness Warrior NFT")

        if message.payload == "BUY_PRODUCT":
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                text="You are now a proud subscriber to their 'Quantum Mindfulness Plus Pro Max' package. Your credit card will be charged $99/month (perhaps more) for access to AI-powered affirmations and blockchain-validated meditation sessions.",
            )
            client.send.rcs(
                from_="test",
                to=TO_NUM,
                text="ITEM UNLOCKED: Quantum Mindfulness Plus Pro Max",
            )
            if "Quantum Mindfulness Plus Pro Max" not in ITEMS_FOUND:
                ITEMS_FOUND.append("Quantum Mindfulness Plus Pro Max")

            client.send.rcs(
                from_="test",
                to=TO_NUM,
                text="Your credit card statement weeps silently. You still don't know what a 'Quantum Mindfulness Plus Pro Max' is",
            )

    if isinstance(message, TextMessage):
        if TALKING_ACTIVE is True:
            client.send.rcs(
                from_="test", to=TO_NUM, text="Michael and Justin are thinking..."
            )
            if message.messageType == "text" and TALKING_ACTIVE is True:
                print(CONVERSATION_HISTORY)
                if len(CONVERSATION_HISTORY) == 0:
                    CONVERSATION_HISTORY.append(
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": f"""You are tasked with roleplaying as two San Francisco tech bros named Michael and Justin. They will be having a conversation with a user who is trying to ask them about their startup. Here's the context and background information:

Background:
Michael and Justin started their startup based on a misunderstanding. They overheard the user complaining about sunburn due to being pale from coding all day, saying: "The sun burns - your circadian rhythm has been optimized for 'GitHub dark mode' for the past three sprints." They mistook this the user's pain for a new meditation technique and immediately started a wellness startup around it. They are unaware that the user overheard them.

Recent conversation between Michael and Justin:
"Oh yeah dude, they're disrupting the disruptive disruption space. Their Series A was like $50 million - all in dogecoin obviously. So based. Bro we should totally build a Web4 dApp that uses machine learning to optimize your morning affirmations. Probably would've helped that one guy (the user). I would kill for a term sheet from Chad Brosephson at Sand Hill Capital..."

Here is the user's question:
<user_question>
{message.text}
</user_question>

Your task is to respond to the user's question as Michael and Justin would. Follow these guidelines:

1. Be satirical and annoying to the user.
2. Only mention small facts about Chad Brosephson's lifestyle if directly asked about him or Sand Hill Capital. If asked about Chad's location, make sure to provide this specific location and room (e.g., Chad's probably crushing it in the Redwood Conference Room at Sand Hill Capital's Menlo Park office).
3. Always try to steer the conversation back to one of these three topics:
   a. Getting the user to come work for their startup
   b. Getting the user as a customer
   c. Talking about dogecoin
4. Use tech bro lingo and buzzwords.
5. Have Michael and Justin interrupt each other and finish each other's sentences.
6. Say they think Chad Brosephson is in the Redwood Conference Room at Sand Hill Capital's Menlo Park office only after persistence from the user.
7. No emojis.

Then, provide the response as a dialogue between Michael and Justin, with each line starting with either "Michael:" or "Justin:". Include at least 2 exchanges between them, but no more than 4. Do not use emojis.

Format your final response as a Python dictionary with the following structure:

{{
  "responses": [
    {{"name": "Michael", "text": "..."}},
    {{"name": "Justin", "text": "..."}},
    ...
  ],
  "chad_location": false,
  "joins_them": false,
  "invests": false,
  "bought_product": false
}}

The "responses" list should contain at least 4 entries, alternating between Michael and Justin.

Set the following flags to true if the conditions are met in the conversation:
- "chad_location": if the user learns Chad's specific location
- "joins_them": if the user ends up agreeing to work for them
- "invests": if the user agrees to invest in their startup
- "bought_product": if the user agrees to buy their product

Keep the conversation flowing naturally while trying to achieve these outcomes. Don't force them if they don't fit the context of the user's question and the natural flow of the conversation.""",
                                }
                            ],
                        }
                    )
                CONVERSATION_HISTORY.append(
                    {
                        "role": "user",
                        "content": [{"type": "text", "text": message.text}],
                    }
                )
                tech_bro_conversation()

    return {"status": "success"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
