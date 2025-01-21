import openai
from datetime import datetime
from typing import Optional
from database import Notes, get_download_url
import json


def get_date(date_str: str) -> Optional[str]:
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"Given that today is {datetime.now().strftime('%Y-%m-%d')}, use the user's message to determine the date. Return the date in YYYY-MM-DD format. Otherwise return 'unknown'. Return in JSON format with the key 'date'.",
            },
            {"role": "user", "content": date_str},
        ],
        temperature=0,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "date_schema",
                "description": "The date in 'YYYY-MM-DD' format",
                "schema": {
                    "type": "object",
                    "properties": {
                        "date": {
                            "type": "string",
                            "description": "The date in 'YYYY-MM-DD' format",
                        },
                    },
                    "additionalProperties": False,
                },
            },
        },
    )

    if response.choices[0].message.content:
        date_str = json.loads(response.choices[0].message.content)["date"]
        if date_str == "unknown":
            return None

        else:
            try:
                datetime.strptime(date_str, "%Y-%m-%d")
                return date_str
            except ValueError:
                return None
    else:
        return None


def get_chat_messages(notes: Notes):
    user_notes = {
        "role": "user",
        "content": [
            {
                "type": "text",
                "text": f"Here are my notes for {notes.createdAt}:\n\n",
            },
        ],
    }
    for note in notes.notes:
        if note["contentType"] == "text":
            user_notes["content"].append(
                {
                    "type": "text",
                    "text": note["content"],
                }
            )
        elif note["contentType"] == "image":
            user_notes["content"].append(
                {
                    "type": "image_url",
                    "image_url": {
                        "url": get_download_url(note["content"]),
                    },
                }
            )
    return user_notes


def summarize_notes(notes: Notes) -> Optional[str]:
    response = openai.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": f"Given that today is {datetime.now().strftime('%Y-%m-%d')} and the user's notes, summarize the user's notes and the user's day. These notes will include both text and image links. Make the summary personal, interesting, thoughtful, and positive. Return the summary in JSON format with the key 'summary'.",
            },
            get_chat_messages(notes),  # type: ignore
        ],
        temperature=0,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "summary_schema",
                "description": "The summary of the user's notes",
                "schema": {
                    "type": "object",
                    "properties": {
                        "summary": {
                            "type": "string",
                            "description": "The summary of the user's notes",
                        },
                    },
                    "additionalProperties": False,
                },
            },
        },
    )

    if response.choices[0].message.content:
        return json.loads(response.choices[0].message.content)["summary"]
    else:
        return None
