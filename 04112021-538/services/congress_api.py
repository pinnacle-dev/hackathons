import requests
import time
from typing import List, Union, Optional
from models.member import Member
from models.legislation import (    
    BillResponse,
    BillTextResponse
)
from models.bill import (
    CosponsorResponse,
    BillDetailResponse
)

class CongressAPI:
    BASE_URL: str = "https://api.congress.gov/v3"
    
    def __init__(self, api_key: str) -> None:
        self.session: requests.Session = requests.Session()
        self.session.headers.update({'X-Api-Key': api_key})
    
    def get_all_members(self) -> List[Member]:
        """Fetch all current congress members, handling pagination."""
        members = []
        NUMBER_OF_MEMBERS_TO_GET = 250
        url = f"{self.BASE_URL}/member?currentMember=True&limit={NUMBER_OF_MEMBERS_TO_GET}"
        
        while url:
            print("url:", url)
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            
            members_data = data['members']
            members.extend([Member(**member) for member in members_data])
            
            url = data['pagination'].get('next')
            
            if url:
                time.sleep(1)
        
        return members
    
    def get_bills(self, num_bills: str, congress: str, bill_type: str) -> BillResponse: 
        url = f"{self.BASE_URL}/bill/{congress}/{bill_type.lower()}?limit={num_bills}"
        print("url:", url)
        response = self.session.get(url)
        response.raise_for_status()
        data = response.json()
        return BillResponse(**data)
    
    def get_bill_text(self, congress: str, bill_type: str, bill_number: str) -> Union[str, None]:
        """
        Retrieves the full text of a bill using its congress, type, and number.
        Returns the bill text as a string, or None if unavailable.
        """
        try:
            url = f"{self.BASE_URL}/bill/{congress}/{bill_type.lower()}/{bill_number}/text"
            print("\nurl:", url, "\n")
            response = self.session.get(url)
            response.raise_for_status()
            data = response.json()
            text_data = BillTextResponse(**data)

            # Find the URL for the Formatted XML version
            xml_url = next(
                (format.url for version in text_data.textVersions 
                 for format in version.formats if format.type == "Formatted XML"),
                None
            )

            if xml_url:
                # Fetch and parse the XML content
                response = self.session.get(xml_url)
                response.raise_for_status()
                
                # Parse XML with BeautifulSoup using lxml parser
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(response.content, 'lxml-xml')
                
                # Extract all text content, removing XML tags
                return soup.get_text(separator=' ', strip=True)
                
            return None
            
        except requests.RequestException as e:
            print(f"Error fetching bill text: {e}")
            return None
        except Exception as e:
            print(f"Error processing bill text: {e}")
            return None
    
    def get_bill_cosponsors(self, congress: str, bill_type: str, bill_number: str) -> CosponsorResponse:
        """
        Retrieves the cosponsors for a specific bill.
        Returns a CosponsorResponse object containing a list of Cosponsor objects.
        """
        url = f"{self.BASE_URL}/bill/{congress}/{bill_type.lower()}/{bill_number}/cosponsors"
        response = self.session.get(url)
        response.raise_for_status()
        data = response.json()
        return CosponsorResponse(**data)
    
    def get_bill_information(self, congress: str, bill_type: str, bill_number: str) -> BillDetailResponse:
        """
        Retrieves detailed information about a specific bill.
        Returns a BillDetailResponse object containing comprehensive bill details.
        """
        url = f"{self.BASE_URL}/bill/{congress}/{bill_type.lower()}/{bill_number}"
        print("url:", url)
        response = self.session.get(url)
        response.raise_for_status()
        data = response.json()
        return BillDetailResponse(**data)
    

    
