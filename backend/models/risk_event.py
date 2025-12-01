from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class RiskTier(str, Enum):
    GREEN = "green"
    YELLOW = "yellow"
    RED = "red"


class RiskFactor(BaseModel):
    type: str  # "hrv_drop", "sleep_efficiency_low", "steps_decline", etc.
    window_days: Optional[int] = None
    delta: Optional[float] = None  # % change or absolute
    threshold: Optional[float] = None
    actual_value: Optional[float] = None
    baseline_value: Optional[float] = None
    severity: Optional[float] = None  # 0-1 score


class RiskEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    member_id: str
    org_id: str
    
    # Risk assessment
    tier: RiskTier
    score: float  # 0-100 composite risk score
    
    # Explanation
    factors: List[RiskFactor] = []
    explanation_text: str  # Human-readable summary
    
    # Workflow
    status: str = "new"  # "new", "acknowledged", "in_progress", "resolved", "dismissed"
    assignee_id: Optional[str] = None  # Care team member
    
    # Actions
    suggested_actions: List[str] = []  # ["Check in", "Schedule call", ...]
    caregiver_notes: Optional[str] = None
    
    # Timestamps
    detected_at: datetime = Field(default_factory=datetime.utcnow)
    acknowledged_at: Optional[datetime] = None
    resolved_at: Optional[datetime] = None
    
    # Metadata
    metadata: Optional[Dict[str, Any]] = None
    
    class Config:
        use_enum_values = True


class RiskEventCreate(BaseModel):
    member_id: str
    org_id: str
    tier: RiskTier
    score: float
    factors: List[RiskFactor]
    explanation_text: str
    suggested_actions: Optional[List[str]] = []


class RiskEventUpdate(BaseModel):
    status: Optional[str] = None
    assignee_id: Optional[str] = None
    caregiver_notes: Optional[str] = None


class RiskEventResponse(BaseModel):
    id: str
    member_id: str
    tier: RiskTier
    score: float
    explanation_text: str
    status: str
    detected_at: datetime
