from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from datetime import datetime

# 1. The User Table
class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True) # "index" makes searching faster
    hashed_password: str

    # Relationship: One User has Many Transactions
    transactions: List["Transaction"] = Relationship(back_populates="owner")

# 2. The Transaction Table
class Transaction(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    amount: float
    category: str
    type: str
    date: datetime = Field(default_factory=datetime.utcnow)
    
    # Foreign Key: Links this transaction to a specific User ID
    owner_id: Optional[int] = Field(default=None, foreign_key="user.id")
    
    # Relationship: Link back to the User object
    owner: Optional[User] = Relationship(back_populates="transactions")