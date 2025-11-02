from fastapi import APIRouter, Depends
from app.auth import get_current_user

router = APIRouter(prefix='/admin')

@router.get('/stats')
async def stats(current=Depends(get_current_user)):
    # placeholder — implement admin checks and real stats
    return {'active_users': 123, 'servers': []}