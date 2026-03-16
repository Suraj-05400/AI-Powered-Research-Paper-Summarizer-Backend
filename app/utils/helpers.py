import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def setup_logging():
    """Setup application logging"""
    log_directory = "logs"
    if not os.path.exists(log_directory):
        os.makedirs(log_directory)
    
    log_file = os.path.join(log_directory, f"app_{datetime.now().strftime('%Y-%m-%d')}.log")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

def create_upload_directory():
    """Create upload directory if it doesn't exist"""
    from app.config import settings
    if not os.path.exists(settings.UPLOAD_DIRECTORY):
        os.makedirs(settings.UPLOAD_DIRECTORY)
        logger.info(f"Created upload directory: {settings.UPLOAD_DIRECTORY}")

def get_file_size_mb(file_size_bytes: int) -> float:
    """Convert file size from bytes to MB"""
    return round(file_size_bytes / (1024 * 1024), 2)

def validate_email(email: str) -> bool:
    """Validate email format"""
    import re
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
