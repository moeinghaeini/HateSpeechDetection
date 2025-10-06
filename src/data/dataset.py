"""
Dataset classes for hate speech detection.
"""

import torch
from torch.utils.data import Dataset
from typing import List, Dict, Any, Optional
import pandas as pd
from loguru import logger


class HateSpeechDataset(Dataset):
    """Custom dataset class for hate speech detection."""
    
    def __init__(self, texts: List[str], labels: List[int], tokenizer, 
                 max_length: int = 512, label_mapping: Optional[Dict[str, int]] = None):
        """
        Initialize the dataset.
        
        Args:
            texts: List of text samples
            labels: List of corresponding labels
            tokenizer: Tokenizer for text processing
            max_length: Maximum sequence length
            label_mapping: Optional mapping from label names to integers
        """
        self.texts = texts
        self.labels = labels
        self.tokenizer = tokenizer
        self.max_length = max_length
        self.label_mapping = label_mapping
        
        # Validate inputs
        if len(texts) != len(labels):
            raise ValueError("Number of texts and labels must match")
        
        logger.info(f"Dataset initialized with {len(texts)} samples")
    
    def __len__(self) -> int:
        """Return the number of samples in the dataset."""
        return len(self.texts)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """
        Get a sample from the dataset.
        
        Args:
            idx: Index of the sample
            
        Returns:
            Dictionary containing input_ids, attention_mask, and labels
        """
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
    
    def get_class_weights(self) -> torch.Tensor:
        """
        Calculate class weights for imbalanced datasets.
        
        Returns:
            Class weights tensor
        """
        from collections import Counter
        
        class_counts = Counter(self.labels)
        total_samples = len(self.labels)
        num_classes = len(class_counts)
        
        weights = []
        for i in range(num_classes):
            if i in class_counts:
                weight = total_samples / (num_classes * class_counts[i])
                weights.append(weight)
            else:
                weights.append(1.0)
        
        return torch.FloatTensor(weights)
    
    def get_class_distribution(self) -> Dict[int, int]:
        """
        Get the distribution of classes in the dataset.
        
        Returns:
            Dictionary mapping class labels to counts
        """
        from collections import Counter
        return dict(Counter(self.labels))
    
    def to_dataframe(self) -> pd.DataFrame:
        """
        Convert dataset to pandas DataFrame.
        
        Returns:
            DataFrame with texts and labels
        """
        return pd.DataFrame({
            'text': self.texts,
            'label': self.labels
        })


class BalancedHateSpeechDataset(HateSpeechDataset):
    """Balanced dataset that ensures equal representation of classes."""
    
    def __init__(self, texts: List[str], labels: List[int], tokenizer, 
                 max_length: int = 512, label_mapping: Optional[Dict[str, int]] = None,
                 balance_method: str = 'undersample'):
        """
        Initialize balanced dataset.
        
        Args:
            texts: List of text samples
            labels: List of corresponding labels
            tokenizer: Tokenizer for text processing
            max_length: Maximum sequence length
            label_mapping: Optional mapping from label names to integers
            balance_method: Method for balancing ('undersample', 'oversample')
        """
        super().__init__(texts, labels, tokenizer, max_length, label_mapping)
        
        if balance_method == 'undersample':
            self._undersample()
        elif balance_method == 'oversample':
            self._oversample()
        else:
            raise ValueError(f"Unknown balance method: {balance_method}")
    
    def _undersample(self) -> None:
        """Undersample majority class to balance the dataset."""
        from collections import Counter
        import random
        
        class_counts = Counter(self.labels)
        min_count = min(class_counts.values())
        
        # Get indices for each class
        class_indices = {}
        for i, label in enumerate(self.labels):
            if label not in class_indices:
                class_indices[label] = []
            class_indices[label].append(i)
        
        # Sample equal number from each class
        balanced_indices = []
        for label, indices in class_indices.items():
            sampled_indices = random.sample(indices, min_count)
            balanced_indices.extend(sampled_indices)
        
        # Update dataset
        self.texts = [self.texts[i] for i in balanced_indices]
        self.labels = [self.labels[i] for i in balanced_indices]
        
        logger.info(f"Dataset balanced by undersampling: {len(self.texts)} samples")
    
    def _oversample(self) -> None:
        """Oversample minority class to balance the dataset."""
        from collections import Counter
        import random
        
        class_counts = Counter(self.labels)
        max_count = max(class_counts.values())
        
        # Get indices for each class
        class_indices = {}
        for i, label in enumerate(self.labels):
            if label not in class_indices:
                class_indices[label] = []
            class_indices[label].append(i)
        
        # Oversample each class to max_count
        balanced_texts = []
        balanced_labels = []
        
        for label, indices in class_indices.items():
            # Add original samples
            balanced_texts.extend([self.texts[i] for i in indices])
            balanced_labels.extend([self.labels[i] for i in indices])
            
            # Add oversampled samples
            while len([l for l in balanced_labels if l == label]) < max_count:
                random_idx = random.choice(indices)
                balanced_texts.append(self.texts[random_idx])
                balanced_labels.append(self.labels[random_idx])
        
        # Update dataset
        self.texts = balanced_texts
        self.labels = balanced_labels
        
        logger.info(f"Dataset balanced by oversampling: {len(self.texts)} samples")
