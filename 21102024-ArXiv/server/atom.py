import feedparser
from datetime import datetime, timedelta
from dataclasses import dataclass
from typing import Optional, List
from supabase import create_client, Client
from dotenv import load_dotenv
from mendeley import Mendeley
import os
import logging
import schedule
import time
from rcs import Pinnacle

load_dotenv()

client = Pinnacle(
    api_key=os.getenv("PINNACLE_API_KEY"),
)

@dataclass
class ArxivPaper:
    arxiv_id: str
    title: str
    updated: datetime
    abstract_link: str
    summary: str
    categories: list[str]
    published: datetime
    announce_type: str
    rights: str
    journal_reference: Optional[str]
    doi: Optional[str]
    creators: str
    views: int = 0

@dataclass
class ArxivSubscriber:
    created_at: datetime
    phone_number: str
    name: str
    is_subscribed: bool

def sendPapers(to: str, papers: List[ArxivPaper]):
    cards = []
    for paper in papers:
        card = {
            "title": paper.title,
            "subtitle": f"{paper.creators}\n\n{paper.summary[:200]}...",
        }
        cards.append(card)

    try:
        client.send.rcs(
            from_="test",
            to=to,
            cards=cards,
            quick_replies=[
                {
                    "title": "Opt out",
                    "payload": "OPT_OUT",
                    "type": "trigger"
                }
            ]
        )
        logging.info(f"Successfully sent {len(papers)} papers to {to}")
        print(f"Successfully sent {len(papers)} papers to {to}")
    except Exception as e:
        logging.error(f"Failed to send papers to {to}: {str(e)}")
        print(f"Failed to send papers to {to}: {str(e)}")

# Initialize Supabase client
supabase_url = os.getenv("SUPABASE_URL")
supabase_key = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(supabase_url, supabase_key)

def get_most_recent_paper():
    result = supabase.table('Arxiv').select('updated').order('updated', desc=True).limit(1).execute()
    if result.data:
        updated_str = result.data[0]['updated']
        try:
            # Try parsing the datetime string directly
            return datetime.fromisoformat(updated_str)
        except ValueError:
            # If parsing fails, remove microseconds and try again
            updated_str = updated_str.split('.')[0] + '+00:00'
            return datetime.fromisoformat(updated_str)
    return None

def get_arxiv_papers(category='cs.ai', since=None):
    """
    Fetch arXiv papers from the current RSS feed for a given category.
    
    :param category: arXiv category to fetch papers from (default: 'cs.ai')
    :param since: datetime object to fetch papers updated after this time
    :return: List of ArxivPaper objects
    """
    feed_url = f"https://rss.arxiv.org/atom/{category}"
    
    feed = feedparser.parse(feed_url)
    papers = []
    
    for entry in feed.entries:
        updated = datetime.fromisoformat(entry.updated.replace('Z', '+00:00'))
        if since and updated <= since:
            continue
        
        paper = ArxivPaper(
            arxiv_id=entry.id.split('/')[-1],
            title=entry.title,
            updated=updated,
            abstract_link=next(link.href for link in entry.links if link.rel == 'alternate' and link.type == 'text/html'),
            summary=entry.summary.replace('\n', ' '),
            categories=[tag['term'] for tag in entry.tags],
            published=datetime.fromisoformat(entry.published.replace('Z', '+00:00')),
            announce_type=entry.get('arxiv_announce_type', 'N/A'),
            rights=entry.get('rights', 'N/A'),
            journal_reference=entry.get('arxiv_journal_reference', None),
            doi=entry.get('arxiv_doi', None),
            creators=', '.join(author.name for author in entry.authors),
            views=0  # Initialize views to 0 for new papers
        )
        
        paper.views = get_views(paper.doi) if paper.doi else 0
        
        papers.append(paper)
    
    return papers

