import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Vayu Suchak – AQI Prediction & Health Advisory System"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api"

    # External Provider Keys (kept strictly on server)
    WAQI_API_KEY: str = ""
    OPENAQ_API_KEY: str = ""
    GEMINI_API_KEY: str = ""
    OPENAI_API_KEY: str = ""

    # Database
    DATABASE_URL: str = "sqlite:///./vayu_suchak.db"

    # Host & Port
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000,http://127.0.0.1:5173"

    # Rate Limiting
    RATE_LIMIT_AI_CHAT_MINUTE: int = 10
    RATE_LIMIT_AI_CHAT_DAY: int = 100
    RATE_LIMIT_FORECAST_MINUTE: int = 30
    RATE_LIMIT_GENERAL_MINUTE: int = 60

    # ML Model directory
    ML_MODEL_PATH: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml", "aqi_model.pkl")
    ML_FEATURES_PATH: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml", "model_features.pkl")
    ML_DATA_PATH: str = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml", "data", "kanpur_clean_wide.csv")

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    def redact_key(self, key: str) -> str:
        if not key:
            return "<not-set>"
        if len(key) <= 6:
            return "***"
        return f"{key[:3]}...{key[-3:]}"

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
