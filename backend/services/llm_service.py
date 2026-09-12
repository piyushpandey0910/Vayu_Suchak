import os
import re
import datetime
from typing import Optional, Dict
from core.config import settings

def _generate_expert_rule_guidance(message: str, city: str, aqi: float, pollutants: Optional[Dict[str, float]] = None) -> str:
    """
    Expert rule-based fallback engine for health queries.
    Provides immediate, reliable, medical-standard advice even when external LLMs are unreachable.
    """
    q = message.lower()
    city_name = city.title() if city else "your area"
    aqi_level = float(aqi) if aqi else 100.0

    # Severity context
    if aqi_level <= 50:
        level_desc = "Good (0–50)"
        risk_tier = "low"
    elif aqi_level <= 100:
        level_desc = "Moderate (51–100)"
        risk_tier = "moderate"
    elif aqi_level <= 150:
        level_desc = "Unhealthy for Sensitive Groups (101–150)"
        risk_tier = "sensitive"
    elif aqi_level <= 200:
        level_desc = "Unhealthy (151–200)"
        risk_tier = "unhealthy"
    elif aqi_level <= 300:
        level_desc = "Very Unhealthy (201–300)"
        risk_tier = "very_unhealthy"
    else:
        level_desc = "Hazardous (301+)"
        risk_tier = "hazardous"

    # Specific topic checks
    if any(k in q for k in ["run", "jog", "exercise", "walk", "outdoor activity", "sports", "cycling", "gym"]):
        if risk_tier in ["very_unhealthy", "hazardous"]:
            return (
                f"🚨 **Avoid outdoor exercise today in {city_name}** (Current AQI: {round(aqi_level)}, {level_desc}). "
                f"High particulate matter (PM2.5) deep in the lungs increases cardiovascular strain during intense breathing. "
                f"**Recommendation**: Move your workout indoors, use a treadmill or do bodyweight exercises in an enclosed space with air filtration."
            )
        elif risk_tier == "unhealthy":
            return (
                f"⚠️ **Limit outdoor exertion in {city_name}** (Current AQI: {round(aqi_level)}, {level_desc}). "
                f"Healthy adults should reduce duration and intensity. Children, elderly, and those with respiratory conditions should completely avoid outdoor sports today."
            )
        elif risk_tier == "sensitive":
            return (
                f"⚡ **Caution for sensitive individuals in {city_name}** (Current AQI: {round(aqi_level)}). "
                f"Healthy adults can exercise outdoors, but if you have asthma, allergies, or heart conditions, consider exercising indoors or scheduling outdoor activities in the afternoon when PM2.5 dispersion is highest."
            )
        else:
            return (
                f"✅ **Air quality in {city_name} is acceptable for outdoor workouts** (AQI: {round(aqi_level)}, {level_desc}). "
                f"You can comfortably jog, run, or cycle outside."
            )

    if any(k in q for k in ["mask", "n95", "kn95", "cloth mask"]):
        if risk_tier in ["unhealthy", "very_unhealthy", "hazardous"]:
            return (
                f"😷 **N95 / FFP2 mask strongly recommended in {city_name}** (Current AQI: {round(aqi_level)}). "
                f"Cloth or standard surgical masks do not filter fine PM2.5 particles effectively. "
                f"Ensure a snug seal around your nose and chin whenever stepping outdoors."
            )
        elif risk_tier == "sensitive":
            return (
                f"😷 **N95 mask advised for sensitive groups in {city_name}** (Current AQI: {round(aqi_level)}). "
                f"If you commute on open roads or have respiratory sensitivities, an N95 or KN95 respirator provides crucial protection against fine particulates."
            )
        else:
            return (
                f"ℹ️ With the current AQI of {round(aqi_level)} in {city_name}, masks are not generally necessary for healthy individuals, though sensitive individuals may choose to wear one in heavy traffic zones."
            )

    if any(k in q for k in ["asthma", "child", "baby", "elderly", "pregnant", "heart", "bronchitis", "allerg"]):
        return (
            f"🏥 **Health Alert for Vulnerable Groups in {city_name}** (AQI: {round(aqi_level)}, {level_desc}):\n\n"
            f"• **Asthma & COPD patients**: Keep rescue inhalers (reliever) within reach at all times.\n"
            f"• **Children & Elderly**: Limit time outdoors, especially during peak traffic and early morning smog hours.\n"
            f"• **Home environment**: Keep windows closed and run an air purifier with a True HEPA filter if available."
        )

    if any(k in q for k in ["purifier", "filter", "hepa", "window", "room", "indoor"]):
        if risk_tier in ["unhealthy", "very_unhealthy", "hazardous"]:
            return (
                f"🏠 **Indoor Air Quality Guidance for {city_name}** (Current AQI: {round(aqi_level)}):\n\n"
                f"• **Keep doors and windows sealed** to prevent toxic outdoor particulates from infiltrating.\n"
                f"• **Turn on HEPA air purifiers** in bedrooms and living rooms.\n"
                f"• Avoid burning incense, candles, or frying foods without kitchen exhaust fans, as this adds indoor particulate load."
            )
        else:
            return (
                f"🌿 At the current AQI of {round(aqi_level)} in {city_name}, cross-ventilation during afternoon hours is safe. An air purifier is helpful for people with dust allergies, but ambient indoor levels are currently manageable."
            )

    # General advisory response
    return (
        f"**Air Quality & Health Advisory for {city_name}**\n\n"
        f"• **Current Status**: AQI {round(aqi_level)} ({level_desc})\n"
        f"• **General Health Impact**: " + (
            "Air is clean and healthy. Great day for outdoor activities!" if risk_tier == "low" else
            "Air quality is acceptable for most people; very sensitive individuals might notice mild irritation." if risk_tier == "moderate" else
            "Sensitive groups (asthma, children, elderly) should reduce prolonged outdoor exertion." if risk_tier == "sensitive" else
            "Everyone may begin to experience health effects; members of sensitive groups may experience more serious health effects. Wear an N95 outdoors." if risk_tier == "unhealthy" else
            "Health alert: risk of health effects is significantly increased for everyone. Avoid outdoor exposure."
        ) + f"\n• **Actionable Advice**: Drink plenty of water, monitor real-time hourly trends on Vayu Suchak, and minimize exposure during early morning hours when inversion layers trap pollutants near the ground."
    )

