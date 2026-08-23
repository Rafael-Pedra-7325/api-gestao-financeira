from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Account
from app.core.security import verify_password, create_access_token
from app.schemas.token import Token

router = APIRouter(tags=["Autenticação"])

@router.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == form_data.username).first()
    
    if not account or not verify_password(form_data.password, account.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="ID da conta ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = create_access_token(data={"sub": account.id})
    return {"access_token": access_token, "token_type": "bearer"}
