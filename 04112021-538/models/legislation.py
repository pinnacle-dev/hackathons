from typing import List, Optional, Union
from datetime import datetime
from pydantic import BaseModel

class BillLatestAction(BaseModel):
    actionDate: str
    text: str

class Bill(BaseModel):
    congress: int
    latestAction: BillLatestAction
    number: str
    originChamber: str
    originChamberCode: str
    title: str
    type: str
    updateDate: str
    updateDateIncludingText: str
    url: str

class BillResponse(BaseModel):
    bills: List[Bill] 

class BillTextFormat(BaseModel):
    type: str
    url: str

class BillTextVersion(BaseModel):
    date: Union[datetime, str, None]
    formats: List[BillTextFormat]
    type: str

class BillTextResponse(BaseModel):
    pagination: dict
    request: dict
    textVersions: List[BillTextVersion] 