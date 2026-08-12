from dataclasses import dataclass
from typing import Optional


@dataclass
class Item:
    id: Optional[int]
    description: str
    category: str
