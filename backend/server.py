from fastapi import FastAPI, APIRouter, Depends, HTTPException, Header, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

# Import models
from models import (
    User, UserCreate, UserLogin, UserResponse, UserRole,
    Member, MemberCreate, MemberResponse,
    MetricSample, MetricSampleCreate, MetricSampleBulkCreate, MetricType,
    RiskEvent, RiskEventCreate, RiskEventResponse, RiskEventUpdate, RiskTier,
    Consent, ConsentCreate, ConsentType,
    DeviceAccount, DeviceAccountCreate
)

# Import repositories
from repositories import (
    UserRepository, MemberRepository, MetricRepository,
    RiskRepository, ConsentRepository, DeviceRepository
)

# Import services
from services import AuthService, MemberService, MetricService, RiskService

# Import additional models
from models import Caregiver, CaregiverCreate, CaregiverInvite, CaregiverOnMember


ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize repositories
user_repo = UserRepository(db)
member_repo = MemberRepository(db)
metric_repo = MetricRepository(db)
risk_repo = RiskRepository(db)
consent_repo = ConsentRepository(db)
device_repo = DeviceRepository(db)

# Import caregiver repository
from repositories.caregiver_repository import CaregiverRepository, CaregiverMemberRepository
caregiver_repo = CaregiverRepository(db)
caregiver_member_repo = CaregiverMemberRepository(db)

# Initialize services
auth_service = AuthService(user_repo)
member_service = MemberService(member_repo, consent_repo)
metric_service = MetricService(metric_repo)
risk_service = RiskService(risk_repo, metric_repo)

# Create the main app
app = FastAPI(
    title="Aegis AI Wellness API",
    description="Proactive wellness monitoring platform API",
    version="1.0.0"
)

# Security
security = HTTPBearer()

# Create API router
api_router = APIRouter(prefix="/api")


# ==================== AUTH DEPENDENCY ====================

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> User:
    """Dependency to get current authenticated user"""
    token = credentials.credentials
    user = await auth_service.get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    return user


# ==================== AUTH ROUTES ====================

class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


@api_router.post("/auth/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def register(user_create: UserCreate):
    """Register a new user"""
    try:
        user, access_token, refresh_token = await auth_service.register_user(user_create)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse(**user.dict())
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.post("/auth/login", response_model=TokenResponse)
async def login(user_login: UserLogin):
    """Login with email and password"""
    try:
        user, access_token, refresh_token = await auth_service.login_user(user_login)
        return TokenResponse(
            access_token=access_token,
            refresh_token=refresh_token,
            user=UserResponse(**user.dict())
        )
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


class RefreshTokenRequest(BaseModel):
    refresh_token: str


@api_router.post("/auth/refresh")
async def refresh_token(request: RefreshTokenRequest):
    """Refresh access token"""
    try:
        access_token = await auth_service.refresh_access_token(request.refresh_token)
        return {"access_token": access_token, "token_type": "bearer"}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))


class PasswordResetRequest(BaseModel):
    email: str


@api_router.post("/auth/password-reset-request")
async def request_password_reset(request: PasswordResetRequest):
    """Request password reset (generates token)"""
    token = await auth_service.request_password_reset(request.email)
    # In production, send email with token
    return {"message": "If email exists, reset instructions will be sent", "token": token}


class PasswordResetConfirm(BaseModel):
    reset_token: str
    new_password: str


