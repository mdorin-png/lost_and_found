from dataclasses import dataclass
from typing import Optional


@dataclass
class Claim:
    id: Optional[int]
    student_id: int
    found_report_id: int
    identifying_information: str
    status: str = "pending"
