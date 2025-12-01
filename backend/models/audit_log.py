from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum
import uuid


class AuditAction(str, Enum):
    # Auth
    LOGIN = "login"
    LOGOUT = "logout"
    PASSWORD_RESET = "password_reset"
    
    # Data access
    VIEW_MEMBER = "view_member"
    VIEW_METRICS = "view_metrics"
    VIEW_ALERT = "view_alert"
    
    # Data modification
    CREATE_MEMBER = "create_member"
    UPDATE_MEMBER = "update_member"
    DELETE_MEMBER = "delete_member"
    
    # Consent
    GRANT_CONSENT = "grant_consent"
    REVOKE_CONSENT = "revoke_consent"
    
    # Alerts
    ACKNOWLEDGE_ALERT = "acknowledge_alert"
    RESOLVE_ALERT = "resolve_alert"
    
    # Data export
    EXPORT_DATA = "export_data"
    DELETE_DATA = "delete_data"


class AuditLog(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    
    # Actor
    user_id: Optional[str] = None
    user_email: Optional[str] = None
    user_role: Optional[str] = None
    
    # Action
    action: AuditAction
    resource_type: Optional[str] = None  # "member", "alert", "metric"
    resource_id: Optional[str] = None
    
    # Context
    org_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    
    # Details
    details: Optional[Dict[str, Any]] = None
    success: bool = True
    error_message: Optional[str] = None
    
    # Timestamp
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    
    class Config:
        use_enum_values = True
