from datetime import datetime, timedelta, timezone
import os
from dotenv import load_dotenv
import feedparser
from dataclasses import dataclass
from typing import List, Optional
from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse
import asyncio
from contextlib import asynccontextmanager

from rcs import AsyncPinnacle
# Load environment variables
load_dotenv()

# Get the API key from .env
api_key = os.getenv('PINNACLE_API_KEY')

client = AsyncPinnacle(
    api_key=api_key,
)

@dataclass
class ArXivPaper:
    title: str
    link: str
    description: str
    pubDate: str
    guid: str
    categories: List[str]  # Changed from 'category' to 'categories'
    announce_type: str
    creators: List[str]

def is_date_newer(date1: datetime, date2: datetime) -> bool:
    """
    Compare two dates and return True if the first date is newer than the second.
    
    Args:
    date1 (datetime): The first date to compare
    date2 (datetime): The second date to compare
    
    Returns:
    bool: True if date1 is newer than date2, False otherwise
    """
    # Convert both dates to UTC and remove timezone information
    date1_utc = date1.astimezone(timezone.utc).replace(tzinfo=None)
    date2_utc = date2.astimezone(timezone.utc).replace(tzinfo=None)
    
    return date1_utc > date2_utc

async def ai_rss(is_test: bool) -> List[ArXivPaper]:
    link = 'http://export.arxiv.org/rss/cs.ai'
    if is_test:
        link = 'sample_feed.xml'

    feed = feedparser.parse(link)

    print(f"Feed Title: {feed['feed']['title']}")

    papers = []
    for entry in feed.entries:
        # Extract categories
        categories = [tag.term for tag in entry.get('tags', [])]

        # Extract creators (authors)
        creators = entry.get('authors', [])
        if isinstance(creators, str):
            creator_names = [name.strip() for name in creators.split(',')]
        else:
            creator_names = [author.get('name', '').strip() for author in creators]

        paper = ArXivPaper(
            title=entry.get('title', ''),
            link=entry.get('link', ''),
            description=entry.get('summary', ''),
            pubDate=entry.get('published', ''),
            guid=entry.get('id', ''),
            categories=categories,
            announce_type=entry.get('arxiv_announce_type', ''),
            creators=creator_names,
        )
        papers.append(paper)

    # Handle the case when there are no entries
    latest_pub_time = None
    if feed.entries:
        latest_pub_time = feed.entries[0].get('published_parsed')

    return papers, latest_pub_time

@asynccontextmanager
async def lifespan(app: FastAPI):
    asyncio.create_task(update_papers())
    yield

app = FastAPI(lifespan=lifespan)

last_check_time = None
papers_cache = []

async def update_papers():
    from db import upload_papers_to_supabase, get_most_recent_paper_date, get_all_subscribers
    global last_check_time, papers_cache
    while True:
        try:
            current_time = datetime.now()
            new_papers, latest_pub_time = await ai_rss(is_test=False)
            
            if latest_pub_time is None:
                print("No new papers found or error fetching feed")
                subscribers = get_all_subscribers()
                if subscribers:
                  for subscriber in subscribers:
                    await client.send.rcs(
                        from_="test",
                        to=subscriber[1],
                        text="No new AI papers are available on ArXiv! (Latest pub time none)"
                    )
                    await asyncio.sleep(1800)  # Sleep for 30 minutes
                    continue
            
            latest_pub_datetime = datetime(*latest_pub_time[:6])
            most_recent_db_date = get_most_recent_paper_date()  # This function is not async
            if most_recent_db_date is None or is_date_newer(latest_pub_datetime, most_recent_db_date):
                papers_cache = new_papers
                last_check_time = current_time
                uploaded = await upload_papers_to_supabase(new_papers)
                print(f"Upload status: {uploaded}")
                if not uploaded:
                    print("Failed to upload papers")
                else:
                    # Send the most recent paper to all subscribers
                    subscribers = get_all_subscribers()
                    if subscribers and new_papers:
                        most_recent_paper = new_papers[0]
                        for subscriber in subscribers:
                            await client.send.rcs(
                                from_="test",
                                to=subscriber[1],
                                cards=[{
                                    "title": f"{most_recent_paper.title}",
                                    "mediaUrl": "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExdjN2YWEyMGhiam5wZG1xN2xlbnVtZXFlcHdlYWdrcWZlYWtkM2N5cCZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/PymCh9M2X6tm5aZ9rn/giphy.gif",
                                    "subtitle": f"Authors: {', '.join(most_recent_paper.creators)}",
                                    "buttons": [
                                        {
                                            "title": "See paper",
                                            "payload": f"{most_recent_paper.link}",
                                            "type": "openUrl"
                                        },
                                        {
                                            "payload": "https://arxiv.org/",
                                            "type": "openUrl",
                                            "title": "See all papers",
                                        }
                                    ]
                                }]
                            )
            else:
                print("No new data")
                subscribers = get_all_subscribers()
                for subscriber in subscribers:
                    await client.send.rcs(
                        from_="test",
                        to=subscriber[1],
                        text="No new AI papers are available on ArXiv!"
                    )
        except Exception as e:
            print(f"Error updating papers: {str(e)}")
        
        await asyncio.sleep(1800)  # Sleep for 30 minutes

@app.get("/papers")
async def get_papers():
    return JSONResponse(content=[paper.__dict__ for paper in papers_cache])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
