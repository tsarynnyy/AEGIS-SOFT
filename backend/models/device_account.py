from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class DeviceType(str, Enum):
    HEALTHKIT = "healthkit"
    GOOGLE_FIT = "googlefit"
    FITBIT = "fitbit"
    OURA = "oura"
    GARMIN = "garmin"
    WITHINGS = "withings"
    MOCK = "mock"


class DeviceAccount(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    member_id: str
    
    # Device info
    device_type: DeviceType
    device_name: Optional[str] = None  # "Apple Watch", "Fitbit Charge 5"
    
    # OAuth tokens (encrypted in production)
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires_at: Optional[datetime] = None
    
    # Sync status
    is_active: bool = True
    last_sync_at: Optional[datetime] = None
    last_sync_status: Optional[str] = None  # "success", "failed"
    last_sync_error: Optional[str] = None
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = None
    
    # Timestamps
    connected_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True


class DeviceAccountCreate(BaseModel):
    member_id: str
    device_type: DeviceType
    device_name: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
