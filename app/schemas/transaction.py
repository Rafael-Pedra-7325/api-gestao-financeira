from pydantic import BaseModel, Field
from datetime import datetime
from app.db.models import TransactionType

class DepositRequest(BaseModel):
    amount: float = Field(..., gt=0)

class TransferRequest(BaseModel):
    to_account_id: str
    amount: float = Field(..., gt=0)

class TransactionResponse(BaseModel):
    id: str
    amount: float
    type: TransactionType
    timestamp: datetime
    related_account_id: str | None = None

    class Config:
        from_attributes = True
