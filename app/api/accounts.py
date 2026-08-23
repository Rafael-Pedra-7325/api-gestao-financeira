from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db.database import get_db
from app.db.models import Account, Transaction, TransactionType
from app.schemas.account import AccountCreate, AccountResponse
from app.schemas.transaction import DepositRequest, TransferRequest, TransactionResponse
from app.core.security import get_password_hash, get_current_account_id

router = APIRouter(prefix="/accounts", tags=["Contas e Transações"])

@router.post("/", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
def create_account(account: AccountCreate, db: Session = Depends(get_db)):
    db_account = Account(
        owner_name=account.owner_name,
        document=account.document,
        hashed_password=get_password_hash(account.password),
        balance=0.0
    )
    try:
        db.add(db_account)
        db.commit()
        db.refresh(db_account)
        return db_account
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Documento (CPF/CNPJ) já cadastrado.")

@router.post("/{account_id}/deposit", response_model=TransactionResponse)
def make_deposit(account_id: str, deposit: DepositRequest, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).with_for_update().first()
    if not account:
        raise HTTPException(status_code=404, detail="Conta não encontrada.")

    account.balance += deposit.amount
    transaction = Transaction(account_id=account.id, amount=deposit.amount, type=TransactionType.DEPOSIT)
    
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

@router.post("/{account_id}/transfer", status_code=status.HTTP_200_OK)
def make_transfer(
    account_id: str, 
    transfer: TransferRequest, 
    db: Session = Depends(get_db),
    current_account_id: str = Depends(get_current_account_id)
):
    if account_id != current_account_id:
        raise HTTPException(status_code=403, detail="Você não tem permissão para operar nesta conta.")

    if account_id == transfer.to_account_id:
        raise HTTPException(status_code=400, detail="Não é possível transferir para a mesma conta.")

    try:
        from_account = db.query(Account).filter(Account.id == account_id).with_for_update().first()
        to_account = db.query(Account).filter(Account.id == transfer.to_account_id).with_for_update().first()

        if not from_account or not to_account:
            raise HTTPException(status_code=404, detail="Conta de origem ou destino não encontrada.")
        
        if from_account.balance < transfer.amount:
            raise HTTPException(status_code=400, detail="Saldo insuficiente.")

        from_account.balance -= transfer.amount
        to_account.balance += transfer.amount

        tx_out = Transaction(account_id=from_account.id, related_account_id=to_account.id, amount=transfer.amount, type=TransactionType.TRANSFER_OUT)
        tx_in = Transaction(account_id=to_account.id, related_account_id=from_account.id, amount=transfer.amount, type=TransactionType.TRANSFER_IN)

        db.add_all([tx_out, tx_in])
        db.commit()
        
        return {"message": "Transferência realizada com sucesso", "amount": transfer.amount, "transaction_id": tx_out.id}

    except HTTPException as he:
        db.rollback()
        raise he
    except Exception:
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno ao processar a transferência.")

@router.get("/{account_id}", response_model=AccountResponse)
def get_account(account_id: str, db: Session = Depends(get_db)):
    account = db.query(Account).filter(Account.id == account_id).first()
    if not account:
        raise HTTPException(status_code=404, detail="Conta não encontrada.")
    return account
