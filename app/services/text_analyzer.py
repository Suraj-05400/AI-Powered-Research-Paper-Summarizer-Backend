import logging
from typing import List, Dict, Any
import re
import nltk
from nltk.tokenize import sent_tokenize
from nltk.corpus import stopwords
from collections import Counter

logger = logging.getLogger(__name__)

# Download required NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/stopwords')
except LookupError:
    nltk.download('stopwords')

class TextAnalyzer:
    """Analyze text to extract key findings, topics, and insights"""
    
    def __init__(self):
        self.stop_words = set(stopwords.words('english'))
    
    def extract_key_findings(self, text: str, num_findings: int = 5) -> List[str]:
        """Extract key findings from text"""
        try:
            # Split into sentences
            sentences = sent_tokenize(text)
            
            # Calculate sentence importance scores
            word_freq = self._calculate_word_frequency(text)
            
            sentence_scores = {}
            for i, sent in enumerate(sentences):
                words = sent.lower().split()
                score = sum(word_freq.get(word, 0) for word in words)
                sentence_scores[i] = score
            
            # Get top sentences as key findings
            top_sentences = sorted(sentence_scores.items(), key=lambda x: x[1], reverse=True)[:num_findings]
            findings = [sentences[idx] for idx, _ in sorted(top_sentences, key=lambda x: x[0])]
            
            return [f.strip() for f in findings if f.strip()]
        except Exception as e:
            logger.error(f"Error extracting key findings: {e}")
            return []
    
    def _calculate_word_frequency(self, text: str) -> Dict[str, int]:
        """Calculate word frequency in text"""
        words = text.lower().split()
        words = [word.strip('.,!?;:"\'-') for word in words if word.strip('.,!?;:"\'-')]
        words = [word for word in words if word not in self.stop_words and len(word) > 3]
        
        return dict(Counter(words).most_common(50))
    
    def extract_topics(self, text: str) -> List[Dict[str, Any]]:
        """Extract potential topics from text"""
        try:
            word_freq = self._calculate_word_frequency(text)
            
            # Create topics from top words with their frequencies
            topics = []
            for word, freq in list(word_freq.items())[:10]:
                topics.append({
                    "topic": word,
                    "frequency": freq,
                    "importance": min(freq / max(word_freq.values()), 1.0) if word_freq else 0
                })
            
            return topics
        except Exception as e:
            logger.error(f"Error extracting topics: {e}")
            return []
    
    def generate_insights(self, text: str, summary: str) -> List[str]:
        """Generate insights from text and summary"""
        try:
            insights = []
            
            # Insight 1: Length analysis
            word_count = len(text.split())
            if word_count > 10000:
                insights.append(f"Comprehensive research document with {word_count:,} words")
            elif word_count > 5000:
                insights.append(f"Detailed research paper with {word_count:,} words")
            else:
                insights.append(f"Concise research document with {word_count:,} words")
            
            # Insight 2: Content density
            sentences = sent_tokenize(text)
            avg_sentence_length = word_count / len(sentences) if sentences else 0
            if avg_sentence_length > 30:
                insights.append("Complex writing with detailed explanations")
            else:
                insights.append("Clear and concise writing style")
            
            # Insight 3: Summary compression
            summary_words = len(summary.split())
            compression_ratio = summary_words / word_count if word_count > 0 else 0
            compression_percent = (1 - compression_ratio) * 100
            insights.append(f"Summary compressed to {compression_percent:.1f}% of original length")
            
            # Insight 4: Unique vocabulary
            unique_words = len(set(word.lower() for word in text.split()))
            vocabulary_ratio = unique_words / word_count if word_count > 0 else 0
            insights.append(f"Vocabulary diversity: {vocabulary_ratio:.1%} unique words")
            
            return insights
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return []
    
    def get_word_frequency(self, text: str, top_n: int = 20) -> Dict[str, int]:
        """Get word frequency distribution"""
        return dict(self._calculate_word_frequency(text))
