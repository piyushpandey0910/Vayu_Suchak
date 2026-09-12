from fastapi import APIRouter, Request, Query, Depends
from typing import Optional
from core.rate_limiter import limiter
from core.config import settings
from core.security import get_current_user_optional, UserPlaceholder
from schemas.advisory import HealthAdvisoryResponse
from ml.features import get_aqi_category_and_color

router = APIRouter(tags=["Health Advisory"])

@router.get("/health-advisory", response_model=HealthAdvisoryResponse)
@limiter.limit(f"{settings.RATE_LIMIT_GENERAL_MINUTE}/minute")
async def get_health_advisory(
    request: Request,
    aqi: float = Query(..., description="Current AQI value (0-500)"),
    current_user: Optional[UserPlaceholder] = Depends(get_current_user_optional)
):
    """
    Returns rule-based health guidance and actionable precautions
    tailored to the given Air Quality Index (AQI) value.
    Guaranteed 100% reliable without external API dependencies.
    """
    category, color = get_aqi_category_and_color(aqi)

    if aqi <= 50:
        return HealthAdvisoryResponse(
            aqi=aqi,
            category=category,
            color=color,
            headline="Air quality is satisfactory. Breathe easy!",
            general_advice="Air pollution poses little or no risk to the general public. Ideal conditions for all activities.",
            mask_recommendation="No mask required for general outdoor activities.",
            outdoor_activity="Perfect conditions for walks, running, and all outdoor recreation.",
            exercise_advice="Great day for intense cardio, cycling, and outdoor workouts.",
            sensitive_groups="People with asthma and respiratory conditions can enjoy normal outdoor activities.",
            air_purifier_needed=False
        )
    elif aqi <= 100:
        return HealthAdvisoryResponse(
            aqi=aqi,
            category=category,
            color=color,
            headline="Air quality is acceptable for most people.",
            general_advice="A very small number of unusually sensitive individuals may experience slight respiratory irritation.",
            mask_recommendation="Optional in heavy traffic or industrial areas.",
            outdoor_activity="Normal outdoor activities are safe for the general public.",
            exercise_advice="Outdoor workouts and sports are safe. Sensitive individuals can monitor symptoms.",
            sensitive_groups="Unusually sensitive individuals should consider taking more breaks during outdoor exertion.",
            air_purifier_needed=False
        )
    elif aqi <= 150:
        return HealthAdvisoryResponse(
            aqi=aqi,
            category=category,
            color=color,
            headline="Members of sensitive groups may experience health effects.",
            general_advice="The general public is less likely to be affected. Sensitive individuals should reduce prolonged outdoor exertion.",
            mask_recommendation="Recommended for sensitive groups (children, elderly, asthmatics) and open commuters.",
            outdoor_activity="Take regular rest breaks during extended outdoor work or sports.",
            exercise_advice="Sensitive individuals should reduce prolonged or heavy outdoor exertion. Move workouts indoors if coughing occurs.",
            sensitive_groups="People with asthma, heart conditions, children, and older adults should limit outdoor exertion.",
            air_purifier_needed=True
        )
    elif aqi <= 200:
        return HealthAdvisoryResponse(
            aqi=aqi,
            category=category,
            color=color,
            headline="Everyone may begin to experience health effects.",
            general_advice="Active children and adults, and people with respiratory diseases, should avoid prolonged outdoor exertion.",
            mask_recommendation="N95 or FFP2 respirator strongly advised for anyone stepping outside.",
            outdoor_activity="Significantly limit outdoor exposure, especially during morning and evening rush hours.",
            exercise_advice="Avoid high-intensity outdoor exercise. Move workouts inside with doors and windows closed.",
            sensitive_groups="Vulnerable individuals must stay indoors as much as possible and keep emergency medications accessible.",
            air_purifier_needed=True
        )
    elif aqi <= 300:
        return HealthAdvisoryResponse(
            aqi=aqi,
            category=category,
            color=color,
            headline="Health alert: Serious risk of health effects for everyone.",
            general_advice="High concentrations of fine toxic particulates. General public should strictly minimize all outdoor activities.",
            mask_recommendation="N95/KN95 respirator mandatory when outdoors with a tight nasal seal.",
            outdoor_activity="Avoid all non-essential outdoor travel and activities.",
            exercise_advice="Strictly avoid outdoor sports or running. Exercise indoors only in filtered air.",
            sensitive_groups="Sensitive groups must remain strictly indoors and use HEPA air purifiers.",
            air_purifier_needed=True
        )
    else:
        return HealthAdvisoryResponse(
            aqi=aqi,
            category=category,
            color=color,
            headline="Hazardous Emergency Conditions: Severe health warning.",
            general_advice="Emergency atmospheric conditions. Everyone is likely to experience acute respiratory or cardiovascular symptoms.",
            mask_recommendation="N95 or higher respirator mandatory outdoors. Limit outdoor exposure to absolute emergencies.",
            outdoor_activity="Do not go outside unless strictly necessary. Keep all doors and windows sealed shut.",
            exercise_advice="Zero outdoor exercise. Indoor exertion should be light and inside purified rooms.",
            sensitive_groups="Remain indoors in sealed rooms with active HEPA air filtration. Seek medical attention if experiencing breathing distress.",
            air_purifier_needed=True
        )
