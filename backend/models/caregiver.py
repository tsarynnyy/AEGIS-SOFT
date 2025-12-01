from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class Caregiver(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str  # Links to User with role=caregiver
    
    # Profile
    first_name: str
    last_name: str
    phone: Optional[str] = None
    relationship: Optional[str] = None  # "family", "friend", "professional"
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CaregiverOnMember(BaseModel):
    """Join table for Member-Caregiver relationship"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    member_id: str
    caregiver_id: str
    
    # Access control
    can_view_alerts: bool = True
    can_view_metrics: bool = True
    can_add_notes: bool = True
    
    # Status
    invitation_status: str = "pending"  # "pending", "accepted", "declined"
    invitation_sent_at: datetime = Field(default_factory=datetime.utcnow)
    accepted_at: Optional[datetime] = None
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class CaregiverCreate(BaseModel):
    user_id: str
    first_name: str
    last_name: str
    relationship: Optional[str] = None


class CaregiverInvite(BaseModel):
    member_id: str
    email: str
    first_name: str
    last_name: str
    relationship: Optional[str] = None
