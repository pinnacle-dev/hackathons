from bs4 import BeautifulSoup
import os
from openai import OpenAI
from dotenv import load_dotenv
import anthropic
import requests
from urllib.parse import urlparse
import time

# Load environment variables
load_dotenv()

def create_prompt(bill_text, bill_metadata):
    return f"""You are tasked with summarizing a bill based on its text and metadata. Your summary should consist of three paragraphs: a brief overview, shocking parts of the bill, and information about who introduced it.

First, you will be provided with the full text of the bill:

<bill_text>
{bill_text}
</bill_text>

Next, you will be given metadata about the bill, including its sponsors and party affiliations:

<bill_metadata>
{bill_metadata}
</bill_metadata>

Please follow these steps to create your summary:

1. Carefully read and analyze the bill text and metadata.

2. In your analysis, pay attention to:
   - The main purpose and key provisions of the bill
   - Any controversial or unusual elements
   - The bill's sponsors and their party affiliations

3. Prepare your summary in three paragraphs:

   Paragraph 1: Brief Overview | 1-2 sentences
   - Summarize the main purpose and key provisions of the bill
   - Keep this paragraph concise and informative

   Paragraph 2: Shocking or Controversial Elements | 5-10 sentences
   - Highlight any parts of the bill that may be considered surprising, controversial, or unusual
   - If there are no shocking elements, discuss the most significant or impactful provision. Typically that's around 5 shocking things from the bill.
   - Present these in bullet points

   Paragraph 3: Bill Introduction and Partisanship | 1-3 setences
   - Provide information on who introduced the bill
   - Indicate whether the bill is Democratic, Republican, or bipartisan based on its sponsors
   - If bipartisan, mention the level of support from each party

4. Format your response using XML:
   <summary>
       <overview></overview>
       <shocking_elements></shocking_elements>
       <introduction_and_partisanship></introduction_and_partisanship>
   </summary>
   
5. Keep each paragraph to a reasonable length (<=10 sentences)

6. Use objective language and avoid personal opinions or biases in your summary.

7. Ensure each section is properly enclosed within its respective XML tags.

Remember to base your summary solely on the information provided in the bill text and metadata. Do not include any external information or personal knowledge about the bill or its context."""


# Initialize clients
client_openai = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
client_anthropic = anthropic.Client(api_key=os.getenv('ANTHROPIC_API_KEY'))