class LLMService:
    @staticmethod
    def generate_health_chat(message: str, city: str, aqi: float, pollutants: Optional[Dict[str, float]] = None) -> tuple[str, str]:
        """
        Calls Gemini API (or OpenAI) if configured, else seamlessly falls back to expert rule engine.
        Returns: (reply_text, source_identifier)
        """
        # 1. Try Gemini if configured
        if settings.GEMINI_API_KEY:
            try:
                from google import genai
                client = genai.Client(api_key=settings.GEMINI_API_KEY)
                prompt = (
                    f"You are 'Vayu Suchak AI Health Assistant', an expert pulmonologist and environmental health advisor.\n"
                    f"Location: {city}\n"
                    f"Current Air Quality Index (AQI): {aqi}\n"
                    f"Pollutant breakdown: {pollutants or 'standard'}\n\n"
                    f"User question: {message}\n\n"
                    f"Provide concise, empathetic, medically accurate health guidance formatted with clear bullet points. "
                    f"Advise clearly on masks (N95), exercise, sensitive groups (asthmatics, children), and indoor precautions."
                )
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt
                )
                if response and response.text:
                    return response.text.strip(), "gemini"
            except Exception as e:
                print(f"[LLMService] Gemini API error: {e}")

        # 2. Try OpenAI if configured
        if settings.OPENAI_API_KEY:
            try:
                import httpx
                headers = {
                    "Authorization": f"Bearer {settings.OPENAI_API_KEY}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": "You are Vayu Suchak AI Health Assistant, providing clear, concise, actionable health advice regarding air pollution."},
                        {"role": "user", "content": f"City: {city}, AQI: {aqi}, Question: {message}"}
                    ],
                    "temperature": 0.4
                }
                resp = httpx.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload, timeout=6.0)
                if resp.status_code == 200:
                    reply = resp.json()["choices"][0]["message"]["content"]
                    return reply.strip(), "openai"
            except Exception as e:
                print(f"[LLMService] OpenAI API error: {e}")

        # 3. Seamless expert rule engine fallback
        fallback_reply = _generate_expert_rule_guidance(message, city, aqi, pollutants)
        return fallback_reply, "expert_rules"
