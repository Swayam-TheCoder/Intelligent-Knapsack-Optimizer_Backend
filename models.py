from pydantic import BaseModel
from typing import List, Optional

class Product(BaseModel):
    id: int
    name: str
    weight: float
    value: float
    image: Optional[str] = None

class KnapsackRequest(BaseModel):
    capacity: float
