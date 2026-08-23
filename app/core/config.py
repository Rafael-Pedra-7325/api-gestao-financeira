import os

class Settings:
    SECRET_KEY: str = os.getenv("SECRET_KEY", "sua_chave_secreta_super_segura_aqui")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./sistema_financeiro.db")

settings = Settings()
