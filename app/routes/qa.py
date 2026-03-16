from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, ResearchPaper, QASession, QAQuestion
from app.schemas.schemas import QAQuestionResponse, QASessionResponse, QAQuestionCreate
from app.utils.auth import get_current_active_user
from app.services.qa_service import QAService

router = APIRouter(prefix="/api/qa", tags=["question-answering"])

# Services will be initialized lazily when needed

@router.post("/{paper_id}/sessions", response_model=QASessionResponse)
async def create_qa_session(
    paper_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new Q&A session for a paper"""
    
    # Verify paper exists and belongs to user
    paper = db.query(ResearchPaper).filter(
        ResearchPaper.id == paper_id,
        ResearchPaper.user_id == current_user.id
    ).first()
    
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found"
        )
    
    # Create new session
    session = QASession(
        user_id=current_user.id,
        paper_id=paper_id
    )
    
    db.add(session)
    db.commit()
    db.refresh(session)
    
    return session

@router.post("/{paper_id}/sessions/{session_id}/ask", response_model=QAQuestionResponse)
async def ask_question(
    paper_id: int,
    session_id: int,
    question_data: QAQuestionCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Ask a question about a paper"""
    
    # Verify session exists and belongs to user
    session = db.query(QASession).filter(
        QASession.id == session_id,
        QASession.user_id == current_user.id,
        QASession.paper_id == paper_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Get paper and chunks
    paper = db.query(ResearchPaper).filter(ResearchPaper.id == paper_id).first()
    chunks = db.query(__import__('app.models', fromlist=['PaperChunk']).PaperChunk).filter(
        __import__('app.models', fromlist=['PaperChunk']).PaperChunk.paper_id == paper_id
    ).all()
    
    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Paper has no processed chunks"
        )
    
    # Initialize QA service (lazy load)
    qa_service = QAService()
    
    # Setup QA system
    chunk_texts = [chunk.content for chunk in chunks]
    qa_service.setup_qa_system(chunk_texts)
    
    # Get answer
    answer, confidence, relevant_chunk_indices = qa_service.answer_question(
        question_data.question,
        top_k=5
    )
    
    # Save question and answer
    question = QAQuestion(
        session_id=session_id,
        question=question_data.question,
        answer=answer,
        confidence_score=confidence,
        relevant_chunks=relevant_chunk_indices
    )
    
    db.add(question)
    db.commit()
    db.refresh(question)
    
    return question

@router.get("/{paper_id}/sessions/{session_id}", response_model=QASessionResponse)
async def get_session_questions(
    paper_id: int,
    session_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all questions in a Q&A session"""
    
    session = db.query(QASession).filter(
        QASession.id == session_id,
        QASession.user_id == current_user.id,
        QASession.paper_id == paper_id
    ).first()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return session

@router.get("/{paper_id}/sessions")
async def get_paper_sessions(
    paper_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all Q&A sessions for a paper"""
    
    sessions = db.query(QASession).filter(
        QASession.paper_id == paper_id,
        QASession.user_id == current_user.id
    ).order_by(QASession.created_at.desc()).all()
    
    return sessions
