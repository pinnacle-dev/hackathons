from mendeley import Mendeley
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_views(DOI: str) -> int:
    # Get Mendeley API credentials from environment variables
    CLIENT_ID = os.getenv('MENDELEY_ID')
    CLIENT_SECRET = os.getenv('MENDELEY_SECRET_KEY')

    # Initialize Mendeley client
    mendeley = Mendeley(CLIENT_ID, CLIENT_SECRET)
    session = mendeley.start_client_credentials_flow().authenticate()

    # Search for the paper using its DOI
    doc = session.catalog.by_identifier(doi=DOI, view='stats')

    if doc:
        return doc.reader_count
    else:
        return 0

# Example usage:
views = get_views("10.1145/3637528.3671683")
views = get_views("10.24963/ijcai.2024/386")
print(f"The paper has {views} readers.")
