import os
from typing import Dict, Any, List, Set
from supabase import create_client, Client

class DatabaseService:
    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_KEY')

        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase credentials not found. Please set SUPABASE_URL and SUPABASE_KEY environment variables.")

        self.client: Client = create_client(self.supabase_url, self.supabase_key)

    def store_members(self, members_data: List[Dict[str, Any]]) -> None:
        """Store member data in Supabase."""
        if not members_data:
            print("No new members to add to the database.")
            return

        try:
            result = self.client.table('CongressMembers').upsert(members_data).execute()
            print(f"Successfully stored data for {len(members_data)} new members")
        except Exception as e:
            print(f"Error batch storing members: {str(e)}")

    def store_legislation(self, legislation_data: List[Dict[str, Any]]) -> None:
        """Store legislation data in Supabase."""
        if not legislation_data:
            print("No new legislation to add to the database.")
            return

        try:
            result = self.client.table('Legislation').upsert(legislation_data).execute()
            print(f"Successfully stored {len(legislation_data)} pieces of legislation")
        except Exception as e:
            print(f"Error batch storing legislation: {str(e)}")

    def get_existing_member_ids(self) -> Set[str]:
        """Get bioguide IDs of existing members from the database."""
        try:
            existing_members = self.client.table('CongressMembers').select('bioguideId').execute()
            return {member['bioguideId'] for member in existing_members.data}
        except Exception as e:
            print(f"Error fetching existing members: {str(e)}")
            return set()

    @staticmethod
    def prepare_member_data(member) -> Dict[str, Any]:
        """Convert member object to database format."""
        return {
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

    @staticmethod
    def prepare_legislation_data(legislation, member_id: str) -> Dict[str, Any]:
        """Convert legislation object to database format."""
        base_data = {
            'congress': legislation.congress,
            'introducedDate': legislation.introducedDate,
            'url': legislation.url,
            'memberBioguideId': member_id,
            'latestAction': legislation.latestAction.__dict__ if legislation.latestAction else None,
        }

        if hasattr(legislation, 'amendmentNumber'):
            # This is an amendment
            base_data.update({
                'amendmentNumber': legislation.amendmentNumber,
                'type': legislation.type.value if legislation.type else None,
                'isAmendment': True
            })
        else:
            # This is a bill/resolution
            base_data.update({
                'number': legislation.number,
                'title': legislation.title,
                'policyArea': legislation.policyArea,
                'type': legislation.type.value if legislation.type else None,
                'isAmendment': False
            })

        return base_data 