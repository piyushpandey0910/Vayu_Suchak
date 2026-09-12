from typing import List, Optional, Dict
from pydantic import BaseModel

class PollutantItem(BaseModel):
    name: str
    code: str
    value: float
    unit: str
    status: str
    color: str

class CurrentAQIResponse(BaseModel):
    city: str
    timestamp: str
    aqi: float
    category: str
    color: str
    pm25: float
    pm10: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    wind_speed: Optional[float] = None
    pollutants: Dict[str, PollutantItem]
    source: str = "live"

class ForecastPoint(BaseModel):
    timestamp: str
    step: int
    predicted_pm25: float
    predicted_aqi: float
    category: str
    color: str
    confidence_pct: float
    lower_bound: float
    upper_bound: float

class ForecastResponse(BaseModel):
    city: str
    horizon: str
    generated_at: str
    overall_status: str
    average_predicted_aqi: float
    points: List[ForecastPoint]

class HistoryPoint(BaseModel):
    timestamp: str
    aqi: float
    pm25: float
    pm10: Optional[float] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None

class HistoryResponse(BaseModel):
    city: str
    range: str
    points: List[HistoryPoint]

class PollutantsResponse(BaseModel):
    city: str
    timestamp: str
    pollutants: Dict[str, PollutantItem]
