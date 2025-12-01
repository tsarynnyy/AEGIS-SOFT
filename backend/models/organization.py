from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class Organization(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    
    # Settings
    timezone: str = "Europe/Kyiv"
    locale: str = "en-US"
    
    # Risk engine settings
    risk_sensitivity: str = "medium"  # "low", "medium", "high"
    alert_quiet_hours_start: Optional[int] = 22  # 10 PM
    alert_quiet_hours_end: Optional[int] = 7    # 7 AM
    
    # Compliance
    hipaa_enabled: bool = True
    gdpr_enabled: bool = True
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class OrganizationCreate(BaseModel):
    name: str
    timezone: Optional[str] = "Europe/Kyiv"
    locale: Optional[str] = "en-US"
