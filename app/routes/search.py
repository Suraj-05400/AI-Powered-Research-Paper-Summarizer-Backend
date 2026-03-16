from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User, ResearchPaper, PaperChunk
from app.schemas.schemas import SemanticSearchQuery, SemanticSearchResponse, SemanticSearchResult
from app.utils.auth import get_current_active_user
import app.services.embedding_service as EmbeddingService  # type: ignore

router = APIRouter(prefix="/api/search", tags=["search"])

@router.post("/semantic", response_model=SemanticSearchResponse)
async def semantic_search(
    query: SemanticSearchQuery,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Perform semantic search across user's papers"""
    
    try:
        # Initialize embedding service (lazy load)
        embedding_service = EmbeddingService()
        
        # Get all user's papers
        papers = db.query(ResearchPaper).filter(
            ResearchPaper.user_id == current_user.id
        ).all()
        
        if not papers:
            return SemanticSearchResponse(results=[], total_results=0)
        
        results = []
        
        # Search in each paper
        for paper in papers:
            chunks = db.query(PaperChunk).filter(
                PaperChunk.paper_id == paper.id
            ).all()
            
            if not chunks:
                continue
            
            # Setup embedding service for this paper
            chunk_texts = [chunk.content for chunk in chunks]
            embeddings = embedding_service.create_embeddings(chunk_texts)
            index = embedding_service.build_faiss_index(embeddings)
            
            # Search
            search_results = embedding_service.search(
                query.query, index, chunk_texts, k=min(query.top_k, len(chunks))
            )
            
            # Format results
            for content, similarity, chunk_idx in search_results:
                results.append(SemanticSearchResult(
                    paper_id=paper.id,
                    paper_title=paper.title,
                    chunk_content=content,
                    similarity_score=float(similarity)
                ))
        
        # Sort by similarity and limit
        results.sort(key=lambda x: x.similarity_score, reverse=True)
        results = results[:query.top_k]
        
        return SemanticSearchResponse(
            results=results,
            total_results=len(results)
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Search error: {str(e)}"
        )

@router.post("/papers/{paper_id}")
async def search_in_paper(
    paper_id: int,
    query: SemanticSearchQuery,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Search within a specific paper"""
    
    try:
        # Verify paper exists and belongs to user
        paper = db.query(ResearchPaper).filter(
            ResearchPaper.id == paper_id,
            ResearchPaper.user_id == current_user.id
        ).first()
        
        if not paper:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        # Get chunks
        chunks = db.query(PaperChunk).filter(
            PaperChunk.paper_id == paper_id
        ).all()
        
        if not chunks:
            return SemanticSearchResponse(results=[], total_results=0)
        
        # Initialize embedding service (lazy load)
        embedding_service = EmbeddingService()
        
        # Setup and search
        chunk_texts = [chunk.content for chunk in chunks]
        embeddings = embedding_service.create_embeddings(chunk_texts)
        index = embedding_service.build_faiss_index(embeddings)
        
        search_results = embedding_service.search(
            query.query, index, chunk_texts, k=min(query.top_k, len(chunks))
        )
        
        # Format results
        results = [
            SemanticSearchResult(
                paper_id=paper_id,
                paper_title=paper.title,
                chunk_content=content,
                similarity_score=float(similarity)
            )
            for content, similarity, _ in search_results
        ]
        
        return SemanticSearchResponse(
            results=results,
            total_results=len(results)
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")
