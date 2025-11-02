from fastapi import APIRouter, Depends, HTTPException
from app.schemas import UserCreate, UserOut
from app.database import get_db
from app.models import User
from sqlalchemy.future import select
from app.auth import get_password_hash

router = APIRouter(prefix='/users')

@router.get('/me', response_model=UserOut)
async def me(current=Depends(lambda: {"id": 1, "email": "demo@localhost"})):
    # placeholder for demo; replace with get_current_user in prod
    return {"id": 1, "email": "demo@localhost", "is_admin": True}

@router.post('/create', response_model=UserOut)
async def create_user(user_in: UserCreate, db=Depends(get_db)):
    q = await db.execute(select(User).filter(User.email == user_in.email))
    if q.scalars().first():
        raise HTTPException(status_code=400, detail='User exists')
    hashed = get_password_hash(user_in.password)
    user = User(email=user_in.email, hashed_password=hashed)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user