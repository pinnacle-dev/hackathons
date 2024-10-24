from typing import Dict, List, Optional
from rcs_types import InboundMessage

database: Dict[str, List[InboundMessage]] = {}


def get(id: str) -> Optional[List[InboundMessage]]:
    return database.get(id)


def set(id: str, msg: InboundMessage):
    if id not in database:
        database[id] = []
    database[id].append(msg)
