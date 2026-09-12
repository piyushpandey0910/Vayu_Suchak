from typing import List, Optional
from pydantic import BaseModel

class LocationItem(BaseModel):
    city: str
    state: Optional[str] = None
    country: str = "India"
    lat: Optional[float] = None
    lon: Optional[float] = None

class LocationSearchResponse(BaseModel):
    query: str
    results: List[LocationItem]
