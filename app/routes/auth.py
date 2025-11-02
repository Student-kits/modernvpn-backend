from fastapi import APIRouter

router = APIRouter(prefix='/auth')

@router.post('/login')
async def login():
    # TODO: Implement authentication
    return {'access_token': 'demo_token', 'token_type': 'bearer'}

@router.post('/register')
async def register():
    # TODO: Implement user registration
    return {'message': 'User registered'}