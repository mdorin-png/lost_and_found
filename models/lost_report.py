from dataclasses import dataclass
from typing import Optional


@dataclass
class LostReport:
    id: Optional[int]
    student_id: int
    item_id: int
    location_id: int
    status: str = "open"
