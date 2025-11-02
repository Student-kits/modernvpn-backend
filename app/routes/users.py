from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.schemas import UserCreate, UserOut
from app.database import get_db
from app.models import User
from app.auth import get_password_hash
from app.routes.auth import get_current_user

router = APIRouter(prefix='/users')

@router.get('/me', response_model=UserOut)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """Get current authenticated user information"""
    return UserOut(
        id=current_user.id,
        email=current_user.email,
        is_admin=current_user.is_admin,
        created_at=current_user.created_at
    )

@router.post('/create', response_model=UserOut)
async def create_user(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Create new user account (public endpoint)"""
    try:
        # Check if user already exists
        result = await db.execute(select(User).filter(User.email == user_in.email))
        if result.scalars().first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='User with this email already exists'
            )
        
        # Create new user
        hashed_password = get_password_hash(user_in.password)
        new_user = User(
            email=user_in.email,
            hashed_password=hashed_password,
            is_admin=False
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        return UserOut(
            id=new_user.id,
            email=new_user.email,
            is_admin=new_user.is_admin,
            created_at=new_user.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user account"
        )

@router.get('/profile')
async def get_user_profile(current_user: User = Depends(get_current_user)):
    """Get detailed user profile with VPN usage stats"""
    try:
        # In a real implementation, you'd fetch VPN usage statistics
        profile_data = {
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "is_admin": current_user.is_admin,
                "created_at": current_user.created_at
            },
            "vpn_stats": {
                "total_connections": 0,
                "data_used_mb": 0,
                "active_configs": 0,
                "last_connection": None
            },
            "account_status": "active"
        }
        
        return profile_data
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to fetch user profile"
        )