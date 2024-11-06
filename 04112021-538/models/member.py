from dataclasses import dataclass, field
from typing import Union

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