def summarize_text(text, vote_info):
    # Format the metadata from vote_info into a text summary
    metadata = f"""
    Senate Roll Call Vote Summary:
    Total Yeas: {vote_info['vote_summary'].get('total_yeas', 0)}
    Total Nays: {vote_info['vote_summary'].get('total_nays', 0)}
    Not Voting: {vote_info['vote_summary'].get('total_not_voting', 0)}
    
    Vote Result: {vote_info['vote_summary'].get('result', 'Unknown')}
    
    Voting Breakdown:
    Yeas: {', '.join(f"{senator['name']} ({senator['party_state']})" for senator in vote_info['yeas'])}
    Nays: {', '.join(f"{senator['name']} ({senator['party_state']})" for senator in vote_info['nays'])}
    Not Voting: {', '.join(f"{senator['name']} ({senator['party_state']})" for senator in vote_info['not_voting'])}
    """
    
    prompt = create_prompt(text, metadata)

    print("PROMPT: ", prompt)

    # Updated Anthropic API call
    message = client_anthropic.messages.create(
        model="claude-3-5-sonnet-20241022",
        max_tokens=2048,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    return message.content

def parse_bill_info(html_file, vote_info=None):
    print("Starting parse_bill_info...")  # Debugging print
    # Read the HTML file
    with open(html_file, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Create BeautifulSoup object
    soup = BeautifulSoup(content, 'html.parser')
    
    # Dictionary to store bill information
    bill_info = {}
    
    # Get basic bill information
    bill_info['title'] = soup.find('h1').text.strip() if soup.find('h1') else ''
    
    # Get all text content from the 'bill-summary' class
    bill_summary = soup.find_all(class_='bill-summary')
    bill_summary_text = '\n'.join([summary.text.strip() for summary in bill_summary if summary.text.strip()])
    bill_info['content'] = bill_summary_text
    print("HERE YOU GO", bill_info)  # This should print if the function executes correctly
    
    # Add summary to bill_info if vote_info is available
    if bill_summary_text and vote_info:
        bill_info['summary'] = summarize_text(bill_summary_text, vote_info)
    else:
        bill_info['summary'] = "No summary available - missing vote information"
    
    return bill_info

def parse_senate_vote(html_file):
    """Parse Senate roll call vote information from HTML file"""
    with open(html_file, 'r', encoding='utf-8') as file:
        content = file.read()
    
    soup = BeautifulSoup(content, 'html.parser')
    
    vote_info = {
        'yeas': [],
        'nays': [],
        'not_voting': [],
        'vote_summary': {}
    }

    # Get vote summary information
    summary_section = soup.find('div', class_='contenttext')
    if summary_section:
        # Extract vote counts
        vote_counts = {}
        for div in soup.find_all('div', class_='contenttext'):
            text = div.text.strip()
            if 'YEAs' in text:
                # Extract number using string manipulation
                count = text.split('YEAs')[-1].strip()
                if count.isdigit():
                    vote_counts['total_yeas'] = int(count)
            elif 'NAYs' in text:
                count = text.split('NAYs')[-1].strip()
                if count.isdigit():
                    vote_counts['total_nays'] = int(count)
            elif 'Not Voting' in text and len(text.split()) < 5:  # Avoid longer text sections
                count = text.split('Not Voting')[-1].strip()
                if count.isdigit():
                    vote_counts['total_not_voting'] = int(count)

        # Get vote result
        result_div = soup.find('div', string=lambda text: text and 'Vote Result:' in text)
        if result_div:
            vote_counts['result'] = result_div.text.replace('Vote Result:', '').strip()

        vote_info['vote_summary'] = vote_counts

    # Parse individual votes
    for div in soup.find_all('div', class_='newspaperDisplay_3column'):
        votes_text = div.get_text()
        
        # Process each line of votes
        for line in votes_text.split('\n'):
            if not line.strip():
                continue
                
            # Parse senator info
            if ',' in line and any(x in line for x in ['Yea', 'Nay', 'Not Voting']):
                name_part, vote_part = line.split(',', 1)
                name = name_part.strip()
                
                # Extract party and state
                party_state = name[name.find('(')+1:name.find(')')]
                
                senator_info = {
                    'name': name,
                    'party_state': party_state
                }
                
                # Add to appropriate list based on vote
                if 'Yea' in vote_part:
                    vote_info['yeas'].append(senator_info)
                elif 'Nay' in vote_part:
                    vote_info['nays'].append(senator_info)
                elif 'Not Voting' in vote_part:
                    vote_info['not_voting'].append(senator_info)

    return vote_info

def scrape_congress_bill(url):
    """Scrape bill information from congress.gov and ensure it is within token limits."""
    try:
        # Enhanced headers to look more like a real browser
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0'
        }
        
        # Add a session to maintain cookies
        session = requests.Session()
        response = session.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Add a small delay to mimic human behavior
        time.sleep(2)
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        bill_info = {}
        
        # Get bill title
        title_elem = soup.find('h1', class_='legDetail')
        bill_info['title'] = title_elem.text.strip() if title_elem else ''
        
        # Get bill content from the billTextContainer section
        content_elem = soup.find('pre', id='billTextContainer')
        if content_elem:
            bill_text = content_elem.text
            bill_info['content'] = bill_text
        else:
            # Fallback to get all text within element id 'bill-summary' and its children
            summary_elem = soup.find(id='bill-summary')
            if summary_elem:
                bill_text = summary_elem.get_text(separator='\n', strip=True)
                bill_info['content'] = bill_text

        # Check token count and trim if necessary
        while True:
            response = client_anthropic.beta.messages.count_tokens(
                betas=["token-counting-2024-11-01"],
                model="claude-3-5-sonnet-20241022",
                system="You are a scientist",
                messages=[{
                    "role": "user",
                    "content": bill_info['content']
                }],
            )
            
            # Debug print to understand the response structure
            print("Token count response:", response)
            
            # Assuming response is an object, not a dictionary
            token_count = response.input_tokens  # Adjust this line based on the actual response structure
            
            if token_count <= 180000:
                break
            # Calculate the number of tokens over the limit
            tokens_over_limit = token_count - 180000
            
            # Calculate the number of characters to trim
            trim_length = tokens_over_limit * 4  # CHAR_TOKEN_RATIO is 3
            
            # Trim the content by the calculated length
            bill_info['content'] = bill_info['content'][:-trim_length]

        return f"CONTENT: {bill_info['content']}"
    except Exception as e:
        raise RuntimeError(f"Error scraping congress.gov: {str(e)}")

def main():
    # Use a hardcoded URL instead of prompting for input
    bill_source = "https://www.congress.gov/bill/118th-congress/house-bill/3935/text"
    senate_vote_file = 'senatecall.html'
    
    try:
        # Parse senate vote information first
        print("Checking if senate vote file exists.")
        vote_info = None
        if os.path.exists(senate_vote_file):
            print("Senate vote file found. Parsing vote information.")
            vote_info = parse_senate_vote(senate_vote_file)
        else:
            print("Warning: Senate vote file not found.")

        print("Scraping bill information from congress.gov.")
        bill_info = scrape_congress_bill(bill_source)

        print("Generating summary from bill information and vote info.")
        xlm_summary = summarize_text(bill_info, vote_info)
        print("Summary generated successfully.")
        print("xlm_summary:", xlm_summary)

        # Extract and print each section of the XML summary
        if xlm_summary:
            print("Parsing XML summary.")
            soup = BeautifulSoup(xlm_summary, 'xml')
            
            # Print each section
            print("Extracting overview section from XML.")
            print("\nOverview:")
            overview = soup.find('overview')
            if overview:
                print("Overview section found.")
                print(overview.text.strip())
            else:
                print("Warning: Overview section not found in XML.")
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
