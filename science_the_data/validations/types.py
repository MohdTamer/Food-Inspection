from typing import Any, TypedDict


class Issue(TypedDict):
    field: str
    message: str
    count: int
    sample: list[Any]
