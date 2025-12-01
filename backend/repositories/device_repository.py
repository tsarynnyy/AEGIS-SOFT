from .base import BaseRepository
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict, Any


class DeviceRepository(BaseRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'device_accounts')
    
    async def find_by_member(self, member_id: str) -> List[Dict[str, Any]]:
        """Find all device accounts for a member"""
        cursor = self.collection.find({'member_id': member_id})
        docs = await cursor.to_list(length=100)
        for doc in docs:
            doc.pop('_id', None)
        return docs
    
    async def find_active_devices(self, member_id: str) -> List[Dict[str, Any]]:
        """Find active device accounts for a member"""
        cursor = self.collection.find({'member_id': member_id, 'is_active': True})
        docs = await cursor.to_list(length=100)
        for doc in docs:
            doc.pop('_id', None)
        return docs
