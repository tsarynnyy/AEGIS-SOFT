from typing import Optional, List
from repositories import MemberRepository, ConsentRepository
from models import Member, MemberCreate, Consent, ConsentCreate, ConsentType
from datetime import datetime


class MemberService:
    def __init__(self, member_repo: MemberRepository, consent_repo: ConsentRepository):
        self.member_repo = member_repo
        self.consent_repo = consent_repo
    
    async def create_member(self, member_create: MemberCreate) -> Member:
        """
        Create a new member profile.
        """
        member_data = member_create.dict()
        member_data['created_at'] = datetime.utcnow()
        member_data['updated_at'] = datetime.utcnow()
        
        created = await self.member_repo.create(member_data)
        return Member(**created)
    
    async def get_member(self, member_id: str) -> Optional[Member]:
        """
        Get member by ID.
        """
        member_data = await self.member_repo.find_by_id(member_id)
        if not member_data:
            return None
        return Member(**member_data)
    
    async def get_member_by_user(self, user_id: str) -> Optional[Member]:
        """
        Get member by user ID.
        """
        member_data = await self.member_repo.find_by_user_id(user_id)
        if not member_data:
            return None
        return Member(**member_data)
    
    async def grant_consent(
        self,
        member_id: str,
        consent_type: ConsentType,
        granted: bool,
        source: Optional[str] = None
    ) -> Consent:
        """
        Grant or revoke consent.
        """
        consent_data = {
            'member_id': member_id,
            'consent_type': consent_type,
            'granted': granted,
            'source': source,
            'granted_at': datetime.utcnow()
        }
        
        created = await self.consent_repo.create(consent_data)
        return Consent(**created)
    
    async def get_member_consents(self, member_id: str) -> List[Consent]:
        """
        Get all consents for a member.
        """
        consents_data = await self.consent_repo.find_by_member(member_id)
        return [Consent(**c) for c in consents_data]
    
    async def has_consent(self, member_id: str, consent_type: ConsentType) -> bool:
        """
        Check if member has active consent of specific type.
        """
        consent = await self.consent_repo.find_active_consent(member_id, consent_type)
        return consent is not None
