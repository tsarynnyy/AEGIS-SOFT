from .base import BaseRepository
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import List, Dict, Any
from datetime import datetime


class MetricRepository(BaseRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'metric_samples')
    
    async def create_indexes(self):
        """Create indexes for efficient time-series queries"""
        await self.collection.create_index([('member_id', 1), ('type', 1), ('timestamp', -1)])
        await self.collection.create_index([('member_id', 1), ('timestamp', -1)])
    
    async def find_by_member_and_type(
        self,
        member_id: str,
        metric_type: str,
        start_date: datetime,
        end_date: datetime,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Find metrics for a member by type and date range"""
        query = {
            'member_id': member_id,
            'type': metric_type,
            'timestamp': {'$gte': start_date, '$lte': end_date}
        }
        cursor = self.collection.find(query).sort('timestamp', -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        for doc in docs:
            doc.pop('_id', None)
        return docs
    
    async def find_by_member(
        self,
        member_id: str,
        start_date: datetime,
        end_date: datetime,
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """Find all metrics for a member in date range"""
        query = {
            'member_id': member_id,
            'timestamp': {'$gte': start_date, '$lte': end_date}
        }
        cursor = self.collection.find(query).sort('timestamp', -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        for doc in docs:
            doc.pop('_id', None)
        return docs
    
    async def get_latest_by_type(
        self,
        member_id: str,
        metric_type: str,
        limit: int = 1
    ) -> List[Dict[str, Any]]:
        """Get latest metrics of a specific type"""
        query = {'member_id': member_id, 'type': metric_type}
        cursor = self.collection.find(query).sort('timestamp', -1).limit(limit)
        docs = await cursor.to_list(length=limit)
        for doc in docs:
            doc.pop('_id', None)
        return docs
    
    async def bulk_create(self, samples: List[Dict[str, Any]]) -> int:
        """Bulk insert metric samples"""
        if not samples:
            return 0
        result = await self.collection.insert_many(samples)
        return len(result.inserted_ids)
