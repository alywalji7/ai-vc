import os
from datetime import datetime
from typing import List, Optional
import csv
import io
from fastapi import FastAPI, HTTPException, Depends, Query, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session

# Database Connection
DB_URL = os.environ.get("DATABASE_URL")
if not DB_URL:
    raise Exception("No DATABASE_URL environment variable found")

engine = create_engine(DB_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Models
class BetaFeedback(Base):
    __tablename__ = "beta_feedback"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    sentiment = Column(String)  # positive, neutral, negative
    message = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

class LP(Base):
    __tablename__ = "limited_partners"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)
    organization = Column(String, nullable=True)
    status = Column(String, default="PENDING_BETA")  # PENDING_BETA, ACTIVE, INACTIVE
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Founder(Base):
    __tablename__ = "founders"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    name = Column(String, nullable=True)
    company_name = Column(String, nullable=True)
    deck_url = Column(String, nullable=True)
    status = Column(String, default="PENDING_REVIEW")  # PENDING_REVIEW, ACTIVE, REJECTED
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

# Create tables
Base.metadata.create_all(bind=engine)

# Pydantic Models
class FeedbackCreate(BaseModel):
    user_id: str
    sentiment: str
    message: str

class FeedbackResponse(BaseModel):
    id: int
    user_id: str
    sentiment: str
    message: str
    created_at: datetime
    
    class Config:
        orm_mode = True

class LPCreate(BaseModel):
    email: str
    name: Optional[str] = None
    organization: Optional[str] = None

class FounderCreate(BaseModel):
    email: str
    name: Optional[str] = None
    company_name: Optional[str] = None
    deck_url: Optional[str] = None

# Database Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize FastAPI
app = FastAPI(title="Beta Feedback API")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this to specific domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
@app.post("/feedback", response_model=FeedbackResponse)
def create_feedback(feedback: FeedbackCreate, db: Session = Depends(get_db)):
    db_feedback = BetaFeedback(**feedback.dict())
    db.add(db_feedback)
    db.commit()
    db.refresh(db_feedback)
    return db_feedback

@app.get("/feedback", response_model=List[FeedbackResponse])
def get_all_feedback(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    feedbacks = db.query(BetaFeedback).offset(skip).limit(limit).all()
    return feedbacks

@app.get("/feedback/export")
def export_feedback(
    format: str = Query("csv", description="Export format (csv only for now)"),
    db: Session = Depends(get_db)
):
    feedbacks = db.query(BetaFeedback).all()
    
    if format.lower() == "csv":
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow(["id", "user_id", "sentiment", "message", "created_at"])
        
        # Write data
        for feedback in feedbacks:
            writer.writerow([
                feedback.id,
                feedback.user_id,
                feedback.sentiment,
                feedback.message,
                feedback.created_at
            ])
            
        response = Response(content=output.getvalue())
        response.headers["Content-Disposition"] = "attachment; filename=feedback_export.csv"
        response.headers["Content-Type"] = "text/csv"
        return response
    else:
        raise HTTPException(status_code=400, detail="Unsupported export format")

@app.get("/lps", response_model=List)
def get_all_lps(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    lps = db.query(LP).offset(skip).limit(limit).all()
    return lps

@app.get("/founders", response_model=List)
def get_all_founders(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    founders = db.query(Founder).offset(skip).limit(limit).all()
    return founders

@app.post("/lp", response_model=dict)
def create_lp(lp: LPCreate, db: Session = Depends(get_db)):
    # Check if LP with this email already exists
    db_lp = db.query(LP).filter(LP.email == lp.email).first()
    if db_lp:
        return {"status": "exists", "message": "LP with this email already exists"}
    
    # Create new LP
    new_lp = LP(**lp.dict())
    db.add(new_lp)
    db.commit()
    db.refresh(new_lp)
    return {"status": "success", "message": "LP created successfully", "id": new_lp.id}

@app.post("/founder", response_model=dict)
def create_founder(founder: FounderCreate, db: Session = Depends(get_db)):
    # Check if founder with this email already exists
    db_founder = db.query(Founder).filter(Founder.email == founder.email).first()
    if db_founder:
        return {"status": "exists", "message": "Founder with this email already exists"}
    
    # Create new founder
    new_founder = Founder(**founder.dict())
    db.add(new_founder)
    db.commit()
    db.refresh(new_founder)
    return {"status": "success", "message": "Founder created successfully", "id": new_founder.id}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8200)