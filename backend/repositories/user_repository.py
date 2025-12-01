from .base import BaseRepository
from motor.motor_asyncio import AsyncIOMotorDatabase
from typing import Optional, Dict, Any


class UserRepository(BaseRepository):
    def __init__(self, db: AsyncIOMotorDatabase):
        super().__init__(db, 'users')
    
    async def find_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Find user by email"""
        return await self.find_one({'email': email})
    
    async def find_by_oauth(self, provider: str, oauth_sub: str) -> Optional[Dict[str, Any]]:
        """Find user by OAuth provider and subject"""
        return await self.find_one({
            'oauth_provider': provider,
            'oauth_sub': oauth_sub
        })
    
    async def find_by_reset_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Find user by password reset token"""
        return await self.find_one({'reset_token': token})
    
    async def verify_email(self, user_id: str) -> bool:
        """Mark user email as verified"""
        result = await self.collection.update_one(
            {'id': user_id},
            {'$set': {'is_verified': True, 'verification_token': None}}
        )
        return result.modified_count > 0
