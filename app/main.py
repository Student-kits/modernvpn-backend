from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import auth as auth_router
from app.routes import users as users_router
from app.routes import vpn as vpn_router
from app.routes import ads as ads_router
from app.database import engine
from app.models import Base

app = FastAPI(title="ModernVPN Control Plane")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    # create DB tables (simple approach for dev)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app.include_router(auth_router.router)
app.include_router(users_router.router)
app.include_router(vpn_router.router)
app.include_router(ads_router.router)

@app.get("/health")
async def health():
    return {"status": "ok"}