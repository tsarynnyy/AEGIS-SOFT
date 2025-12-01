from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime, date
import uuid


class Member(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str  # Links to User
    org_id: str
    
    # Profile
    first_name: str
    last_name: str
    date_of_birth: Optional[date] = None
    gender: Optional[str] = None
    
    # Preferences
    locale: str = "en-US"
    timezone: str = "Europe/Kyiv"
    
    # Health context (non-diagnostic)
    health_notes: Optional[str] = None  # General wellness notes
    
    # Data sharing
    data_sharing_enabled: bool = True
    data_sharing_paused_until: Optional[datetime] = None
    
    # Emergency contacts
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class MemberCreate(BaseModel):
    user_id: str
    org_id: str
    first_name: str
    last_name: str
    date_of_birth: Optional[date] = None
    timezone: Optional[str] = "Europe/Kyiv"
    locale: Optional[str] = "en-US"


class MemberResponse(BaseModel):
    id: str
    user_id: str
    first_name: str
    last_name: str
    locale: str
    timezone: str
    data_sharing_enabled: bool
    created_at: datetime
