from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import nltk
import os
import logging

from app.database import init_db
from app.config import settings
from app.utils.helpers import setup_logging, create_upload_directory
from app.routes import auth, papers, qa, search, analytics, translation
from app.database import init_db

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

nltk_data_path = os.path.join(os.getcwd(), "nltk_data")
if nltk_data_path not in nltk.data.path:
    nltk.data.path.append(nltk_data_path)

# Create FastAPI app
app = FastAPI(
    title="AI Research Paper Analyzer",
    description="AI-powered research paper analyzer with RAG, summarization, and semantic search",
    version="1.0.0"
)

# CORS middleware - production safe
cors_origins = [
    "https://researchpaperpro.netlify.app",
    "http://localhost:3000",
    "http://localhost:5173",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5174",
]

# Add production origins from environment if set
if settings.ENVIRONMENT == "production":
    prod_origin = os.getenv("FRONTEND_URL", "").strip()
    if prod_origin:
        cors_origins.append(prod_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,#{"*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Research Paper Project Backend is running with SQLite!"}

# Initialize database
init_db()
create_upload_directory()

# Include routers
app.include_router(auth.router)
app.include_router(papers.router)
app.include_router(qa.router)
app.include_router(search.router)
app.include_router(analytics.router)
app.include_router(translation.router)

'''async def root():
    """Root endpoint"""
    return {
        "message": "AI Research Paper Analyzer API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }'''

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
