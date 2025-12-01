from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from enum import Enum
import uuid


class UserRole(str, Enum):
    MEMBER = "member"
    CAREGIVER = "caregiver"
    ORG_ADMIN = "org_admin"
    CARE_MANAGER = "care_manager"
    ANALYST = "analyst"


class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    email: EmailStr
    hashed_password: Optional[str] = None  # None for OAuth users
    role: UserRole
    org_id: Optional[str] = None
    
    # OAuth fields
    oauth_provider: Optional[str] = None  # "apple", "google"
    oauth_sub: Optional[str] = None
    
    # Profile
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None
    
    # Security
    is_active: bool = True
    is_verified: bool = False
    verification_token: Optional[str] = None
    reset_token: Optional[str] = None
    reset_token_expires: Optional[datetime] = None
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None
    
    class Config:
        use_enum_values = True


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    role: UserRole
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    org_id: Optional[str] = None


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    role: UserRole
    first_name: Optional[str]
    last_name: Optional[str]
    is_active: bool
    is_verified: bool
    created_at: datetime
