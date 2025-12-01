from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class MetricType(str, Enum):
    # Heart
    HEART_RATE = "heart_rate"
    HRV = "hrv"
    RESTING_HR = "resting_hr"
    
    # Activity
    STEPS = "steps"
    DISTANCE = "distance"
    ACTIVE_MINUTES = "active_minutes"
    CALORIES = "calories"
    
    # Sleep
    SLEEP_DURATION = "sleep_duration"
    SLEEP_EFFICIENCY = "sleep_efficiency"
    DEEP_SLEEP = "deep_sleep"
    REM_SLEEP = "rem_sleep"
    LIGHT_SLEEP = "light_sleep"
    AWAKE_TIME = "awake_time"
    
    # Vitals
    WEIGHT = "weight"
    BMI = "bmi"
    BLOOD_PRESSURE_SYSTOLIC = "bp_systolic"
    BLOOD_PRESSURE_DIASTOLIC = "bp_diastolic"
    BLOOD_OXYGEN = "blood_oxygen"
    BODY_TEMPERATURE = "body_temperature"
    
    # Other
    BATHROOM_VISITS = "bathroom_visits"
    ROOM_TRANSITIONS = "room_transitions"


class MetricSample(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    member_id: str
    
    # Metric data
    type: MetricType
    value_num: Optional[float] = None  # Numeric value
    value_json: Optional[Dict[str, Any]] = None  # Complex data
    unit: Optional[str] = None  # "bpm", "steps", "minutes", "kg", etc.
    
    # Source
    source: str  # "healthkit", "googlefit", "fitbit", "withings", "mock"
    device_account_id: Optional[str] = None
    
    # Timing
    timestamp: datetime  # When the measurement was taken
    ingested_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True


class MetricSampleCreate(BaseModel):
    member_id: str
    type: MetricType
    value_num: Optional[float] = None
    value_json: Optional[Dict[str, Any]] = None
    unit: Optional[str] = None
    source: str
    timestamp: datetime


class MetricSampleBulkCreate(BaseModel):
    samples: list[MetricSampleCreate]
