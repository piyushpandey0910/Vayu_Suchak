from pydantic import BaseModel

class HealthAdvisoryResponse(BaseModel):
    aqi: float
    category: str
    color: str
    headline: str
    general_advice: str
    mask_recommendation: str
    outdoor_activity: str
    exercise_advice: str
    sensitive_groups: str
    air_purifier_needed: bool
