from fastapi import FastAPI, HTTPException, Header, Depends
from fastapi.responses import HTMLResponse, FileResponse
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, Numeric, DateTime, Date
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from datetime import datetime, date
from typing import Optional
import decimal

# --- Database Setup ---
# Using SQLite: It's a file-based DB, perfect for time-boxed assessments while still being a "real" DB.
SQLALCHEMY_DATABASE_URL = "sqlite:///./expenses.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ExpenseModel(Base):
    __tablename__ = "expenses"
    id = Column(Integer, primary_key=True, index=True)
    amount = Column(Numeric(10, 2), nullable=False) # STRICT REQUIREMENT: Decimal for money
    category = Column(String, index=True, nullable=False)
    description = Column(String, nullable=False)
    date = Column(Date, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    idempotency_key = Column(String, unique=True, index=True, nullable=True) # STRICT REQUIREMENT: Handle retries

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fenmo Expense API")

# --- Pydantic Schemas ---
class ExpenseCreate(BaseModel):
    amount: decimal.Decimal
    category: str
    description: str
    date: date

class ExpenseOut(BaseModel):
    id: int
    amount: decimal.Decimal
    category: str
    description: str
    date: date
    created_at: datetime
    
    class Config:
        from_attributes = True

# --- Database Dependency ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# --- Routes ---

# 1. Serve the Frontend UI
@app.get("/", response_class=HTMLResponse)
def serve_frontend():
    return FileResponse("index.html")

# 2. Create Expense (POST)
@app.post("/expenses", response_model=ExpenseOut)
def create_expense(
    expense: ExpenseCreate, 
    db: Session = Depends(get_db), 
    idempotency_key: Optional[str] = Header(None)
):
    # Edge Case: Prevent negative money amounts
    if expense.amount < 0:
        raise HTTPException(status_code=400, detail="Amount cannot be negative")

    # Edge Case: Handle network retries safely
    if idempotency_key:
        existing = db.query(ExpenseModel).filter(ExpenseModel.idempotency_key == idempotency_key).first()
        if existing:
            return existing # Safely return the already-created resource instead of duplicating it
            
    db_expense = ExpenseModel(
        amount=expense.amount,
        category=expense.category,
        description=expense.description,
        date=expense.date,
        idempotency_key=idempotency_key
    )
    db.add(db_expense)
    db.commit()
    db.refresh(db_expense)
    return db_expense

# 3. Get Expenses (GET)
@app.get("/expenses", response_model=list[ExpenseOut])
def get_expenses(
    category: Optional[str] = None, 
    sort: Optional[str] = None, 
    db: Session = Depends(get_db)
):
    query = db.query(ExpenseModel)
    
    if category:
        query = query.filter(ExpenseModel.category == category)
        
    if sort == "date_desc":
        query = query.order_by(ExpenseModel.date.desc())
        
    return query.all()

import os
import uvicorn

if __name__ == "__main__":
    # Get the port Render provides, or default to 8000 locally
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)