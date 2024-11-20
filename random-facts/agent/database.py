from typing import Dict, List, Optional

database: Dict[str, List[str]] = {}


def get(id: str) -> List[str]:
    return database.get(id, [""])


def set(id: str, facts: List[str]):
    database[id] = facts
