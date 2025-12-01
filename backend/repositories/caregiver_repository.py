from .base import BaseRepository
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict, Any


class CaregiverRepository(BaseRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'caregivers')
    
    async def find_by_user_id(self, user_id: str) -> Dict[str, Any]:
        """Find caregiver by user ID"""
        return await self.find_one({'user_id': user_id})


class CaregiverMemberRepository(BaseRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'caregiver_members')
    
    async def find_by_member(self, member_id: str) -> List[Dict[str, Any]]:
        """Find all caregivers for a member"""
        return await self.find_many({'member_id': member_id})
    
    async def find_by_caregiver(self, caregiver_id: str) -> List[Dict[str, Any]]:
        """Find all members for a caregiver"""
        return await self.find_many({'caregiver_id': caregiver_id})
    
    async def find_relationship(self, member_id: str, caregiver_id: str) -> Dict[str, Any]:
        """Find specific member-caregiver relationship"""
        return await self.find_one({
            'member_id': member_id,
            'caregiver_id': caregiver_id
        })
    
    async def accept_invitation(self, relationship_id: str) -> bool:
        """Accept a caregiver invitation"""
        from datetime import datetime
        result = await self.collection.update_one(
            {'id': relationship_id},
            {'$set': {
                'invitation_status': 'accepted',
                'accepted_at': datetime.utcnow()
            }}
        )
        return result.modified_count > 0
