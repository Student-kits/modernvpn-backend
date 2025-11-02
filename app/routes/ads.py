from fastapi import APIRouter, Depends
from app.models import AdEvent
from app.database import get_db

router = APIRouter(prefix='/ads')

@router.post('/event')
async def ad_event(payload: dict, db=Depends(get_db)):
    # payload expected: {user_id, event_type, metadata}
    ev = AdEvent(
        user_id=payload.get('user_id'),
        event_type=payload.get('event_type'),
        metadata=payload.get('metadata', {})
    )
    db.add(ev)
    await db.commit()
    await db.refresh(ev)
    return {'ok': True}