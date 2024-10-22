from typing import Dict, List, Optional
from rcs_types import PayloadData

database: Dict[str, List[PayloadData]] = {}


def get(id: str) -> Optional[List[PayloadData]]:
    return database.get(id)


def set(id: str, msg: PayloadData):
    if id not in database:
        database[id] = []
    database[id].append(msg)
