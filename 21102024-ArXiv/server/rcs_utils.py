    
from rcs import Pinnacle, RcsFunctionalities
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the API key from .env
api_key = os.getenv('PINNACLE_API_KEY')

client = Pinnacle(
    api_key=api_key,
)

def check_rcs_functionality(phone_number):
  functionality: RcsFunctionalities = client.get_rcs_functionality(phone_number=phone_number)
  if functionality.is_enabled:
    print(f"RCS enabled on {phone_number}")
    return True
  print(f"RCS not enabled on {phone_number}")
  return False