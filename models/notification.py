from dataclasses import dataclass
from typing import Optional


@dataclass
class Notification:
    id: Optional[int]
    student_id: int
    message: str
    is_read: bool = False
