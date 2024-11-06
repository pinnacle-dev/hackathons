import os
from dotenv import load_dotenv
from services.congress_api import CongressAPI
from services.database import DatabaseService
import time
import json
import requests
from bs4 import BeautifulSoup
import lxml
import anthropic
from termcolor import colored

# Load environment variables from .env file
load_dotenv()

def get_bill_text_from_xml(xml_url):
    try:
        # Fetch the XML content
        response = requests.get(xml_url)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        # Parse XML with BeautifulSoup using lxml parser
        soup = BeautifulSoup(response.content, 'lxml-xml')
        
        # Extract all text content, removing XML tags
        text_content = soup.get_text(separator=' ', strip=True)
        
        return text_content
    except requests.RequestException as e:
        print(f"Error fetching XML: {e}")
        return None
    except Exception as e:
        print(f"Error parsing XML: {e}")
        return None
    
def create_prompt(bill_text):
    # Load the prompt template from JSON
    with open('prompt_template.json', 'r') as f:
        prompt_data = json.load(f)
    
    # Return both system prompt and formatted user prompt separately
    return {
        "system_prompt": prompt_data['system_prompt'],
        "template": prompt_data['template'].format(bill_text=bill_text)
    }


client_anthropic = anthropic.Client(api_key=os.getenv('ANTHROPIC_API_KEY'))

def get_summary(text):
    prompt = create_prompt(text)
    # Updated Anthropic API call
    message = client_anthropic.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        system = prompt['system_prompt'],
        messages=[
            {"role": "user", "content": prompt['template']}
        ]
    )
    # Extract just the text content from the TextBlock
    return message.content[0].text

def print_bill_details(bill_one, bill_info, bill_cosponsors, summary_json):
    # Get unique parties from all sponsors
    sponsor_parties = set(sponsor['party'] for sponsor in bill_info.bill['sponsors'])
    
    # Determine color based on party mix
    title_color = 'purple' if {'D', 'R'}.issubset(sponsor_parties) else \
                 'blue' if 'D' in sponsor_parties else \
                 'red' if 'R' in sponsor_parties else 'white'
    
    print(f"\n\n{colored(bill_one.title, title_color)} - {colored(bill_one.originChamber, title_color)}")

    print("\n" + colored("Sponsors: \n", "white"))
    for sponsor in bill_info.bill['sponsors']:
        sponsor_color = 'blue' if sponsor['party'] == "D" else 'red' if sponsor['party'] == "R" else 'white'
        print(f"- {colored(sponsor['fullName'], sponsor_color)}")

    print("\n" + colored("Cosponsors: \n", "white"))
    if bill_cosponsors is []:
        print("No cosponsors")
    for cosponsor in bill_cosponsors.cosponsors:
        cosponsor_color = 'blue' if cosponsor['party'] == "D" else 'red' if cosponsor['party'] == "R" else 'white'
        print(f"- {colored(cosponsor['fullName'], cosponsor_color)}, sponsorship date: {cosponsor['sponsorshipDate']}")

    print("\nOverview:")
    print(summary_json["overview"])
    print("\nPoints:")
    for i, element in enumerate(summary_json["shocking_elements"], 1):
        print(f"{i}. {element}")

def main():
    api_key = os.getenv('CONGRESS_API_KEY')
    if not api_key:
        raise ValueError("API key not found. Please set the API_KEY environment variable.")
    
    api: CongressAPI = CongressAPI(api_key)
    db = DatabaseService()
    
    # Get existing members from the database
    existing_bioguide_ids = db.get_existing_member_ids()

    NUM_BILLS = 25
    CONGRESS = 118
    TYPE = "s"
    
    bill_data = api.get_bills(NUM_BILLS, CONGRESS, TYPE)

    for bill in bill_data.bills:
        congress = bill.congress
        bill_number = bill.number
        bill_type = bill.type

        bill_text = api.get_bill_text(congress, bill_type, bill_number)
        bill_cosponsors = api.get_bill_cosponsors(congress, bill_type, bill_number)
        bill_info = api.get_bill_information(congress, bill_type, bill_number)
        
        summary_json = json.loads(get_summary(bill_text))
        print_bill_details(bill, bill_info, bill_cosponsors, summary_json)
        
        # Add a separator between bills
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    main()
