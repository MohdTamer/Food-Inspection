from typing import TypedDict, Any

class Issue(TypedDict):
    field: str
    message: str
    count: int
    sample: list[Any]