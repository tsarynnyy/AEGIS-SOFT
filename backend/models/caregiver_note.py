from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
import uuid


class CaregiverNote(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    member_id: str
    caregiver_id: str
    
    # Note content
    note_text: str
    note_type: str = "general"  # "general", "concern", "observation", "action"
    
    # Related to alert
    related_alert_id: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class CaregiverNoteCreate(BaseModel):
    member_id: str
    note_text: str
    note_type: Optional[str] = "general"
    related_alert_id: Optional[str] = None


class PushNotificationLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Recipient
    user_id: str
    push_token: Optional[str] = None
    
    # Notification content
    title: str
    body: str
    data: Optional[dict] = None
    
    # Type
    notification_type: str  # "risk_alert", "caregiver_invite", "general"
    
    # Status
    status: str = "pending"  # "pending", "sent", "failed"
    error_message: Optional[str] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    sent_at: Optional[datetime] = None
