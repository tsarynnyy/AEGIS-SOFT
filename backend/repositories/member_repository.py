from .base import BaseRepository
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List, Dict, Any


class MemberRepository(BaseRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'members')
    
    async def find_by_user_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Find member by user ID"""
        return await self.find_one({'user_id': user_id})
    
    async def find_by_org(self, org_id: str, limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
        """Find all members in an organization"""
        return await self.find_many({'org_id': org_id}, limit=limit, skip=skip)
    
    async def pause_data_sharing(self, member_id: str, paused_until: Any) -> bool:
        """Pause data sharing for member"""
        result = await self.collection.update_one(
            {'id': member_id},
            {'$set': {'data_sharing_paused_until': paused_until}}
        )
        return result.modified_count > 0
