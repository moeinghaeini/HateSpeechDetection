"""
Data processing and loading utilities.
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Any, Optional
from pathlib import Path
import re
import string
from sklearn.model_selection import train_test_split
from torch.utils.data import Dataset, DataLoader
import torch
from transformers import AutoTokenizer
from loguru import logger


class HateSpeechDataset(Dataset):
    """Custom dataset class for hate speech detection."""
    
    def __init__(self, texts: List[str], labels: List[int], tokenizer, max_length: int = 512):
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
    
    def __len__(self):
        return len(self.texts)
    
    def __getitem__(self, idx):
        text = str(self.texts[idx])
        label = self.labels[idx]
        
        # Tokenize text
        encoding = self.tokenizer(
            text,
            truncation=True,
            padding='max_length',
            max_length=self.max_length,
            return_tensors='pt'
        )
        
        return {
            'input_ids': encoding['input_ids'].flatten(),
            'attention_mask': encoding['attention_mask'].flatten(),
            'labels': torch.tensor(label, dtype=torch.long)
        }


def load_dataset(data_path: str, file_format: str = 'csv') -> pd.DataFrame:
    """
    Load dataset from file.
    
    Args:
        data_path: Path to the dataset file
        file_format: Format of the dataset file ('csv', 'json', 'jsonl')
        
    Returns:
        Loaded dataset as pandas DataFrame
    """
    try:
        if file_format.lower() == 'csv':
            df = pd.read_csv(data_path)
        elif file_format.lower() == 'json':
            df = pd.read_json(data_path)
        elif file_format.lower() == 'jsonl':
            df = pd.read_json(data_path, lines=True)
        else:
            raise ValueError(f"Unsupported file format: {file_format}")
        
        logger.info(f"Dataset loaded from {data_path}: {len(df)} samples")
        return df
        
    except Exception as e:
        logger.error(f"Error loading dataset from {data_path}: {e}")
        raise


def preprocess_text(text: str, remove_urls: bool = True, remove_mentions: bool = True, 
                   remove_hashtags: bool = False, lowercase: bool = True) -> str:
    """
    Preprocess text for hate speech detection.
    
    Args:
        text: Input text to preprocess
        remove_urls: Whether to remove URLs
        remove_mentions: Whether to remove @mentions
        remove_hashtags: Whether to remove #hashtags
        lowercase: Whether to convert to lowercase
        
    Returns:
        Preprocessed text
    """
    if pd.isna(text) or text is None:
        return ""
    
    text = str(text).strip()
    
    if remove_urls:
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
    
    if remove_mentions:
        # Remove @mentions
        text = re.sub(r'@\w+', '', text)
    
    if remove_hashtags:
        # Remove #hashtags
        text = re.sub(r'#\w+', '', text)
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    if lowercase:
        text = text.lower()
    
    return text.strip()


def create_data_loaders(train_texts: List[str], train_labels: List[int],
                       val_texts: List[str], val_labels: List[int],
                       test_texts: List[str], test_labels: List[int],
                       tokenizer, batch_size: int = 16, max_length: int = 512) -> Tuple[DataLoader, DataLoader, DataLoader]:
    """
    Create data loaders for training, validation, and testing.
    
    Args:
        train_texts: Training texts
        train_labels: Training labels
        val_texts: Validation texts
        val_labels: Validation labels
        test_texts: Test texts
        test_labels: Test labels
        tokenizer: Tokenizer for text processing
        batch_size: Batch size for data loaders
        max_length: Maximum sequence length
        
    Returns:
        Tuple of (train_loader, val_loader, test_loader)
    """
    # Create datasets
    train_dataset = HateSpeechDataset(train_texts, train_labels, tokenizer, max_length)
    val_dataset = HateSpeechDataset(val_texts, val_labels, tokenizer, max_length)
    test_dataset = HateSpeechDataset(test_texts, test_labels, tokenizer, max_length)
    
    # Create data loaders
    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=batch_size, shuffle=False)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False)
    
    logger.info(f"Data loaders created - Train: {len(train_dataset)}, Val: {len(val_dataset)}, Test: {len(test_dataset)}")
    
    return train_loader, val_loader, test_loader


def split_dataset(df: pd.DataFrame, text_column: str, label_column: str,
                  train_size: float = 0.7, val_size: float = 0.15, 
                  test_size: float = 0.15, random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Split dataset into train, validation, and test sets.
    
    Args:
        df: Input DataFrame
        text_column: Name of the text column
        label_column: Name of the label column
        train_size: Proportion of data for training
        val_size: Proportion of data for validation
        test_size: Proportion of data for testing
        random_state: Random state for reproducibility
        
    Returns:
        Tuple of (train_df, val_df, test_df)
    """
    # Validate split sizes
    if abs(train_size + val_size + test_size - 1.0) > 1e-6:
        raise ValueError("Train, validation, and test sizes must sum to 1.0")
    
    # First split: train vs (val + test)
    train_df, temp_df = train_test_split(
        df, 
        test_size=(val_size + test_size), 
        random_state=random_state,
        stratify=df[label_column] if label_column in df.columns else None
    )
    
    # Second split: val vs test
    val_ratio = val_size / (val_size + test_size)
    val_df, test_df = train_test_split(
        temp_df,
        test_size=(1 - val_ratio),
        random_state=random_state,
        stratify=temp_df[label_column] if label_column in temp_df.columns else None
    )
    
    logger.info(f"Dataset split - Train: {len(train_df)}, Val: {len(val_df)}, Test: {len(test_df)}")
    
    return train_df, val_df, test_df


def get_class_weights(labels: List[int]) -> torch.Tensor:
    """
    Calculate class weights for imbalanced datasets.
    
    Args:
        labels: List of labels
        
    Returns:
        Class weights tensor
    """
    from collections import Counter
    
    class_counts = Counter(labels)
    total_samples = len(labels)
    num_classes = len(class_counts)
    
    weights = []
    for i in range(num_classes):
        weight = total_samples / (num_classes * class_counts[i])
        weights.append(weight)
    
    return torch.FloatTensor(weights)
