"""
Tests for data utilities.
"""

import pytest
import pandas as pd
import numpy as np
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.data_utils import preprocess_text, split_dataset, get_class_weights
from src.data.dataset import HateSpeechDataset
from src.data.preprocessing import TextPreprocessor


class TestDataUtils:
    """Test cases for data utilities."""
    
    def test_preprocess_text(self):
        """Test text preprocessing."""
        # Test basic preprocessing
        text = "This is a test @user #hashtag http://example.com"
        processed = preprocess_text(text, remove_urls=True, remove_mentions=True, remove_hashtags=True)
        assert processed == "this is a test"
        
        # Test with None input
        assert preprocess_text(None) == ""
        assert preprocess_text("") == ""
    
    def test_split_dataset(self):
        """Test dataset splitting."""
        # Create test data
        df = pd.DataFrame({
            'text': ['text1', 'text2', 'text3', 'text4', 'text5'],
            'label': [0, 1, 0, 1, 0]
        })
        
        train_df, val_df, test_df = split_dataset(df, 'text', 'label')
        
        # Check sizes
        assert len(train_df) + len(val_df) + len(test_df) == len(df)
        assert len(train_df) > 0
        assert len(val_df) > 0
        assert len(test_df) > 0
    
    def test_get_class_weights(self):
        """Test class weight calculation."""
        labels = [0, 0, 0, 1, 1]
        weights = get_class_weights(labels)
        
        assert len(weights) == 2
        assert weights[0] < weights[1]  # Class 0 is more frequent


class TestHateSpeechDataset:
    """Test cases for HateSpeechDataset."""
    
    def test_dataset_creation(self):
        """Test dataset creation."""
        texts = ["This is hate speech", "This is not hate speech"]
        labels = [1, 0]
        
        # Mock tokenizer
        mock_tokenizer = Mock()
        mock_tokenizer.return_value = {
            'input_ids': [[1, 2, 3, 4, 5]],
            'attention_mask': [[1, 1, 1, 1, 1]]
        }
        
        dataset = HateSpeechDataset(texts, labels, mock_tokenizer)
        
        assert len(dataset) == 2
        assert dataset.texts == texts
        assert dataset.labels == labels
    
    def test_get_class_weights(self):
        """Test class weight calculation."""
        texts = ["text1", "text2", "text3", "text4"]
        labels = [0, 0, 1, 1]
        
        mock_tokenizer = Mock()
        dataset = HateSpeechDataset(texts, labels, mock_tokenizer)
        
        weights = dataset.get_class_weights()
        assert len(weights) == 2
        assert weights[0] == weights[1]  # Balanced classes


class TestTextPreprocessor:
    """Test cases for TextPreprocessor."""
    
    def test_preprocessor_initialization(self):
        """Test preprocessor initialization."""
        preprocessor = TextPreprocessor()
        assert preprocessor.remove_urls == True
        assert preprocessor.remove_mentions == True
        assert preprocessor.lowercase == True
    
    def test_preprocess_text(self):
        """Test text preprocessing."""
        preprocessor = TextPreprocessor()
        
        text = "This is a test @user #hashtag http://example.com"
        processed = preprocessor.preprocess(text)
        
        assert "@user" not in processed
        assert "http://example.com" not in processed
        assert processed.islower()
    
    def test_preprocess_batch(self):
        """Test batch preprocessing."""
        preprocessor = TextPreprocessor()
        
        texts = [
            "This is hate speech",
            "This is not hate speech",
            "Another test @user"
        ]
        
        processed = preprocessor.preprocess_batch(texts)
        
        assert len(processed) == len(texts)
        assert all(isinstance(text, str) for text in processed)
    
    def test_preprocess_dataframe(self):
        """Test DataFrame preprocessing."""
        preprocessor = TextPreprocessor()
        
        df = pd.DataFrame({
            'text': ["This is hate speech", "This is not hate speech"],
            'label': [1, 0]
        })
        
        processed_df = preprocessor.preprocess_dataframe(df, 'text')
        
        assert len(processed_df) == len(df)
        assert 'text' in processed_df.columns
        assert all(isinstance(text, str) for text in processed_df['text'])


if __name__ == "__main__":
    pytest.main([__file__])
