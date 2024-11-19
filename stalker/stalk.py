from rcs_types import RCSMessage, Action
from typing import List
from openai import OpenAI
import os


def stalk(query: str) -> RCSMessage:
    client = OpenAI(
        api_key=os.environ["PPLX_API_KEY"], base_url="https://api.perplexity.ai"
    )

    # chat completion without streaming
    response = client.chat.completions.create(
        model="llama-3.1-sonar-large-128k-online",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an artificial intelligence assistant. Your task is to find and note interesting, noteworthy, and nice details about a person based on their online presence."
                    "You should gather information from various sources such as social media profiles, public records, and other online platforms. Ensure that the information is accurate, respectful, and presented in a positive manner."
                    "Make it as detailed as possible and specific as possible."
                    "Avoid any content that could be considered invasive or inappropriate."
                    "Find the following person:"
                ),
            },
            {"role": "user", "content": query},
        ],
    )

    citations: List[str] = response.citations  # type: ignore

    return {
        "text": response.choices[0].message.content,
        "quick_replies": [
            Action(title=f"Source {index + 1}", type="openUrl", payload=sourceUrl)
            for index, sourceUrl in enumerate(citations)
        ],
    }
