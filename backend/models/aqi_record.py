import datetime
from sqlalchemy import Column, Integer, Float, String, DateTime, Index
from models.database import Base

class AQIHistoryRecord(Base):
    __tablename__ = "aqi_history"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String(100), index=True, nullable=False)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow, index=True, nullable=False)
    aqi = Column(Float, nullable=False)
    pm25 = Column(Float, nullable=False)
    pm10 = Column(Float, nullable=True)
    co = Column(Float, nullable=True)
    no = Column(Float, nullable=True)
    no2 = Column(Float, nullable=True)
    so2 = Column(Float, nullable=True)
    o3 = Column(Float, nullable=True)
    temperature = Column(Float, nullable=True)
    humidity = Column(Float, nullable=True)
    source = Column(String(50), default="recorded")  # "recorded" or "forecast"
    
    # Nullable user_id for future per-user sensors or saved readings (Section 8)
    user_id = Column(String(100), nullable=True, index=True)

    __table_args__ = (
        Index("idx_city_timestamp", "city", "timestamp"),
    )

class AIChatLog(Base):
    __tablename__ = "ai_chat_logs"

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(100), nullable=True, index=True)
    message = Column(String(1000), nullable=False)
    response = Column(String(4000), nullable=False)
    city = Column(String(100), nullable=True)
    current_aqi = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    
    # Nullable user_id for future account chat history (Section 8)
    user_id = Column(String(100), nullable=True, index=True)

class SavedLocation(Base):
    __tablename__ = "saved_locations"

    id = Column(Integer, primary_key=True, index=True)
    city = Column(String(100), nullable=False)
    state = Column(String(100), nullable=True)
    country = Column(String(100), default="India")
    lat = Column(Float, nullable=True)
    lon = Column(Float, nullable=True)

    # Nullable user_id for future user saved locations (Section 8)
    user_id = Column(String(100), nullable=True, index=True)
