from dataclasses import dataclass
from typing import Optional


@dataclass
class Student:
    id: Optional[int]
    name: str
    contact: str
