import os
from supabase import create_client, Client
from dotenv import load_dotenv
from dataclasses import dataclass
from datetime import datetime
from typing import List
from arxiv import ArXivPaper

# Load environment variables from .env file
load_dotenv()

# Setup typeshit
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
supabase: Client = create_client(supabase_url=url, supabase_key=key)

@dataclass
class ArxivPaper:
    id: int
    created_at: datetime
    last_time: datetime
    title: str
    description: str
    pubDate: datetime
    guid: str

def fetch_all_papers() -> list[ArxivPaper]:
    try:
        # Query the 'arxiv' table to fetch all papers
        response = supabase.table('Arxiv').select('*').execute()

        # Convert the response data to ArxivPaper objects
        papers = []
        for item in response.data:
            paper = ArxivPaper(
                id=item['id'],
                created_at=datetime.fromisoformat(item['created_at']),
                last_time=datetime.fromisoformat(item['last_time']),
                title=item['title'],
                description=item['description'],
                pubDate=datetime.fromisoformat(item['pubDate']),
                guid=item['guid']
            )
            papers.append(paper)

        print(f"Successfully fetched {len(papers)} papers from Arxiv.")
        return papers

    except Exception as e:
        print(f"Error fetching papers from Arxiv: {e}")
        return []

def get_most_recent_paper_date() -> datetime:
    try:
        # Query the 'arxiv' table to fetch the most recent paper
        response = supabase.table('Arxiv').select('pubDate').order('pubDate', desc=True).limit(1).execute()

        if response.data:
            # Convert the ISO format string to datetime
            most_recent_date = datetime.fromisoformat(response.data[0]['pubDate'])
            print(f"Most recent paper date: {most_recent_date}")
            return most_recent_date
        else:
            print("No papers found in the database.")
            return None

    except Exception as e:
        print(f"Error fetching most recent paper date: {e}")
        return None
    
async def upload_papers_to_supabase(papers: List[ArXivPaper]) -> bool:
    try:
        # Prepare the data for insertion
        data_to_insert = []
        for paper in papers:
            paper_dict = {
                "title": str(paper.title),
                "description": str(paper.description),
                "pubDate": paper.pubDate.isoformat() if isinstance(paper.pubDate, datetime) else str(paper.pubDate),
                "guid": str(paper.guid),
                "categories": paper.categories if hasattr(paper, 'categories') else [],
                "announce_type": str(paper.announce_type) if hasattr(paper, 'announce_type') else None,
                "creators": ", ".join(str(creator) for creator in paper.creators) if hasattr(paper, 'creators') else None,
                "link": str(paper.link) if hasattr(paper, 'link') else None
            }
            data_to_insert.append(paper_dict)

        # Insert the papers into the 'arxiv' table
        response = supabase.table('Arxiv').insert(data_to_insert).execute()

        if response.data:
            print(f"Successfully uploaded {len(response.data)} papers to Supabase.")
            return True
        else:
            print("Failed to upload papers to Supabase.")
            print(f"Error: {response.error}")  # Log the error details
            return False

    except Exception as e:
        print(f"Error uploading papers to Supabase: {e}")
        return False

# User stuff

def register_user(phone_number: str, name: str, is_subscribed: bool) -> bool:
    try:
        # Insert the new user into the 'arxiv' table
        response = supabase.table(table_name='Optin').insert(json={
            "phone_number": phone_number,
            "name": name,
            "is_subscribed": is_subscribed
        }).execute()

        if response.data:
            print(f"User {name} successfully registered!")
            return True
        else:
            print("Failed to register user.")
            return False

    except Exception as e:
        print(f"Error registering user: {e}")
        return False

def is_user_registered(phone_number: str) -> bool:
    try:
        # Query the 'arxiv' table for the given phone number
        response = supabase.table('Optin').select('*').eq('phone_number', phone_number).execute()

        # If any data is returned, the user is registered
        return len(response.data) > 0

    except Exception as e:
        print(f"Error checking user registration: {e}")
        return False

def is_user_subscribed(phone_number: str) -> bool:
    try:
        # Query the 'Optin' table for the given phone number and check if subscribed
        response = supabase.table('Optin').select('is_subscribed').eq('phone_number', phone_number).execute()

        # If any data is returned and is_subscribed is True, the user is subscribed
        return len(response.data) > 0 and response.data[0]['is_subscribed']

    except Exception as e:
        print(f"Error checking user subscription: {e}")
        return False

def update_user_subscription(phone_number: str, is_subscribed: bool) -> bool:
    try:
        # Update the 'Optin' table for the given phone number
        response = supabase.table('Optin').update({"is_subscribed": is_subscribed}).eq('phone_number', phone_number).execute()

        if response.data:
            print(f"User subscription status updated successfully. Is subscribed: {is_subscribed}")
            return True
        else:
            print("Failed to update user subscription status.")
            return False

    except Exception as e:
        print(f"Error updating user subscription: {e}")
        return False

def get_all_subscribers():
    try:
        # Query the 'Optin' table for all subscribed users
        response = supabase.table('Optin').select('name, phone_number').eq('is_subscribed', True).execute()

        if response.data:
            subscribers = [(user['name'], user['phone_number']) for user in response.data]
            return subscribers
        else:
            print("No subscribers found.")
            return []

    except Exception as e:
        print(f"Error fetching subscribers: {e}")
        return []
