import requests
import json
from typing import List, Dict, Optional, Union
import time
from dotenv import load_dotenv
import os
from dataclasses import dataclass, field
from enum import Enum, auto
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv()

# Add Supabase initialization
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("Supabase credentials not found. Please set SUPABASE_URL and SUPABASE_KEY environment variables.")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

class LegislationType(str, Enum):
    HOUSE_BILL = "HR"
    SENATE_BILL = "S"
    HOUSE_JOINT_RESOLUTION = "HJRES"
    SENATE_JOINT_RESOLUTION = "SJRES"
    HOUSE_CONCURRENT_RESOLUTION = "HCONRES"
    SENATE_CONCURRENT_RESOLUTION = "SCONRES"
    HOUSE_RESOLUTION = "HRES"
    SENATE_RESOLUTION = "SRES"

class AmendmentType(str, Enum):
    HOUSE_AMENDMENT = "HAMDT"
    SENATE_AMENDMENT = "SAMDT"
    SENATE_UNPRINTED_AMENDMENT = "SUAMDT" # Only for 97th and 98th Congresses

@dataclass
class LatestAction:
    actionDate: Optional[str] = None
    text: Optional[str] = None
    actionTime: Optional[str] = None

@dataclass
class SponsoredAmendment:
    amendmentNumber: str
    congress: int
    introducedDate: str
    url: str
    latestAction: Optional[Union[LatestAction, None]]
    type: Union[AmendmentType, None]

@dataclass 
class PolicyArea:
    name: Union[str, None] 

@dataclass
class SponsoredLegislation:
    congress: int
    introducedDate: str
    number: int
    policyArea: dict
    title: str
    url: str
    latestAction: Union[LatestAction, None]
    type: Union[LegislationType, None]

@dataclass
class SponsoredLegislationPagination:
    count: int
    next: Optional[str] = None

@dataclass
class SponsoredLegislationRequest:
    bioguideId: str
    contentType: str
    format: str

@dataclass
class SponsoredLegislationResponse:
    pagination: SponsoredLegislationPagination
    request: SponsoredLegislationRequest
    sponsoredLegislation: List[Union[SponsoredLegislation, SponsoredAmendment]]


@dataclass
class MemberPagination:
    count: int
    next: Optional[str]

@dataclass 
class MemberRequest:
    contentType: str
    format: str

@dataclass
class Member:
    bioguideId: str
    name: str
    partyName: str
    state: str
    depiction: dict = field(default_factory=dict)
    terms: dict = field(default_factory=dict)
    updateDate: str = None
    url: str = None
    district: str = None
    sponsored_legislation: Union[SponsoredLegislation, None] = None

    def __str__(self):
        return f"{self.name} ({self.partyName}) - {self.state} - {self.bioguideId}"

    def print_member_info(self):
        print(f"Name: {self.name}")
        print(f"Party: {self.partyName}")
        print(f"State: {self.state}")
        print(f"Bioguide ID: {self.bioguideId}")
        print(f"District: {self.district}")
        print(f"Update Date: {self.updateDate}")
        print(f"Profile URL: {self.url}")
        print(f"Depiction: {self.depiction.get('imageUrl', 'No Image')}")
        print("-" * 40)

