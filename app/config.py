from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    HETZNER_API_TOKEN: str = ""
    WG_BASE_DIR: str = '/etc/wireguard'
    WG_LISTEN_PORT: int = 51820
    ADMIN_EMAIL: str = 'admin@localhost'

    class Config:
        env_file = '.env'

settings = Settings()