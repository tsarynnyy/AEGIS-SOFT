from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid


class ConsentType(str, Enum):
    DATA_COLLECTION = "data_collection"
    DATA_SHARING = "data_sharing"
    CAREGIVER_ACCESS = "caregiver_access"
    ANALYTICS = "analytics"
    MARKETING = "marketing"


class Consent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    member_id: str
    
    # Consent details
    consent_type: ConsentType
    granted: bool
    version: str = "1.0"  # Policy version
    
    # Context
    source: Optional[str] = None  # "onboarding", "settings", "admin"
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Timestamps
    granted_at: datetime = Field(default_factory=datetime.utcnow)
    revoked_at: Optional[datetime] = None
    
    class Config:
        use_enum_values = True


class ConsentCreate(BaseModel):
    member_id: str
    consent_type: ConsentType
    granted: bool
    version: Optional[str] = "1.0"
    source: Optional[str] = None