class CongressAPI:
    BASE_URL = "https://api.congress.gov/v3"
    
    def __init__(self, api_key: str):
        self.session = requests.Session()
        self.session.headers.update({'X-Api-Key': api_key})
    
    def get_all_members(self) -> List[Member]:
        """Fetch all current congress members, handling pagination."""
        members = []
        NUMBER_OF_MEMBERS_TO_GET = 250 # max is 250
        url = f"{self.BASE_URL}/member?currentMember=True&limit={NUMBER_OF_MEMBERS_TO_GET}"
        
        while url:
            # Make request for current page
            print("url:", url)
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            
            # Add members from current page
            members_data = data['members']
            members.extend([Member(**member) for member in members_data])
            
            # Get next page URL if it exists
            url = data['pagination'].get('next')
            
            # Optional: Add rate limiting between requests
            if url:
                time.sleep(1)  # Wait 1 second between pagination requests
        
        return members
    
    def get_sponsored_legislation(self, bioguide_id: str) -> List[SponsoredLegislation]:
        """Fetch sponsored legislation for a specific member by bioguide ID."""
        result = []
        NUMBER_OF_BILLS_TO_GET = 250  # Increased from 1 to 250 for efficiency
        url = f"{self.BASE_URL}/member/{bioguide_id}/sponsored-legislation?limit={NUMBER_OF_BILLS_TO_GET}"
        
        while url:
            response = self.session.get(url)
            response.raise_for_status()
            response_data = response.json()
            
            try:
                legislation_response = SponsoredLegislationResponse(
                    pagination=SponsoredLegislationPagination(**response_data['pagination']),
                    request=SponsoredLegislationRequest(**response_data['request']),
                    sponsoredLegislation=response_data['sponsoredLegislation']
                )
                
                # Process legislation from current page
                for item in legislation_response.sponsoredLegislation:
                    if 'amendmentNumber' in item:
                        amendment = SponsoredAmendment(
                            amendmentNumber=item['amendmentNumber'],
                            congress=item['congress'],
                            introducedDate=item['introducedDate'],
                            url=item['url'],
                            latestAction=LatestAction(**item['latestAction']) if item['latestAction'] is not None else None,
                            type=AmendmentType(item.get('type')) if item.get('type') is not None else None
                        )
                        result.append(amendment)
                    else:
                        legislation = SponsoredLegislation(
                            congress=item['congress'],
                            introducedDate=item['introducedDate'],
                            number=item['number'],
                            policyArea=item['policyArea'],
                            title=item['title'],
                            type=LegislationType(item.get('type')) if item.get('type') else None,
                            url=item['url'],
                            latestAction=LatestAction(**item['latestAction']) if item['latestAction'] is not None else None
                        )
                        result.append(legislation)
                
                # Get next page URL if it exists
                url = legislation_response.pagination.next
            except Exception as e:
                print("\n\n\nEXCEPTION ________________________", e)
                print("data", response_data, "\n\n\n")
        
        return result
    
    def get_all_members_with_legislation(self) -> List[Member]:
        """Fetch all members and their sponsored legislation with rate limiting."""
        members = self.get_all_members()
        result = []
        
        for member in members:
            try:
                time.sleep(1)  # Rate limiting
                name = member.name
                print(f"***************\nFETCHING legislation for {name} from {member.state}")
                legislation = self.get_sponsored_legislation(member.bioguideId)
                member.sponsored_legislation = legislation
                result.append(member)
                print(f"Fetched legislation for {name}\n*****|||||||")
            except Exception as e:
                print(f"Error fetching legislation for {member.bioguideId}: {str(e)}")
        
        return result

def main():
    api_key = os.getenv('CONGRESS_API_KEY')  # Load API key from environment variable
    if not api_key:
        raise ValueError("API key not found. Please set the API_KEY environment variable.")
    api = CongressAPI(api_key)
    
    # # Fetch all data
    # members = api.get_all_members_with_legislation()
    
    # for member in members:
    #     print("\n\n***===============***")
    #     print(f"{member.name} ({member.partyName}) from {member.state}")
    #     print("***===============***")
        
    #     if member.sponsored_legislation is None:
    #         print("It's none :(")
    #     else:
    #         for legislation in member.sponsored_legislation:
    #             try:
    #                 if isinstance(legislation, SponsoredLegislation):
    #                     print(f"Bill: {f'{legislation.type.value}-' if legislation.type is not None else ''}{legislation.number}")
    #                     print(f"Title: {legislation.title}")
    #                     print(f"Introduced: {legislation.introducedDate}")
    #                     if legislation.latestAction:
    #                         print(f"Latest Action: {legislation.latestAction.text}")
    #                     print("---")
    #                 # elif isinstance(legislation, SponsoredAmendment):
    #                 #     print(f"Amendment: {f'{legislation.type.value}-' if legislation.type is not None else ''}{legislation.amendmentNumber}")
    #                 #     print(f"Introduced: {legislation.introducedDate}")
    #                 #     if legislation.latestAction:
    #                 #         print(f"Latest Action: {legislation.latestAction.text}")
    #                 #     print("---")
    #             except Exception as e:
    #                 print(f"Error processing legislation: {str(e)}")
    #                 print("LEGISLATION: ", legislation)
    # # print("Data collection complete. Results saved to congress_data.json")

    members = api.get_all_members()

    # Get existing members from the database
    try:
        existing_members = supabase.table('CongressMembers').select('bioguideId').execute()
        existing_bioguide_ids = {member['bioguideId'] for member in existing_members.data}
    except Exception as e:
        print(f"Error fetching existing members: {str(e)}")
        existing_bioguide_ids = set()

    # Filter out members that already exist
    new_member_data = [
        {
            'bioguideId': member.bioguideId,
            'name': member.name,
            'partyName': member.partyName,
            'state': member.state,
            'district': member.district,
            'terms': member.terms,
            'updateDate': member.updateDate,
            'url': member.url,
            'depiction': member.depiction
        }
        for member in members
        if member.bioguideId not in existing_bioguide_ids
    ]

    if not new_member_data:
        print("No new members to add to the database.")
        return

    try:
        # Batch upsert only new members
        result = supabase.table('CongressMembers').upsert(new_member_data).execute()
        print(f"Successfully stored data for {len(new_member_data)} new members, {result}")
    except Exception as e:
        print(f"Error batch storing members: {str(e)}")

if __name__ == "__main__":
    main()
