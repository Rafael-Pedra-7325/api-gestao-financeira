from pydantic import BaseModel, Field
from datetime import datetime

class AccountCreate(BaseModel):
    owner_name: str = Field(..., min_length=3, max_length=100)
    document: str = Field(..., min_length=11, max_length=14)
    password: str = Field(..., min_length=6)

class AccountResponse(BaseModel):
    id: str
    owner_name: str
    document: str
    balance: float
    created_at: datetime

    class Config:
        from_attributes = True
