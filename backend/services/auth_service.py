from typing import Optional, Dict, Any, Tuple
from datetime import datetime, timedelta
from repositories import UserRepository
from models import User, UserCreate, UserLogin, UserRole
from utils.security import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_verification_token,
    generate_reset_token
)
import uuid


class AuthService:
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo
    
    async def register_user(self, user_create: UserCreate) -> Tuple[User, str, str]:
        """
        Register a new user with email/password.
        Returns (user, access_token, refresh_token)
        """
        # Check if user already exists
        existing_user = await self.user_repo.find_by_email(user_create.email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Create user
        user_data = {
            'id': str(uuid.uuid4()),
            'email': user_create.email,
            'hashed_password': hash_password(user_create.password),
            'role': user_create.role,
            'first_name': user_create.first_name,
            'last_name': user_create.last_name,
            'org_id': user_create.org_id,
            'is_active': True,
            'is_verified': False,
            'verification_token': generate_verification_token(),
            'created_at': datetime.utcnow(),
            'updated_at': datetime.utcnow()
        }
        
        created_user = await self.user_repo.create(user_data)
        user = User(**created_user)
        
        # Generate tokens
        access_token = create_access_token({'sub': user.id, 'role': user.role})
        refresh_token = create_refresh_token({'sub': user.id})
        
        return user, access_token, refresh_token
    
    async def login_user(self, user_login: UserLogin) -> Tuple[User, str, str]:
        """
        Login user with email/password.
        Returns (user, access_token, refresh_token)
        """
        # Find user
        user_data = await self.user_repo.find_by_email(user_login.email)
        if not user_data:
            raise ValueError("Invalid credentials")
        
        user = User(**user_data)
        
        # Verify password
        if not user.hashed_password or not verify_password(user_login.password, user.hashed_password):
            raise ValueError("Invalid credentials")
        
        # Check if user is active
        if not user.is_active:
            raise ValueError("User account is disabled")
        
        # Update last login
        await self.user_repo.update(user.id, {'last_login': datetime.utcnow()})
        
        # Generate tokens
        access_token = create_access_token({'sub': user.id, 'role': user.role})
        refresh_token = create_refresh_token({'sub': user.id})
        
        return user, access_token, refresh_token
    
    async def refresh_access_token(self, refresh_token: str) -> str:
        """
        Generate new access token from refresh token.
        """
        payload = decode_token(refresh_token)
        if not payload or payload.get('type') != 'refresh':
            raise ValueError("Invalid refresh token")
        
        user_id = payload.get('sub')
        user_data = await self.user_repo.find_by_id(user_id)
        if not user_data:
            raise ValueError("User not found")
        
        user = User(**user_data)
        access_token = create_access_token({'sub': user.id, 'role': user.role})
        return access_token
    
    async def request_password_reset(self, email: str) -> Optional[str]:
        """
        Generate password reset token for user.
        Returns reset token if user exists.
        """
        user_data = await self.user_repo.find_by_email(email)
        if not user_data:
            return None  # Don't reveal if user exists
        
        reset_token = generate_reset_token()
        reset_expires = datetime.utcnow() + timedelta(hours=1)
        
        await self.user_repo.update(user_data['id'], {
            'reset_token': reset_token,
            'reset_token_expires': reset_expires
        })
        
        return reset_token
    
    async def reset_password(self, reset_token: str, new_password: str) -> bool:
        """
        Reset user password with reset token.
        """
        user_data = await self.user_repo.find_by_reset_token(reset_token)
        if not user_data:
            raise ValueError("Invalid reset token")
        
        # Check if token is expired
        if user_data.get('reset_token_expires'):
            expires = user_data['reset_token_expires']
            if isinstance(expires, str):
                expires = datetime.fromisoformat(expires)
            if expires < datetime.utcnow():
                raise ValueError("Reset token has expired")
        
        # Update password
        await self.user_repo.update(user_data['id'], {
            'hashed_password': hash_password(new_password),
            'reset_token': None,
            'reset_token_expires': None
        })
        
        return True
    
    async def verify_email(self, verification_token: str) -> bool:
        """
        Verify user email with verification token.
        """
        user_data = await self.user_repo.find_one({'verification_token': verification_token})
        if not user_data:
            return False
        
        await self.user_repo.verify_email(user_data['id'])
        return True
    
    async def oauth_login(
        self,
        provider: str,
        oauth_sub: str,
        email: str,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None
    ) -> Tuple[User, str, str]:
        """
        Login or create user via OAuth (Apple/Google).
        Returns (user, access_token, refresh_token)
        """
        # Try to find existing OAuth user
        user_data = await self.user_repo.find_by_oauth(provider, oauth_sub)
        
        if not user_data:
            # Check if email exists (link accounts)
            user_data = await self.user_repo.find_by_email(email)
            
            if user_data:
                # Link OAuth to existing account
                await self.user_repo.update(user_data['id'], {
                    'oauth_provider': provider,
                    'oauth_sub': oauth_sub,
                    'is_verified': True  # OAuth emails are pre-verified
                })
            else:
                # Create new user
                user_data = {
                    'id': str(uuid.uuid4()),
                    'email': email,
                    'role': UserRole.MEMBER,  # Default role for OAuth
                    'oauth_provider': provider,
                    'oauth_sub': oauth_sub,
                    'first_name': first_name,
                    'last_name': last_name,
                    'is_active': True,
                    'is_verified': True,
                    'created_at': datetime.utcnow(),
                    'updated_at': datetime.utcnow()
                }
                user_data = await self.user_repo.create(user_data)
        
        user = User(**user_data)
        
        # Update last login
        await self.user_repo.update(user.id, {'last_login': datetime.utcnow()})
        
        # Generate tokens
        access_token = create_access_token({'sub': user.id, 'role': user.role})
        refresh_token = create_refresh_token({'sub': user.id})
        
        return user, access_token, refresh_token
    
    async def get_current_user(self, token: str) -> Optional[User]:
        """
        Get current user from access token.
        """
        payload = decode_token(token)
        if not payload or payload.get('type') != 'access':
            return None
        
        user_id = payload.get('sub')
        user_data = await self.user_repo.find_by_id(user_id)
        if not user_data:
            return None
        
        return User(**user_data)
