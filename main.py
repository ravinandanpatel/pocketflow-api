from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select
from typing import List
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext

# Import our own files
from database import create_db_and_tables, get_session
from models import Transaction, User

# -------------------------
# CONFIGURATION
# -------------------------
SECRET_KEY = "mysecretkey"  # In real life, keep this super secret!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Setup Security Tools
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI(title="PocketFlow API")

# -------------------------
# SECURITY FUNCTIONS
# -------------------------
def get_password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)):
    """The Bouncer: Checks if the user has a valid token."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.exec(select(User).where(User.username == username)).first()
    if user is None:
        raise credentials_exception
    return user

# -------------------------
# STARTUP
# -------------------------
@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# -------------------------
# AUTH ENDPOINTS
# -------------------------
@app.post("/register", response_model=User)
def register_user(user: User, db: Session = Depends(get_session)):
    # Check if user already exists
    existing_user = db.exec(select(User).where(User.username == user.username)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username already taken")
    
    # Hash the password and save
    hashed_pwd = get_password_hash(user.hashed_password)
    user.hashed_password = hashed_pwd
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@app.post("/token")
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_session)):
    user = db.exec(select(User).where(User.username == form_data.username)).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# -------------------------
# TRANSACTION ENDPOINTS (PROTECTED)
# -------------------------
@app.post("/transactions/", response_model=Transaction)
def create_transaction(
    transaction: Transaction, 
    current_user: User = Depends(get_current_user), # <--- NEW DEPENDENCY
    db: Session = Depends(get_session)
):
    # Link the transaction to the current logged-in user
    transaction.owner_id = current_user.id 
    db.add(transaction)
    db.commit()
    db.refresh(transaction)
    return transaction

@app.get("/transactions/", response_model=List[Transaction])
def read_transactions(
    current_user: User = Depends(get_current_user), # <--- NEW DEPENDENCY
    db: Session = Depends(get_session)
):
    # Only show transactions belonging to THIS user
    return db.exec(select(Transaction).where(Transaction.owner_id == current_user.id)).all()

@app.get("/analytics/balance")
def get_balance(current_user: User = Depends(get_current_user), db: Session = Depends(get_session)):
    transactions = db.exec(select(Transaction).where(Transaction.owner_id == current_user.id)).all()
    
    total_income = sum(t.amount for t in transactions if t.type == "income")
    total_expense = sum(t.amount for t in transactions if t.type == "expense")
    
    return {"current_balance": total_income - total_expense}

# -------------------------
# 5. DELETE TRANSACTION (SECURED)
# -------------------------
@app.delete("/transactions/{transaction_id}")
def delete_transaction(
    transaction_id: int, 
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_session)
):
    """Delete a transaction only if it belongs to the logged-in user."""
    # 1. Find the transaction that matches ID AND Owner
    transaction = db.exec(
        select(Transaction)
        .where(Transaction.id == transaction_id)
        .where(Transaction.owner_id == current_user.id)
    ).first()
    
    # 2. If not found, it means it doesn't exist OR you don't own it
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found or access denied")
    
    # 3. Delete it
    db.delete(transaction)
    db.commit()
    return {"message": "Transaction deleted successfully"}

# run using this "uvicorn main:app --reload"