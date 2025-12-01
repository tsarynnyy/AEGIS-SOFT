from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, List, Dict, Any, TypeVar, Generic
from datetime import datetime

T = TypeVar('T')


class BaseRepository(Generic[T]):
    """
    Base repository with MongoDB abstraction.
    This pattern allows future migration to PostgreSQL without changing business logic.
    """
    
    def __init__(self, db: AsyncIOMotorDatabase, collection_name: str):
        self.db = db
        self.collection = db[collection_name]
    
    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new document"""
        result = await self.collection.insert_one(data)
        data['_id'] = str(result.inserted_id)
        return data
    
    async def find_by_id(self, id: str) -> Optional[Dict[str, Any]]:
        """Find document by ID"""
        doc = await self.collection.find_one({'id': id})
        if doc:
            doc.pop('_id', None)
        return doc
    
    async def find_one(self, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find one document matching query"""
        doc = await self.collection.find_one(query)
        if doc:
            doc.pop('_id', None)
        return doc
    
    async def find_many(self, query: Dict[str, Any], limit: int = 100, skip: int = 0) -> List[Dict[str, Any]]:
        """Find multiple documents"""
        cursor = self.collection.find(query).skip(skip).limit(limit)
        docs = await cursor.to_list(length=limit)
        for doc in docs:
            doc.pop('_id', None)
        return docs
    
    async def update(self, id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Update document by ID"""
        data['updated_at'] = datetime.utcnow()
        result = await self.collection.update_one(
            {'id': id},
            {'$set': data}
        )
        if result.modified_count:
            return await self.find_by_id(id)
        return None
    
    async def delete(self, id: str) -> bool:
        """Delete document by ID"""
        result = await self.collection.delete_one({'id': id})
        return result.deleted_count > 0
    
    async def count(self, query: Dict[str, Any] = {}) -> int:
        """Count documents matching query"""
        return await self.collection.count_documents(query)
