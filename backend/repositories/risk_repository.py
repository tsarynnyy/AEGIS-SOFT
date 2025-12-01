from .base import BaseRepository
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict, Any
from datetime import datetime


class RiskRepository(BaseRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'risk_events')
    
    async def create_indexes(self):
        """Create indexes for alert queries"""
        await self.collection.create_index([('member_id', 1), ('detected_at', -1)])
        await self.collection.create_index([('org_id', 1), ('status', 1), ('detected_at', -1)])
        await self.collection.create_index([('status', 1), ('tier', 1)])
    
    async def find_by_member(
        self,
        member_id: str,
        limit: int = 50,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """Find risk events for a member"""
        cursor = self.collection.find({'member_id': member_id}).sort('detected_at', -1).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        for doc in docs:
            doc.pop('_id', None)
        return docs
    
    async def find_by_org_and_status(
        self,
        org_id: str,
        status: str = None,
        tier: str = None,
        limit: int = 100,
        skip: int = 0
    ) -> List[Dict[str, Any]]:
        """Find risk events by organization, optionally filtered"""
        query = {'org_id': org_id}
        if status:
            query['status'] = status
        if tier:
            query['tier'] = tier
        
        cursor = self.collection.find(query).sort('detected_at', -1).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        for doc in docs:
            doc.pop('_id', None)
        return docs
    
    async def get_latest_by_member(self, member_id: str) -> Dict[str, Any]:
        """Get latest risk event for a member"""
        cursor = self.collection.find({'member_id': member_id}).sort('detected_at', -1).limit(1)
        docs = await cursor.to_list(length=1)
        if docs:
            docs[0].pop('_id', None)
            return docs[0]
        return None
