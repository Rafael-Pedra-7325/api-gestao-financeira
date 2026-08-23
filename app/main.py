from fastapi import FastAPI
from app.db.database import engine, Base
from app.api import accounts, auth

# Cria as tabelas automaticamente
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="API RESTful de Gestão Financeira",
    description="API robusta com transações ACID, bloqueio pessimista e segurança JWT.",
    version="2.0.0"
)

# Registra as rotas
app.include_router(auth.router)
app.include_router(accounts.router)

@app.get("/")
def root():
    return {"message": "API Financeira rodando com sucesso! Acesse /docs para interagir."}
