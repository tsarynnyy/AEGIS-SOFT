from .base import BaseRepository
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict, Any


class ConsentRepository(BaseRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'consents')
    
    async def find_by_member(self, member_id: str) -> List[Dict[str, Any]]:
        """Find all consents for a member"""
        cursor = self.collection.find({'member_id': member_id}).sort('granted_at', -1)
        docs = await cursor.to_list(length=100)
        for doc in docs:
            doc.pop('_id', None)
        return docs
    
    async def find_active_consent(
        self,
        member_id: str,
        consent_type: str
    ) -> Dict[str, Any]:
        """Find active consent of specific type"""
        doc = await self.collection.find_one({
            'member_id': member_id,
            'consent_type': consent_type,
            'granted': True,
            'revoked_at': None
        })
        if doc:
            doc.pop('_id', None)
        return doc
