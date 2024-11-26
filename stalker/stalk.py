from rcs_types import RCSMessage, Action, Card
from typing import List
from openai import OpenAI
from exa_py import Exa
import os
import requests


def valdiate_citations(citations: List[str]) -> List[str]:
    valid_citations = []
    for citation in citations:
        try:
            response = requests.head(citation, allow_redirects=True)
            if response.status_code == 200:
                valid_citations.append(citation)
        except requests.RequestException:
            continue

    return valid_citations


def stalk(query: str) -> RCSMessage:
    client = OpenAI(
        api_key=os.environ["PPLX_API_KEY"], base_url="https://api.perplexity.ai"
    )

    # chat completion without streaming
    pplx_response = client.chat.completions.create(
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

    citations: List[str] = pplx_response.citations  # type: ignore

    citations = valdiate_citations(citations)

    return {
        "text": pplx_response.choices[0].message.content,
        "quick_replies": [
            Action(title=f"Source {index + 1}", type="openUrl", payload=sourceUrl)
            for index, sourceUrl in enumerate(citations)
        ],
    }


def stalk_category(query: str, category: str) -> RCSMessage:
    exa = Exa(os.environ["EXA_API_KEY"])

    # chat completion without streaming
    response = exa.search_and_contents(
        query=query,
        use_autoprompt=True,
        type="auto",
        category=category,
        num_results=5,
        text={"include_html_tags": False, "max_characters": 100},
    )

    results = response.results

    if len(results) == 0:
        return {
            "text": "Sorry, I didn't find anything. Is there anyone else I can find for you?",
        }
    else:
        return {
            "cards": [
                Card(
                    title=result.title or "",
                    subtitle=result.text or "",
                    buttons=[
                        Action(title="Read More", type="openUrl", payload=result.url)
                    ],
                )
                for result in results
            ],
        }
