# This file makes the models directory a Python package
from app.models.models import (
    User, ResearchPaper, PaperChunk, QASession, QAQuestion,
    SummaryDownload, SearchHistory
)

__all__ = [
    "User", "ResearchPaper", "PaperChunk", "QASession", "QAQuestion",
    "SummaryDownload", "SearchHistory"
]
