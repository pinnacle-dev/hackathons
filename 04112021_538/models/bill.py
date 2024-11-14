from typing import List, Optional
from dataclasses import dataclass

@dataclass
class CboEstimate:
    description: str
    pubDate: str
    title: str
    url: str

@dataclass
class CommitteeReport:
    citation: str
    url: str

@dataclass
class CountUrl:
    count: int
    url: str

@dataclass
class LatestAction:
    actionDate: str
    text: str

@dataclass
class Law:
    number: str
    type: str

@dataclass
class PolicyArea:
    name: str

@dataclass
class Sponsor:
    bioguideId: str
    district: int
    firstName: str
    fullName: str
    isByRequest: str
    lastName: str
    middleName: str
    party: str
    state: str
    url: str

@dataclass
class BillDetail:
    actions: CountUrl
    amendments: CountUrl
    cboCostEstimates: List[CboEstimate]
    committeeReports: List[CommitteeReport]
    committees: dict
    congress: int
    constitutionalAuthorityStatementText: str
    cosponsors: dict
    introducedDate: str
    latestAction: LatestAction
    laws: List[Law]
    number: str
    originChamber: str
    policyArea: PolicyArea
    relatedBills: dict
    sponsors: List[Sponsor]
    subjects: dict
    summaries: dict
    textVersions: dict
    title: str
    titles: dict
    type: str
    updateDate: str
    updateDateIncludingText: str

@dataclass 
class BillDetailResponse:
    bill: BillDetail
    request: dict
    pagination: Optional[dict] = None
    
@dataclass
class Cosponsor:
    bioguideId: str
    district: int
    firstName: str
    fullName: str
    isOriginalCosponsor: bool
    lastName: str
    middleName: Optional[str]
    party: str
    sponsorshipDate: str
    state: str
    url: str

@dataclass
class CosponsorResponse:
    cosponsors: List[Cosponsor]
    pagination: dict
    request: dict