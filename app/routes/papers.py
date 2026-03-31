from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
import os
import time
from pathlib import Path
from app.database import get_db
from app.models import User, ResearchPaper, PaperChunk
from app.schemas.schemas import (
    ResearchPaperResponse, ResearchPaperDetail, ResearchPaperMetadata
)
from app.utils.auth import get_current_active_user
from app.config import settings
from app.services.document_processor import DocumentProcessor
from app.services.summarization_service import SummarizationService
from app.services.text_analyzer import TextAnalyzer
from app.services.embedding_service import EmbeddingService
from app.services.pdf_generator import PDFGeneratorService

router = APIRouter(prefix="/api/papers", tags=["research papers"])

# Initialize document processor (lightweight service)
doc_processor = DocumentProcessor()
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status, BackgroundTasks
# ... (keep your other imports the same)

# --- NEW BACKGROUND WORKER FUNCTION ---
def perform_heavy_ai_tasks(paper_id: int, raw_text: str, chunks: list):
    """
    This function runs in the background. 
    It handles the heavy RAM-consuming tasks.
    """
    # Create a new standalone DB session for the background thread
    db = next(get_db())
    try:
        # 1. Generate summary (Moved from main route)
        summarizer = SummarizationService()
        summary = summarizer.summarize(raw_text, max_length=500)
        
        # 2. Extract key findings (Moved from main route)
        text_analyzer = TextAnalyzer()
        key_findings = text_analyzer.extract_key_findings(raw_text, num_findings=5)
        
        # 3. Create embeddings (Moved from main route)
        embedding_service = EmbeddingService()
        embedding_service.create_embeddings(chunks)

        # 4. Update the database record once AI is done
        paper = db.query(ResearchPaper).filter(ResearchPaper.id == paper_id).first()
        if paper:
            paper.summary = summary
            paper.key_findings = key_findings
            paper.summary_length = len(summary.split())
            db.commit()
            print(f"AI Processing complete for Paper ID: {paper_id}")
    except Exception as e:
        print(f"❌ Background Task Error: {e}")
    finally:
        db.close()

@router.post("/upload", response_model=ResearchPaperResponse)
async def upload_paper(
    background_tasks: BackgroundTasks, # <-- ADDED THIS
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    try:
        # --- PHASE 1: FILE VALIDATION & SAVING (KEEP THIS) ---
        is_valid, message = doc_processor.validate_file(file.filename, file.size)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
        
        os.makedirs(settings.UPLOAD_DIRECTORY, exist_ok=True)
        file_extension = Path(file.filename).suffix.lower()
        unique_filename = f"{current_user.id}_{int(time.time())}{file_extension}"
        file_path = os.path.join(settings.UPLOAD_DIRECTORY, unique_filename)
        
        with open(file_path, "wb") as f:
            contents = await file.read()
            f.write(contents)
        
        # --- PHASE 2: TEXT EXTRACTION (FAST) ---
        raw_text = doc_processor.extract_text(file_path)
        word_count = doc_processor.get_word_count(raw_text)
        chunks = doc_processor.chunk_text(raw_text, chunk_size=500)
        
        # -------------------------------------------------------
        # COMMENTED OUT PREVIOUS SLOW CODE (Caused 502 Errors)
        # -------------------------------------------------------
        # summarizer = SummarizationService()
        # summary = summarizer.summarize(raw_text, max_length=500)
        # text_analyzer = TextAnalyzer()
        # key_findings = text_analyzer.extract_key_findings(raw_text, num_findings=5)
        # embedding_service = EmbeddingService()
        # embedding_service.create_embeddings(chunks)
        # -------------------------------------------------------

        # --- PHASE 3: QUICK DB SAVE (STUB DATA) ---
        paper = ResearchPaper(
            user_id=current_user.id,
            title=Path(file.filename).stem,
            original_filename=file.filename,
            file_path=file_path,
            file_size=file.size,
            file_type=file_extension.lstrip('.'),
            raw_content=raw_text,
            word_count=word_count,
            chunks_count=len(chunks),
            chunk_size=500,
            memory_used=file.size / (1024 * 1024),
            processing_time=0.0,
            summary="Analyzing...", # Default text while AI runs
            key_findings=[],       # Empty list while AI runs
            extra_metadata={}
        )
        
        db.add(paper)
        db.flush() # Get the paper ID

        # Save chunks quickly
        for idx, chunk in enumerate(chunks):
            db.add(PaperChunk(paper_id=paper.id, chunk_index=idx, content=chunk))
        
        db.commit()
        db.refresh(paper)

        # --- PHASE 4: TRIGGER BACKGROUND AI ---
        # This sends the 200/202 response to the user immediately!
        background_tasks.add_task(perform_heavy_ai_tasks, paper.id, raw_text, chunks)
        
        return paper

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))
        