def get_most_popular_papers(limit=3) -> List[ArxivPaper]:
    """
    Get the papers with the most views from the most recent day in the Supabase 'Arxiv' table.
    
    :param limit: Number of top papers to retrieve (default: 3)
    :return: List of ArxivPaper objects with the most views, or empty list if no papers found
    """
    # Get the most recent date
    result = supabase.table('Arxiv').select('updated').order('updated', desc=True).limit(1).execute()
    if not result.data:
        return []
    
    # Parse the datetime string, handling potential microsecond precision
    most_recent_date_str = result.data[0]['updated']
    try:
        most_recent_date = datetime.fromisoformat(most_recent_date_str).date()
    except ValueError:
        # If parsing fails, remove microseconds and try again
        most_recent_date_str = most_recent_date_str.split('.')[0] + '+00:00'
        most_recent_date = datetime.fromisoformat(most_recent_date_str).date()
    
    # Query for papers from the most recent date, ordered by views
    result = supabase.table('Arxiv') \
        .select('*') \
        .gte('updated', most_recent_date.isoformat()) \
        .lt('updated', (most_recent_date + timedelta(days=1)).isoformat()) \
        .order('views', desc=True) \
        .limit(limit) \
        .execute()
    
    if not result.data:
        return []
    
    popular_papers = []
    for paper_data in result.data:
        paper = ArxivPaper(
            arxiv_id=paper_data['arxiv_id'],
            title=paper_data['title'],
            updated=datetime.fromisoformat(paper_data['updated']),
            abstract_link=paper_data['abstract_link'],
            summary=paper_data['summary'],
            categories=paper_data['categories'],
            published=datetime.fromisoformat(paper_data['published']),
            announce_type=paper_data['announce_type'],
            rights=paper_data['rights'],
            journal_reference=paper_data['journal_reference'],
            doi=paper_data['doi'],
            creators=paper_data['creators'],
            views=paper_data['views']
        )
        popular_papers.append(paper)
    
    return popular_papers

def save_papers_to_supabase(papers):
    """
    Save ArxivPaper objects to the Supabase 'Arxiv' table using batch insert.
    
    :param papers: List of ArxivPaper objects
    """
    total_papers = len(papers)
    
    # Prepare the batch of papers
    paper_dicts = []
    for paper in papers:
        paper_dict = paper.__dict__.copy()
        
        # Convert datetime objects to ISO format strings
        paper_dict['updated'] = paper_dict['updated'].isoformat()
        paper_dict['published'] = paper_dict['published'].isoformat()
        
        paper_dicts.append(paper_dict)
    
    # Perform batch insert
    result = supabase.table('Arxiv').insert(paper_dicts).execute()
    
    # Check the result
    if result.data:
        saved_count = len(result.data)
        failed_count = total_papers - saved_count
        print(f"Batch insert completed. Saved: {saved_count}, Failed: {failed_count}")
    else:
        print("Batch insert failed. No papers were saved.")
    
    print(f"Final result: {saved_count} papers saved, {failed_count} papers failed to save.")

def check_for_new_papers():
    logging.info("Checking for new papers...")
    print("Checking for new papers...")
    
    # Get papers from the RSS feed
    papers = get_arxiv_papers()
    
    if papers:
        # Get existing paper IDs from the database
        existing_paper_ids = get_existing_paper_ids()
        
        # Filter out papers that are already in the database
        new_papers = [paper for paper in papers if paper.arxiv_id not in existing_paper_ids]
        
        if new_papers:
            print(f"Found {len(new_papers)} new papers.")
            save_papers_to_supabase(new_papers)
            logging.info(f"Saved {len(new_papers)} new papers to Supabase.")
            
            # Get the top 3 most popular papers
            top_papers = get_most_popular_papers(limit=3)
            
            print(f"Top papers {top_papers}")
            
            # Get all subscribers and send them the new papers and top 3 most popular papers
            subscribers = get_all_subscribers()
            for subscriber in subscribers:
                if subscriber.is_subscribed:
                    sendPapers(subscriber.phone_number, top_papers)
                else:
                    logging.info(f"Subscriber {subscriber.name} ({subscriber.phone_number}) is not currently subscribed")
                    print(f"Subscriber {subscriber.name} ({subscriber.phone_number}) is not currently subscribed")
        else:
            print("No new papers found.")
            logging.info("No new papers found.")
    else:
        print("No papers retrieved from RSS feed.")
        logging.info("No papers retrieved from RSS feed.")

