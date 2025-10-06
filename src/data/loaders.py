"""
Data loading utilities and factories.
"""

import pandas as pd
import numpy as np
from typing import List, Tuple, Dict, Any, Optional, Union
from pathlib import Path
from torch.utils.data import DataLoader, random_split
from sklearn.model_selection import train_test_split
from transformers import AutoTokenizer
from loguru import logger

from .dataset import HateSpeechDataset, BalancedHateSpeechDataset


class DataLoaderFactory:
    """Factory class for creating data loaders."""
    
    def __init__(self, tokenizer_name: str = "bert-base-uncased", 
                 max_length: int = 512, batch_size: int = 16):
        """
        Initialize data loader factory.
        
        Args:
            tokenizer_name: Name of the tokenizer to use
            max_length: Maximum sequence length
            batch_size: Batch size for data loaders
        """
        self.tokenizer_name = tokenizer_name
        self.max_length = max_length
        self.batch_size = batch_size
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        
        logger.info(f"DataLoaderFactory initialized with tokenizer: {tokenizer_name}")
    
    def load_from_csv(self, file_path: str, text_column: str, label_column: str,
                     preprocessor=None, balance_dataset: bool = False,
                     balance_method: str = 'undersample') -> Tuple[DataLoader, DataLoader, DataLoader]:
        """
        Load dataset from CSV file and create data loaders.
        
        Args:
            file_path: Path to CSV file
            text_column: Name of the text column
            label_column: Name of the label column
            preprocessor: Optional text preprocessor
            balance_dataset: Whether to balance the dataset
            balance_method: Method for balancing ('undersample', 'oversample')
            
        Returns:
            Tuple of (train_loader, val_loader, test_loader)
        """
        # Load data
        df = pd.read_csv(file_path)
        logger.info(f"Loaded dataset from {file_path}: {len(df)} samples")
        
        # Preprocess if preprocessor is provided
        if preprocessor:
            df = preprocessor.preprocess_dataframe(df, text_column)
        
        # Split data
        train_df, val_df, test_df = self._split_dataframe(df, text_column, label_column)
        
        # Create datasets
        train_dataset, val_dataset, test_dataset = self._create_datasets(
            train_df, val_df, test_df, text_column, label_column, 
            balance_dataset, balance_method
        )
        
        # Create data loaders
        train_loader = DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=self.batch_size, shuffle=False)
        test_loader = DataLoader(test_dataset, batch_size=self.batch_size, shuffle=False)
        
        logger.info(f"Data loaders created - Train: {len(train_dataset)}, Val: {len(val_dataset)}, Test: {len(test_dataset)}")
        
        return train_loader, val_loader, test_loader
    
    def load_from_json(self, file_path: str, text_column: str, label_column: str,
                      preprocessor=None, balance_dataset: bool = False,
                      balance_method: str = 'undersample') -> Tuple[DataLoader, DataLoader, DataLoader]:
        """
        Load dataset from JSON file and create data loaders.
        
        Args:
            file_path: Path to JSON file
            text_column: Name of the text column
            label_column: Name of the label column
            preprocessor: Optional text preprocessor
            balance_dataset: Whether to balance the dataset
            balance_method: Method for balancing ('undersample', 'oversample')
            
        Returns:
            Tuple of (train_loader, val_loader, test_loader)
        """
        # Load data
        df = pd.read_json(file_path)
        logger.info(f"Loaded dataset from {file_path}: {len(df)} samples")
        
        # Preprocess if preprocessor is provided
        if preprocessor:
            df = preprocessor.preprocess_dataframe(df, text_column)
        
        # Split data
        train_df, val_df, test_df = self._split_dataframe(df, text_column, label_column)
        
        # Create datasets
        train_dataset, val_dataset, test_dataset = self._create_datasets(
            train_df, val_df, test_df, text_column, label_column, 
            balance_dataset, balance_method
        )
        
        # Create data loaders
        train_loader = DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=self.batch_size, shuffle=False)
        test_loader = DataLoader(test_dataset, batch_size=self.batch_size, shuffle=False)
        
        logger.info(f"Data loaders created - Train: {len(train_dataset)}, Val: {len(val_dataset)}, Test: {len(test_dataset)}")
        
        return train_loader, val_loader, test_loader
    
    def load_from_dataframe(self, df: pd.DataFrame, text_column: str, label_column: str,
                           preprocessor=None, balance_dataset: bool = False,
                           balance_method: str = 'undersample') -> Tuple[DataLoader, DataLoader, DataLoader]:
        """
        Load dataset from pandas DataFrame and create data loaders.
        
        Args:
            df: Input DataFrame
            text_column: Name of the text column
            label_column: Name of the label column
            preprocessor: Optional text preprocessor
            balance_dataset: Whether to balance the dataset
            balance_method: Method for balancing ('undersample', 'oversample')
            
        Returns:
            Tuple of (train_loader, val_loader, test_loader)
        """
        logger.info(f"Loaded dataset from DataFrame: {len(df)} samples")
        
        # Preprocess if preprocessor is provided
        if preprocessor:
            df = preprocessor.preprocess_dataframe(df, text_column)
        
        # Split data
        train_df, val_df, test_df = self._split_dataframe(df, text_column, label_column)
        
        # Create datasets
        train_dataset, val_dataset, test_dataset = self._create_datasets(
            train_df, val_df, test_df, text_column, label_column, 
            balance_dataset, balance_method
        )
        
        # Create data loaders
        train_loader = DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True)
        val_loader = DataLoader(val_dataset, batch_size=self.batch_size, shuffle=False)
        test_loader = DataLoader(test_dataset, batch_size=self.batch_size, shuffle=False)
        
        logger.info(f"Data loaders created - Train: {len(train_dataset)}, Val: {len(val_dataset)}, Test: {len(test_dataset)}")
        
        return train_loader, val_loader, test_loader
    
    def _split_dataframe(self, df: pd.DataFrame, text_column: str, label_column: str,
                        train_size: float = 0.7, val_size: float = 0.15, 
                        test_size: float = 0.15, random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
        """Split DataFrame into train, validation, and test sets."""
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
        
        return train_df, val_df, test_df
    
    def _create_datasets(self, train_df: pd.DataFrame, val_df: pd.DataFrame, test_df: pd.DataFrame,
                        text_column: str, label_column: str, balance_dataset: bool = False,
                        balance_method: str = 'undersample') -> Tuple[HateSpeechDataset, HateSpeechDataset, HateSpeechDataset]:
        """Create dataset objects."""
        # Extract texts and labels
        train_texts = train_df[text_column].tolist()
        train_labels = train_df[label_column].tolist()
        val_texts = val_df[text_column].tolist()
        val_labels = val_df[label_column].tolist()
        test_texts = test_df[text_column].tolist()
        test_labels = test_df[label_column].tolist()
        
        # Create datasets
        if balance_dataset:
            train_dataset = BalancedHateSpeechDataset(
                train_texts, train_labels, self.tokenizer, self.max_length,
                balance_method=balance_method
            )
        else:
            train_dataset = HateSpeechDataset(
                train_texts, train_labels, self.tokenizer, self.max_length
            )
        
        val_dataset = HateSpeechDataset(
            val_texts, val_labels, self.tokenizer, self.max_length
        )
        
        test_dataset = HateSpeechDataset(
            test_texts, test_labels, self.tokenizer, self.max_length
        )
        
        return train_dataset, val_dataset, test_dataset
    
    def create_cross_validation_splits(self, df: pd.DataFrame, text_column: str, label_column: str,
                                     n_splits: int = 5, preprocessor=None) -> List[Tuple[DataLoader, DataLoader]]:
        """
        Create cross-validation splits.
        
        Args:
            df: Input DataFrame
            text_column: Name of the text column
            label_column: Name of the label column
            n_splits: Number of CV splits
            preprocessor: Optional text preprocessor
            
        Returns:
            List of (train_loader, val_loader) tuples
        """
        from sklearn.model_selection import StratifiedKFold
        
        # Preprocess if preprocessor is provided
        if preprocessor:
            df = preprocessor.preprocess_dataframe(df, text_column)
        
        # Create stratified k-fold splits
        skf = StratifiedKFold(n_splits=n_splits, shuffle=True, random_state=42)
        cv_splits = []
        
        for train_idx, val_idx in skf.split(df[text_column], df[label_column]):
            train_df = df.iloc[train_idx]
            val_df = df.iloc[val_idx]
            
            # Create datasets
            train_dataset = HateSpeechDataset(
                train_df[text_column].tolist(),
                train_df[label_column].tolist(),
                self.tokenizer,
                self.max_length
            )
            
            val_dataset = HateSpeechDataset(
                val_df[text_column].tolist(),
                val_df[label_column].tolist(),
                self.tokenizer,
                self.max_length
            )
            
            # Create data loaders
            train_loader = DataLoader(train_dataset, batch_size=self.batch_size, shuffle=True)
            val_loader = DataLoader(val_dataset, batch_size=self.batch_size, shuffle=False)
            
            cv_splits.append((train_loader, val_loader))
        
        logger.info(f"Created {len(cv_splits)} cross-validation splits")
        return cv_splits