'''def process_paper_ai(paper_id: int, file_path: str, db: Session):
    try:
        # Extract text, create embeddings, and generate summary here
        # This now runs IN THE BACKGROUND
        summarization_service.generate_summary(paper_id, file_path, db)
    except Exception as e:
        print(f"Background Task Error: {e}")

@router.post("/upload", response_model=ResearchPaperResponse)
async def upload_paper(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload and process a research paper"""
    
    try:
        # Validate file
        is_valid, message = doc_processor.validate_file(file.filename, file.size)
        if not is_valid:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
        
        # Create upload directory if doesn't exist
        os.makedirs(settings.UPLOAD_DIRECTORY, exist_ok=True)
        
        # Save file
        file_extension = Path(file.filename).suffix.lower()
        unique_filename = f"{current_user.id}_{int(time.time())}{file_extension}"
        file_path = os.path.join(settings.UPLOAD_DIRECTORY, unique_filename)
        
        with open(file_path, "wb") as f:
            contents = await file.read()
            f.write(contents)
        
        # Extract text from document
        start_time = time.time()
        raw_text = doc_processor.extract_text(file_path)
        word_count = doc_processor.get_word_count(raw_text)
        
        # Create chunks
        chunks = doc_processor.chunk_text(raw_text, chunk_size=500)
        
        # Generate summary (lazy load)
        summarizer = SummarizationService()
        summary = summarizer.summarize(raw_text, max_length=500)
        
        # Extract key findings (lazy load)
        text_analyzer = TextAnalyzer()
        key_findings = text_analyzer.extract_key_findings(raw_text, num_findings=5)
        
        # Create embeddings for chunks (lazy load)
        embedding_service = EmbeddingService()
        embedding_service.create_embeddings(chunks)
        
        processing_time = time.time() - start_time
        metadata = doc_processor.get_metadata(file_path, file.size, processing_time, len(chunks))
        
        # Save to database
        paper = ResearchPaper(
            user_id=current_user.id,
            title=Path(file.filename).stem,
            original_filename=file.filename,
            file_path=file_path,
            file_size=file.size,
            file_type=file_extension.lstrip('.'),
            raw_content=raw_text,
            word_count=word_count,
            chunks_count=len(chunks),
            chunk_size=500,
            memory_used=file.size / (1024 * 1024),
            processing_time=processing_time,
            summary=summary,
            summary_length=len(summary.split()),
            key_findings=key_findings,
            extra_metadata=metadata
        )
        
        db.add(paper)
        db.flush()  # Flush to generate paper ID
        
        # Save chunks
        for idx, chunk in enumerate(chunks):
            paper_chunk = PaperChunk(
                paper_id=paper.id,
                chunk_index=idx,
                content=chunk
            )
            db.add(paper_chunk)
        
        db.commit()
        db.refresh(paper)
        
        return paper
    
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}"
        )
'''
@router.get("/", response_model=List[ResearchPaperResponse])
async def get_user_papers(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all papers uploaded by current user"""
    papers = db.query(ResearchPaper).filter(
        ResearchPaper.user_id == current_user.id
    ).order_by(ResearchPaper.uploaded_at.desc()).all()
    
    return papers

@router.get("/{paper_id}", response_model=ResearchPaperDetail)
async def get_paper_detail(
    paper_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get detailed information about a paper"""
    paper = db.query(ResearchPaper).filter(
        ResearchPaper.id == paper_id,
        ResearchPaper.user_id == current_user.id
    ).first()
    
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found"
        )
    
    return paper

@router.delete("/{paper_id}")
async def delete_paper(
    paper_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a paper"""
    paper = db.query(ResearchPaper).filter(
        ResearchPaper.id == paper_id,
        ResearchPaper.user_id == current_user.id
    ).first()
    
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found"
        )
    
    # Delete file
    if os.path.exists(paper.file_path):
        os.remove(paper.file_path)
    
    # Delete from database (chunks will be deleted due to cascade)
    db.delete(paper)
    db.commit()
    
    return {"message": "Paper deleted successfully"}

@router.get("/{paper_id}/download-summary")
async def download_summary_pdf(
    paper_id: int,
    language: str = "en",
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Download summary as PDF"""
    paper = db.query(ResearchPaper).filter(
        ResearchPaper.id == paper_id,
        ResearchPaper.user_id == current_user.id
    ).first()
    
    if not paper:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Paper not found"
        )
    
    try:
        # Generate PDF (lazy load)
        pdf_generator = PDFGeneratorService()
        pdf_path = pdf_generator.generate_summary_pdf(
            title=paper.title,
            summary=paper.summary,
            metadata={
                "file_size_mb": paper.memory_used,
                "words": paper.word_count,
                "processing_time": paper.processing_time,
                "chunks_count": paper.chunks_count
            },
            key_findings=paper.key_findings,
            user_id=current_user.id,
            paper_id=paper_id
        )
        
        return FileResponse(
            pdf_path,
            media_type="application/pdf",
            filename=f"{paper.title}_{language}_summary.pdf"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating PDF: {str(e)}"
        )
