import logging
from typing import Optional
import os

logger = logging.getLogger(__name__)

class TranslationService:
    """Service for translating summaries to different languages"""
    
    SUPPORTED_LANGUAGES = {
        'en': 'English',
        'es': 'Spanish',
        'fr': 'French',
        'de': 'German',
        'it': 'Italian',
        'pt': 'Portuguese',
        'ru': 'Russian',
        'ja': 'Japanese',
        'ko': 'Korean',
        'zh': 'Chinese',
        'ar': 'Arabic',
        'hi': 'Hindi',
    }
    
    def __init__(self, use_google: bool = True):
        """Initialize translation service"""
        self.use_google = use_google
        self.translator = None
        
        if use_google:
            self._init_google_translator()
        else:
            self._init_fallback_translator()
    
    def _init_google_translator(self):
        """Initialize Google Translate API"""
        try:
            from google.cloud import translate_v2
            
            credentials_path = os.getenv("GOOGLE_TRANSLATE_CREDENTIALS_PATH")
            if credentials_path and os.path.exists(credentials_path):
                self.translator = translate_v2.Client.from_service_account_json(credentials_path)
                logger.info("Google Translate API initialized")
            else:
                logger.warning("Google credentials not found, falling back to alternative service")
                self._init_fallback_translator()
        except Exception as e:
            logger.warning(f"Could not initialize Google Translate: {e}")
            self._init_fallback_translator()
    
    def _init_fallback_translator(self):
        """Initialize fallback translator (deep_translator library)"""
        try:
            from deep_translator import GoogleTranslator
            self.translator = GoogleTranslator
            logger.info("Fallback translator (deep_translator) initialized")
        except Exception as e:
            logger.error(f"Could not initialize fallback translator: {e}")
    
    def translate(self, text: str, target_language: str) -> str:
        """Translate text to target language"""
        if target_language == 'en' or target_language == 'english':
            return text
        
        try:
            if isinstance(self.translator, type):  # fallback translator
                translator = self.translator(source_language='auto', target_language=target_language)
                return translator.translate(text)
            else:  # Google API
                result = self.translator.translate_text(
                    text,
                    target_language=target_language
                )
                return result.get('translatedText', text)
        except Exception as e:
            logger.error(f"Translation error for {target_language}: {e}")
            return text  # Return original text if translation fails
    
    def translate_to_language_code(self, text: str, language_code: str) -> str:
        """Translate to specific language using language code"""
        if language_code not in self.SUPPORTED_LANGUAGES:
            logger.warning(f"Language {language_code} not supported, returning original text")
            return text
        
        return self.translate(text, language_code)
    
    def get_supported_languages(self) -> dict:
        """Get list of supported languages"""
        return self.SUPPORTED_LANGUAGES
    
    def batch_translate(self, texts: list, target_language: str) -> list:
        """Translate multiple texts to target language"""
        return [self.translate(text, target_language) for text in texts]
