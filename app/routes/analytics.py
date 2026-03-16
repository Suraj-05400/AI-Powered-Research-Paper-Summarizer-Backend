from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Dict, Any
from datetime import datetime, timedelta
from app.database import get_db
from app.models import User, ResearchPaper, QAQuestion
from app.utils.auth import get_current_active_user
from app.schemas.schemas import UserAnalytics

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/user", response_model=UserAnalytics)
async def get_user_analytics(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user analytics"""
    
    # Total papers
    total_papers = db.query(func.count(ResearchPaper.id)).filter(
        ResearchPaper.user_id == current_user.id
    ).scalar() or 0
    
    # Total words processed
    total_words = db.query(func.sum(ResearchPaper.word_count)).filter(
        ResearchPaper.user_id == current_user.id
    ).scalar() or 0
    
    # Total QA questions
    total_qa_questions = db.query(func.count(QAQuestion.id)).join(
        QAQuestion.session
    ).filter(
        ResearchPaper.user_id == current_user.id
    ).count()
    
    # Average processing time
    avg_processing_time = db.query(func.avg(ResearchPaper.processing_time)).filter(
        ResearchPaper.user_id == current_user.id
    ).scalar() or 0
    
    # Papers by month (last 6 months)
    papers_by_month = {}
    for i in range(6):
        month_date = datetime.now() - timedelta(days=30*i)
        month_key = month_date.strftime("%B %Y")
        
        count = db.query(func.count(ResearchPaper.id)).filter(
            ResearchPaper.user_id == current_user.id,
            func.extract('month', ResearchPaper.uploaded_at) == month_date.month,
            func.extract('year', ResearchPaper.uploaded_at) == month_date.year
        ).scalar() or 0
        
        papers_by_month[month_key] = count
    
    return UserAnalytics(
        total_papers=total_papers,
        total_words_processed=int(total_words),
        total_qa_questions=total_qa_questions,
        average_processing_time=float(avg_processing_time),
        papers_by_month=papers_by_month
    )

@router.get("/paper/{paper_id}")
async def get_paper_analytics(
    paper_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get analytics for a specific paper"""
    
    paper = db.query(ResearchPaper).filter(
        ResearchPaper.id == paper_id,
        ResearchPaper.user_id == current_user.id
    ).first()
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    # QA questions for this paper
    qa_count = db.query(func.count(QAQuestion.id)).join(
        __import__('app.models', fromlist=['QASession']).QASession
    ).filter(
        __import__('app.models', fromlist=['QASession']).QASession.paper_id == paper_id
    ).scalar() or 0
    
    return {
        "paper_id": paper_id,
        "title": paper.title,
        "word_count": paper.word_count,
        "chunk_count": paper.chunks_count,
        "processing_time": paper.processing_time,
        "file_size": paper.memory_used,
        "qa_questions": qa_count,
        "uploaded_at": paper.uploaded_at,
        "processed_at": paper.processed_at
    }

@router.get("/history")
async def get_history(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get user's paper processing history"""
    
    papers = db.query(ResearchPaper).filter(
        ResearchPaper.user_id == current_user.id
    ).order_by(ResearchPaper.uploaded_at.desc()).all()
    
    history = []
    for paper in papers:
        history.append({
            "id": paper.id,
            "title": paper.title,
            "uploaded_at": paper.uploaded_at,
            "processed_at": paper.processed_at,
            "word_count": paper.word_count,
            "processing_time": paper.processing_time,
            "file_size": paper.memory_used
        })
    
    return history
