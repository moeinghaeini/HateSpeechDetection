"""
Text preprocessing utilities for hate speech detection.
"""

import re
import string
import pandas as pd
from typing import List, Dict, Any, Optional, Callable
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer, WordNetLemmatizer
from loguru import logger


class TextPreprocessor:
    """Text preprocessing pipeline for hate speech detection."""
    
    def __init__(self, 
                 remove_urls: bool = True,
                 remove_mentions: bool = True,
                 remove_hashtags: bool = False,
                 remove_numbers: bool = False,
                 remove_punctuation: bool = False,
                 lowercase: bool = True,
                 remove_stopwords: bool = False,
                 stem_words: bool = False,
                 lemmatize_words: bool = False,
                 min_length: int = 3,
                 max_length: int = 512):
        """
        Initialize text preprocessor.
        
        Args:
            remove_urls: Whether to remove URLs
            remove_mentions: Whether to remove @mentions
            remove_hashtags: Whether to remove #hashtags
            remove_numbers: Whether to remove numbers
            remove_punctuation: Whether to remove punctuation
            lowercase: Whether to convert to lowercase
            remove_stopwords: Whether to remove stopwords
            stem_words: Whether to stem words
            lemmatize_words: Whether to lemmatize words
            min_length: Minimum text length
            max_length: Maximum text length
        """
        self.remove_urls = remove_urls
        self.remove_mentions = remove_mentions
        self.remove_hashtags = remove_hashtags
        self.remove_numbers = remove_numbers
        self.remove_punctuation = remove_punctuation
        self.lowercase = lowercase
        self.remove_stopwords = remove_stopwords
        self.stem_words = stem_words
        self.lemmatize_words = lemmatize_words
        self.min_length = min_length
        self.max_length = max_length
        
        # Initialize NLTK components
        self._setup_nltk()
        
        # Initialize stemmer and lemmatizer
        if self.stem_words:
            self.stemmer = PorterStemmer()
        if self.lemmatize_words:
            self.lemmatizer = WordNetLemmatizer()
        
        logger.info("Text preprocessor initialized")
    
    def _setup_nltk(self) -> None:
        """Setup NLTK resources."""
        try:
            nltk.data.find('tokenizers/punkt')
        except LookupError:
            nltk.download('punkt')
        
        try:
            nltk.data.find('corpora/stopwords')
        except LookupError:
            nltk.download('stopwords')
        
        try:
            nltk.data.find('corpora/wordnet')
        except LookupError:
            nltk.download('wordnet')
        
        self.stop_words = set(stopwords.words('english'))
    
    def preprocess(self, text: str) -> str:
        """
        Preprocess a single text.
        
        Args:
            text: Input text to preprocess
            
        Returns:
            Preprocessed text
        """
        if pd.isna(text) or text is None:
            return ""
        
        text = str(text).strip()
        
        # Remove URLs
        if self.remove_urls:
            text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove mentions
        if self.remove_mentions:
            text = re.sub(r'@\w+', '', text)
        
        # Remove hashtags
        if self.remove_hashtags:
            text = re.sub(r'#\w+', '', text)
        
        # Remove numbers
        if self.remove_numbers:
            text = re.sub(r'\d+', '', text)
        
        # Convert to lowercase
        if self.lowercase:
            text = text.lower()
        
        # Remove punctuation
        if self.remove_punctuation:
            text = text.translate(str.maketrans('', '', string.punctuation))
        
        # Tokenize and process words
        if self.remove_stopwords or self.stem_words or self.lemmatize_words:
            tokens = word_tokenize(text)
            
            # Remove stopwords
            if self.remove_stopwords:
                tokens = [token for token in tokens if token.lower() not in self.stop_words]
            
            # Stem words
            if self.stem_words:
                tokens = [self.stemmer.stem(token) for token in tokens]
            
            # Lemmatize words
            if self.lemmatize_words:
                tokens = [self.lemmatizer.lemmatize(token) for token in tokens]
            
            text = ' '.join(tokens)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Filter by length
        if len(text) < self.min_length:
            return ""
        if len(text) > self.max_length:
            text = text[:self.max_length]
        
        return text
    
    def preprocess_batch(self, texts: List[str]) -> List[str]:
        """
        Preprocess a batch of texts.
        
        Args:
            texts: List of texts to preprocess
            
        Returns:
            List of preprocessed texts
        """
        return [self.preprocess(text) for text in texts]
    
    def preprocess_dataframe(self, df: pd.DataFrame, text_column: str, 
                            output_column: Optional[str] = None) -> pd.DataFrame:
        """
        Preprocess texts in a DataFrame.
        
        Args:
            df: Input DataFrame
            text_column: Name of the text column
            output_column: Name of the output column (defaults to text_column)
            
        Returns:
            DataFrame with preprocessed texts
        """
        if output_column is None:
            output_column = text_column
        
        df = df.copy()
        df[output_column] = df[text_column].apply(self.preprocess)
        
        # Remove empty texts
        df = df[df[output_column].str.len() > 0]
        
        logger.info(f"Preprocessed {len(df)} texts")
        return df
    
    def get_preprocessing_stats(self, original_texts: List[str], 
                               preprocessed_texts: List[str]) -> Dict[str, Any]:
        """
        Get statistics about preprocessing.
        
        Args:
            original_texts: Original texts
            preprocessed_texts: Preprocessed texts
            
        Returns:
            Dictionary with preprocessing statistics
        """
        original_lengths = [len(text.split()) for text in original_texts]
        preprocessed_lengths = [len(text.split()) for text in preprocessed_texts]
        
        stats = {
            'original_avg_length': sum(original_lengths) / len(original_lengths),
            'preprocessed_avg_length': sum(preprocessed_lengths) / len(preprocessed_lengths),
            'original_min_length': min(original_lengths),
            'preprocessed_min_length': min(preprocessed_lengths),
            'original_max_length': max(original_lengths),
            'preprocessed_max_length': max(preprocessed_lengths),
            'empty_texts_removed': len(original_texts) - len(preprocessed_texts),
            'length_reduction_ratio': (sum(original_lengths) - sum(preprocessed_lengths)) / sum(original_lengths)
        }
        
        return stats


