from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, ResearchPaper
from app.utils.auth import get_current_active_user
from app.services.translation_service import TranslationService

router = APIRouter(prefix="/api/translation", tags=["translation"])

@router.get("/languages")
async def get_supported_languages():
    """Get list of supported languages"""
    translation_service = TranslationService()
    return translation_service.get_supported_languages()

@router.post("/paper/{paper_id}/summary")
async def translate_summary(
    paper_id: int,
    target_language: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Translate paper summary to target language"""
    
    paper = db.query(ResearchPaper).filter(
        ResearchPaper.id == paper_id,
        ResearchPaper.user_id == current_user.id
    ).first()
    
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    
    if not paper.summary:
        raise HTTPException(status_code=400, detail="Paper has no summary")
    
    try:
        translation_service = TranslationService()
        translated_summary = translation_service.translate(
            paper.summary,
            target_language
        )
        
        return {
            "original_summary": paper.summary,
            "translated_summary": translated_summary,
            "target_language": target_language
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")

@router.post("/text")
async def translate_text(
    text: str,
    target_language: str,
    current_user: User = Depends(get_current_active_user)
):
    """Translate arbitrary text"""
    
    try:
        translation_service = TranslationService()
        translated_text = translation_service.translate(text, target_language)
        
        return {
            "original_text": text,
            "translated_text": translated_text,
            "target_language": target_language
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Translation error: {str(e)}")
