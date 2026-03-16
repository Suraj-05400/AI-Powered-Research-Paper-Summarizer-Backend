from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime

# ==================== User Schemas ====================
class UserRegister(BaseModel):
    email: EmailStr
    password: str
    confirm_password: str
    full_name: Optional[str] = None
    phone_number: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: Optional[str]
    phone_number: Optional[str]
    is_verified: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

# ==================== Research Paper Schemas ====================
class ResearchPaperMetadata(BaseModel):
    chunk_size: int
    chunks_count: int
    memory_used: float
    processing_time: float
    word_count: int
    file_size: int

class ResearchPaperSummary(BaseModel):
    id: int
    title: str
    summary: str
    summary_length: int
    key_findings: Optional[List[str]] = None
    metadata: ResearchPaperMetadata
    processed_at: datetime
    
    class Config:
        from_attributes = True

class ResearchPaperResponse(BaseModel):
    id: int
    title: str
    original_filename: str
    file_type: str
    word_count: int
    uploaded_at: datetime
    processed_at: Optional[datetime]
    summary: Optional[str]
    key_findings: Optional[List[str]]
    
    class Config:
        from_attributes = True

class ResearchPaperDetail(BaseModel):
    id: int
    title: str
    original_filename: str
    file_path: str
    file_type: str
    file_size: int
    word_count: int
    chunks_count: int
    chunk_size: int
    memory_used: float
    processing_time: float
    summary: str
    key_findings: Optional[List[str]]
    extra_metadata: Optional[Dict[str, Any]]
    uploaded_at: datetime
    processed_at: Optional[datetime]
    
    class Config:
        from_attributes = True

# ==================== Q&A Schemas ====================
class QAQuestionCreate(BaseModel):
    question: str

class QAQuestionResponse(BaseModel):
    id: int
    question: str
    answer: Optional[str]
    confidence_score: float
    created_at: datetime
    
    class Config:
        from_attributes = True

class QASessionResponse(BaseModel):
    id: int
    paper_id: int
    questions: List[QAQuestionResponse]
    created_at: datetime
    
    class Config:
        from_attributes = True

# ==================== Search Schemas ====================
class SemanticSearchQuery(BaseModel):
    query: str
    top_k: int = 5

class SemanticSearchResult(BaseModel):
    paper_id: int
    paper_title: str
    chunk_content: str
    similarity_score: float

class SemanticSearchResponse(BaseModel):
    results: List[SemanticSearchResult]
    total_results: int

# ==================== Download Schemas ====================
class SummaryDownloadRequest(BaseModel):
    format: str  # pdf, docx, txt
    language: str = "en"

class SummaryDownloadResponse(BaseModel):
    file_path: str
    format: str
    language: str
    created_at: datetime

# ==================== Analytics Schemas ====================
class UserAnalytics(BaseModel):
    total_papers: int
    total_words_processed: int
    total_qa_questions: int
    average_processing_time: float
    papers_by_month: Dict[str, int]

class InsightsData(BaseModel):
    key_findings: List[str]
    word_frequency: Dict[str, int]
    topics: List[Dict[str, Any]]
    insights: List[str]
    recommendations: List[str]