def get_all_subscribers() -> List[ArxivSubscriber]:
    """
    Fetch all subscribers from the Supabase 'ArxivSubscribers' table.
    
    :return: List of ArxivSubscriber objects
    """
    result = supabase.table('ArxivSubscribers').select('*').execute()
    
    subscribers = []
    for row in result.data:
        try:
            # Try parsing the datetime string directly
            created_at = datetime.fromisoformat(row['created_at'])
        except ValueError:
            # If direct parsing fails, remove microseconds and try again
            created_at_str = row['created_at'].split('.')[0]
            created_at = datetime.fromisoformat(created_at_str)
        
        subscriber = ArxivSubscriber(
            created_at=created_at,
            phone_number=row['phone_number'],
            name=row['name'],
            is_subscribed=row['is_subscribed']
        )
        subscribers.append(subscriber)
    
    return subscribers

def get_existing_paper_ids():
    """
    Fetch all existing paper IDs from the Supabase 'Arxiv' table.
    
    :return: Set of existing arxiv_id strings
    """
    result = supabase.table('Arxiv').select('arxiv_id').execute()
    return set(row['arxiv_id'] for row in result.data)

def run_scheduler():
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            logging.error(f"An error occurred in the scheduler: {str(e)}")
            print(f"An error occurred in the scheduler: {str(e)}")
            # Reduced sleep time after an error
            time.sleep(10)

class TimedCache:
    def __init__(self, expiration_time):
        self.expiration_time = expiration_time
        self.cached_value = None
        self.last_update_time = None

    def get(self, update_func):
        current_time = datetime.now()
        if self.cached_value is None or self.last_update_time is None or \
           (current_time - self.last_update_time) > self.expiration_time:
            self.cached_value = update_func()
            self.last_update_time = current_time
        return self.cached_value

mendeley_session_cache = TimedCache(timedelta(minutes=30))

def get_mendeley_session():
    def create_session():
        CLIENT_ID = os.getenv('MENDELEY_ID')
        CLIENT_SECRET = os.getenv('MENDELEY_SECRET_KEY')

        print(f"Initializing Mendeley session")
        print(f"Mendeley Client ID: {CLIENT_ID}")
        print(f"Mendeley Client Secret: {CLIENT_SECRET}")

        mendeley = Mendeley(CLIENT_ID, CLIENT_SECRET)
        return mendeley.start_client_credentials_flow().authenticate()

    return mendeley_session_cache.get(create_session)

def get_views(DOI: str) -> int:
    try:
        session = get_mendeley_session()

        print(f"Searching for DOI: {DOI}")

        # Search for the paper using its DOI
        doc = session.catalog.by_identifier(doi=DOI, view='stats')

        if doc:
            print(f"Document found. Reader count: {doc.reader_count}")
            return doc.reader_count
        else:
            print("Document not found")
            return 0
    except Exception as e:
        logging.error(f"Failed to get views for DOI {DOI}: {str(e)}")
        return 0

if __name__ == "__main__":
    # Configure logging
    print("Main run")
    logging.basicConfig(filename='arxiv_paper_updates.log', level=logging.INFO,
                        format='%(asctime)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

    # Schedule the job to run every hour
    schedule.every(15).seconds.do(check_for_new_papers)

    logging.info("Starting ArXiv paper checker.")
    print("ArXiv paper checker started. Press Ctrl+C to stop.")

    # Run the job immediately once
    check_for_new_papers()

    # Run the scheduler
    run_scheduler()
