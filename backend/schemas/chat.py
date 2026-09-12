from typing import Optional, Dict
from pydantic import BaseModel

class ChatRequest(BaseModel):
    message: str
    city: Optional[str] = "Kanpur"
    current_aqi: Optional[float] = 100.0
    pollutants: Optional[Dict[str, float]] = None

class ChatResponse(BaseModel):
    reply: str
    timestamp: str
    source: str  # "gemini", "openai", or "expert_rules"