class AdvancedTextPreprocessor(TextPreprocessor):
    """Advanced text preprocessor with additional features."""
    
    def __init__(self, **kwargs):
        """Initialize advanced preprocessor."""
        super().__init__(**kwargs)
        self.contraction_mapping = self._load_contractions()
        self.slang_mapping = self._load_slang()
    
    def _load_contractions(self) -> Dict[str, str]:
        """Load contraction mappings."""
        return {
            "don't": "do not",
            "won't": "will not",
            "can't": "cannot",
            "n't": " not",
            "'re": " are",
            "'s": " is",
            "'d": " would",
            "'ll": " will",
            "'t": " not",
            "'ve": " have",
            "'m": " am"
        }
    
    def _load_slang(self) -> Dict[str, str]:
        """Load slang mappings."""
        return {
            "lol": "laugh out loud",
            "omg": "oh my god",
            "wtf": "what the fuck",
            "fyi": "for your information",
            "btw": "by the way",
            "imo": "in my opinion",
            "tbh": "to be honest"
        }
    
    def expand_contractions(self, text: str) -> str:
        """Expand contractions in text."""
        for contraction, expansion in self.contraction_mapping.items():
            text = text.replace(contraction, expansion)
        return text
    
    def replace_slang(self, text: str) -> str:
        """Replace slang with full forms."""
        for slang, full_form in self.slang_mapping.items():
            text = re.sub(r'\b' + slang + r'\b', full_form, text, flags=re.IGNORECASE)
        return text
    
    def preprocess(self, text: str) -> str:
        """Advanced preprocessing with contractions and slang expansion."""
        # First do basic preprocessing
        text = super().preprocess(text)
        
        # Expand contractions
        text = self.expand_contractions(text)
        
        # Replace slang
        text = self.replace_slang(text)
        
        return text