@api_router.post("/auth/password-reset-confirm")
async def confirm_password_reset(request: PasswordResetConfirm):
    """Reset password with token"""
    try:
        await auth_service.reset_password(request.reset_token, request.new_password)
        return {"message": "Password reset successful"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@api_router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return UserResponse(**current_user.dict())


# ==================== MEMBER ROUTES ====================

@api_router.post("/members", response_model=MemberResponse, status_code=status.HTTP_201_CREATED)
async def create_member(
    member_create: MemberCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new member profile"""
    member = await member_service.create_member(member_create)
    return MemberResponse(**member.dict())


@api_router.get("/members/me", response_model=MemberResponse)
async def get_my_member_profile(current_user: User = Depends(get_current_user)):
    """Get current user's member profile"""
    member = await member_service.get_member_by_user(current_user.id)
    if not member:
        raise HTTPException(status_code=404, detail="Member profile not found")
    return MemberResponse(**member.dict())


@api_router.get("/members/{member_id}", response_model=MemberResponse)
async def get_member(
    member_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get member by ID"""
    member = await member_service.get_member(member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    return MemberResponse(**member.dict())


@api_router.patch("/members/{member_id}")
async def update_member(
    member_id: str,
    updates: dict,
    current_user: User = Depends(get_current_user)
):
    """Update member profile"""
    # Validate member exists
    member = await member_service.get_member(member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Update member
    updated_member = await member_repo.update(member_id, updates)
    if not updated_member:
        raise HTTPException(status_code=400, detail="Update failed")
    
    return {"message": "Profile updated successfully", "member": updated_member}


@api_router.post("/members/{member_id}/pause-sharing")
async def pause_data_sharing(
    member_id: str,
    duration_hours: int = 24,
    current_user: User = Depends(get_current_user)
):
    """Pause data sharing temporarily"""
    from datetime import timedelta
    paused_until = datetime.utcnow() + timedelta(hours=duration_hours)
    
    await member_repo.update(member_id, {
        'data_sharing_paused_until': paused_until
    })
    
    return {
        "message": f"Data sharing paused for {duration_hours} hours",
        "paused_until": paused_until
    }


@api_router.post("/members/{member_id}/resume-sharing")
async def resume_data_sharing(
    member_id: str,
    current_user: User = Depends(get_current_user)
):
    """Resume data sharing"""
    await member_repo.update(member_id, {
        'data_sharing_paused_until': None
    })
    
    return {"message": "Data sharing resumed"}


@api_router.get("/members/{member_id}/export-data")
async def export_member_data(
    member_id: str,
    format: str = "json",
    current_user: User = Depends(get_current_user)
):
    """Export all member data (GDPR compliance)"""
    # Get member profile
    member = await member_service.get_member(member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    # Get all related data
    from datetime import timedelta
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=365)  # Last year
    
    metrics = await metric_repo.find_by_member(member_id, start_date, end_date, limit=10000)
    alerts = await risk_repo.find_by_member(member_id, limit=1000)
    consents = await consent_repo.find_by_member(member_id)
    devices = await device_repo.find_by_member(member_id)
    
    export_data = {
        "member_profile": member.dict(),
        "metrics": metrics,
        "alerts": alerts,
        "consents": consents,
        "devices": devices,
        "export_date": datetime.utcnow().isoformat(),
        "data_period": {
            "start": start_date.isoformat(),
            "end": end_date.isoformat()
        }
    }
    
    return export_data


@api_router.delete("/members/{member_id}/delete-account")
async def delete_member_account(
    member_id: str,
    confirmation: str,
    current_user: User = Depends(get_current_user)
):
    """Delete member account and all data"""
    if confirmation != "DELETE":
        raise HTTPException(status_code=400, detail="Confirmation required")
    
    # Delete member data
    await metric_repo.collection.delete_many({'member_id': member_id})
    await risk_repo.collection.delete_many({'member_id': member_id})
    await consent_repo.collection.delete_many({'member_id': member_id})
    await device_repo.collection.delete_many({'member_id': member_id})
    await caregiver_member_repo.collection.delete_many({'member_id': member_id})
    
    # Delete member profile
    await member_repo.delete(member_id)
    
    # Deactivate user
    await user_repo.update(current_user.id, {'is_active': False})
    
    return {"message": "Account deleted successfully"}


# ==================== CONSENT ROUTES ====================

@api_router.post("/members/{member_id}/consents", response_model=Consent)
async def grant_consent(
    member_id: str,
    consent_create: ConsentCreate,
    current_user: User = Depends(get_current_user)
):
    """Grant or revoke consent"""
    consent = await member_service.grant_consent(
        member_id,
        consent_create.consent_type,
        consent_create.granted,
        consent_create.source
    )
    return consent


@api_router.get("/members/{member_id}/consents", response_model=List[Consent])
async def get_member_consents(
    member_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get all consents for a member"""
    consents = await member_service.get_member_consents(member_id)
    return consents


# ==================== METRICS ROUTES ====================

@api_router.post("/metrics", response_model=MetricSample)
async def ingest_metric(
    sample_create: MetricSampleCreate,
    current_user: User = Depends(get_current_user)
):
    """Ingest a single metric sample"""
    sample = await metric_service.ingest_sample(sample_create)
    return sample


@api_router.post("/metrics/bulk")
async def ingest_metrics_bulk(
    bulk_create: MetricSampleBulkCreate,
    current_user: User = Depends(get_current_user)
):
    """Bulk ingest metric samples"""
    count = await metric_service.ingest_samples_bulk(bulk_create.samples)
    return {"ingested_count": count}


@api_router.get("/members/{member_id}/metrics", response_model=List[MetricSample])
async def get_member_metrics(
    member_id: str,
    metric_type: Optional[str] = None,
    days: int = 7,
    current_user: User = Depends(get_current_user)
):
    """Get metrics for a member"""
    metrics = await metric_service.get_member_metrics(member_id, metric_type, days)
    return metrics


# ==================== RISK/ALERTS ROUTES ====================

@api_router.post("/members/{member_id}/analyze-risk", response_model=RiskEvent)
async def analyze_member_risk(
    member_id: str,
    current_user: User = Depends(get_current_user)
):
    """Analyze member risk and create alert if needed"""
    # Get member to get org_id
    member = await member_service.get_member(member_id)
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    
    risk_event = await risk_service.analyze_member_risk(member_id, member.org_id)
    if not risk_event:
        raise HTTPException(status_code=200, detail="No risk detected, member is healthy")
    return risk_event


@api_router.get("/members/{member_id}/alerts", response_model=List[RiskEvent])
async def get_member_alerts(
    member_id: str,
    limit: int = 50,
    current_user: User = Depends(get_current_user)
):
    """Get risk events/alerts for a member"""
    alerts = await risk_service.get_member_alerts(member_id, limit)
    return alerts


@api_router.get("/members/{member_id}/current-risk", response_model=Optional[RiskEvent])
async def get_current_risk(
    member_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get latest risk status for a member"""
    risk = await risk_service.get_latest_member_risk(member_id)
    return risk


@api_router.patch("/alerts/{alert_id}", response_model=RiskEvent)
async def update_alert(
    alert_id: str,
    update: RiskEventUpdate,
    current_user: User = Depends(get_current_user)
):
    """Update alert status"""
    alert_data = await risk_repo.find_by_id(alert_id)
    if not alert_data:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    update_data = update.dict(exclude_unset=True)
    if update.status == "acknowledged" and "acknowledged_at" not in update_data:
        update_data["acknowledged_at"] = datetime.utcnow()
    if update.status == "resolved" and "resolved_at" not in update_data:
        update_data["resolved_at"] = datetime.utcnow()
    
    updated = await risk_repo.update(alert_id, update_data)
    return RiskEvent(**updated)


# ==================== DEVICE ROUTES ====================

@api_router.post("/devices", response_model=DeviceAccount)
async def connect_device(
    device_create: DeviceAccountCreate,
    current_user: User = Depends(get_current_user)
):
    """Connect a health device/data source"""
    device_data = device_create.dict()
    device_data['connected_at'] = datetime.utcnow()
    device_data['updated_at'] = datetime.utcnow()
    device_data['is_active'] = True
    
    created = await device_repo.create(device_data)
    return DeviceAccount(**created)


@api_router.get("/members/{member_id}/devices", response_model=List[DeviceAccount])
async def get_member_devices(
    member_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get all device accounts for a member"""
    devices = await device_repo.find_by_member(member_id)
    return [DeviceAccount(**d) for d in devices]


# ==================== CAREGIVER ROUTES ====================

@api_router.post("/members/{member_id}/caregivers/invite")
async def invite_caregiver(
    member_id: str,
    invite: CaregiverInvite,
    current_user: User = Depends(get_current_user)
):
    """Invite a caregiver for a member"""
    import uuid
    
    # Check if user already exists
    existing_user = await user_repo.find_by_email(invite.email)
    
    if existing_user:
        # User exists, create caregiver profile if doesn't exist
        caregiver_data = await caregiver_repo.find_by_user_id(existing_user['id'])
        if not caregiver_data:
            caregiver_data = {
                'id': str(uuid.uuid4()),
                'user_id': existing_user['id'],
                'first_name': invite.first_name,
                'last_name': invite.last_name,
                'relationship': invite.relationship,
                'created_at': datetime.utcnow(),
                'updated_at': datetime.utcnow()
            }
            caregiver_data = await caregiver_repo.create(caregiver_data)
        
        caregiver_id = caregiver_data['id']
    else:
        # Create new user and caregiver
        user_id = str(uuid.uuid4())
        user_data = {
            'id': user_id,
            'email': invite.email,
            'role': 'caregiver',
            'first_name': invite.first_name,
            'last_name': invite.last_name,
            'is_active': True,
            'is_verified': False,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        await user_repo.create(user_data)
        
        caregiver_id = str(uuid.uuid4())
        caregiver_data = {
            'id': caregiver_id,
            'user_id': user_id,
            'first_name': invite.first_name,
            'last_name': invite.last_name,
            'relationship': invite.relationship,
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        await caregiver_repo.create(caregiver_data)
    
    # Create relationship
    relationship_data = {
        'id': str(uuid.uuid4()),
        'member_id': member_id,
        'caregiver_id': caregiver_id,
        'can_view_alerts': True,
        'can_view_metrics': True,
        'can_add_notes': True,
        'invitation_status': 'pending',
        'invitation_sent_at': datetime.utcnow(),
        'created_at': datetime.utcnow()
    }
    relationship = await caregiver_member_repo.create(relationship_data)
    
    # TODO: Send email invitation
    
    return {
        "message": "Caregiver invitation sent",
        "caregiver_id": caregiver_id,
        "relationship_id": relationship['id']
    }


@api_router.get("/members/{member_id}/caregivers")
async def get_member_caregivers(
    member_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get all caregivers for a member"""
    relationships = await caregiver_member_repo.find_by_member(member_id)
    
    # Enrich with caregiver details
    enriched = []
    for rel in relationships:
        caregiver_data = await caregiver_repo.find_by_id(rel['caregiver_id'])
        if caregiver_data:
            enriched.append({
                **rel,
                'caregiver': caregiver_data
            })
    
    return enriched


@api_router.delete("/caregivers/{relationship_id}")
async def remove_caregiver(
    relationship_id: str,
    current_user: User = Depends(get_current_user)
):
    """Remove a caregiver from care circle"""
    success = await caregiver_member_repo.delete(relationship_id)
    if not success:
        raise HTTPException(status_code=404, detail="Caregiver relationship not found")
    return {"message": "Caregiver removed successfully"}


@api_router.post("/caregivers/{relationship_id}/accept")
async def accept_caregiver_invitation(
    relationship_id: str,
    current_user: User = Depends(get_current_user)
):
    """Accept a caregiver invitation"""
    success = await caregiver_member_repo.accept_invitation(relationship_id)
    if not success:
        raise HTTPException(status_code=404, detail="Invitation not found")
    return {"message": "Invitation accepted"}


# ==================== HEALTH CHECK ====================

@api_router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "service": "Aegis AI Wellness API"
    }


# Include router
app.include_router(api_router)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ==================== STARTUP/SHUTDOWN ====================

@app.on_event("startup")
async def startup_event():
    """Create indexes on startup"""
    logger.info("Creating database indexes...")
    await metric_repo.create_indexes()
    await risk_repo.create_indexes()
    logger.info("Aegis AI API started successfully")


@app.on_event("shutdown")
async def shutdown_db_client():
    """Close database connection"""
    client.close()
    logger.info("Database connection closed")
