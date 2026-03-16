from sqlalchemy import Column, String, DateTime, Integer, Text, ForeignKey, Boolean, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from datetime import datetime
from app.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    phone_number = Column(String, unique=True, nullable=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Google OAuth
    google_id = Column(String, unique=True, nullable=True)
    
    # Relationships
    papers = relationship("ResearchPaper", back_populates="user", cascade="all, delete-orphan")
    qa_sessions = relationship("QASession", back_populates="user", cascade="all, delete-orphan")
    
class ResearchPaper(Base):
    __tablename__ = "research_papers"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String, nullable=False)
    original_filename = Column(String, nullable=False)
    file_path = Column(String, unique=True, nullable=False)
    file_size = Column(Integer)  # in bytes
    file_type = Column(String)  # pdf, docx, txt, etc
    
    # Content
    raw_content = Column(Text)
    word_count = Column(Integer)
    
    # Metadata
    chunks_count = Column(Integer)
    chunk_size = Column(Integer, default=500)
    memory_used = Column(Float)  # in MB
    processing_time = Column(Float)  # in seconds
    
    # Summary
    summary = Column(Text)
    summary_length = Column(Integer)
    
    # Key Findings
    key_findings = Column(JSON)  # List of key findings
    
    # Additional metadata JSON
    extra_metadata = Column(JSON)  # Additional metadata    
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="papers")
    chunks = relationship("PaperChunk", back_populates="paper", cascade="all, delete-orphan")
    qa_sessions = relationship("QASession", back_populates="paper", cascade="all, delete-orphan")

class PaperChunk(Base):
    __tablename__ = "paper_chunks"
    
    id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("research_papers.id"), nullable=False)
    chunk_index = Column(Integer)
    content = Column(Text, nullable=False)
    embedding = Column(String)  # FAISS vector stored as string
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    paper = relationship("ResearchPaper", back_populates="chunks")

class QASession(Base):
    __tablename__ = "qa_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    paper_id = Column(Integer, ForeignKey("research_papers.id"), nullable=False)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="qa_sessions")
    paper = relationship("ResearchPaper", back_populates="qa_sessions")
    questions = relationship("QAQuestion", back_populates="session", cascade="all, delete-orphan")

class QAQuestion(Base):
    __tablename__ = "qa_questions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("qa_sessions.id"), nullable=False)
    
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=True)
    confidence_score = Column(Float, default=0.0)
    relevant_chunks = Column(JSON)  # List of chunk IDs used for answer
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    session = relationship("QASession", back_populates="questions")

class SummaryDownload(Base):
    __tablename__ = "summary_downloads"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    paper_id = Column(Integer, ForeignKey("research_papers.id"))
    
    format = Column(String)  # pdf, docx, txt
    language = Column(String, default="en")
    file_path = Column(String)
    
    created_at = Column(DateTime, default=datetime.utcnow)

class SearchHistory(Base):
    __tablename__ = "search_history"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    paper_id = Column(Integer, ForeignKey("research_papers.id"), nullable=True)
    
    query = Column(Text, nullable=False)
    results_count = Column(Integer)
    
    created_at = Column(DateTime, default=datetime.utcnow)
