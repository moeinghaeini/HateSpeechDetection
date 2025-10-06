"""
Model utilities and helper functions.
"""

import torch
import torch.nn as nn
from transformers import AutoModel, AutoTokenizer, AutoConfig
from typing import Dict, Any, Optional, Tuple
import os
from pathlib import Path
import json
from loguru import logger


class HateSpeechClassifier(nn.Module):
    """Hate speech classification model."""
    
    def __init__(self, model_name: str, num_labels: int = 2, dropout_rate: float = 0.1):
        super(HateSpeechClassifier, self).__init__()
        
        self.config = AutoConfig.from_pretrained(model_name)
        self.bert = AutoModel.from_pretrained(model_name)
        self.dropout = nn.Dropout(dropout_rate)
        self.classifier = nn.Linear(self.config.hidden_size, num_labels)
        
    def forward(self, input_ids, attention_mask):
        outputs = self.bert(input_ids=input_ids, attention_mask=attention_mask)
        pooled_output = outputs.pooler_output
        output = self.dropout(pooled_output)
        return self.classifier(output)


def get_device(device: str = "auto") -> torch.device:
    """
    Get the appropriate device for training.
    
    Args:
        device: Device specification ("auto", "cpu", "cuda")
        
    Returns:
        PyTorch device
    """
    if device == "auto":
        if torch.cuda.is_available():
            device = "cuda"
        elif torch.backends.mps.is_available():
            device = "mps"
        else:
            device = "cpu"
    
    logger.info(f"Using device: {device}")
    return torch.device(device)


def save_model(model: nn.Module, tokenizer, save_path: str, 
               model_config: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> None:
    """
    Save model, tokenizer, and metadata.
    
    Args:
        model: Trained model
        tokenizer: Tokenizer
        save_path: Path to save the model
        model_config: Model configuration
        metadata: Additional metadata
    """
    save_path = Path(save_path)
    save_path.mkdir(parents=True, exist_ok=True)
    
    # Save model
    torch.save(model.state_dict(), save_path / "pytorch_model.bin")
    
    # Save tokenizer
    tokenizer.save_pretrained(save_path)
    
    # Save model config
    with open(save_path / "model_config.json", "w") as f:
        json.dump(model_config, f, indent=2)
    
    # Save metadata
    if metadata:
        with open(save_path / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)
    
    logger.info(f"Model saved to {save_path}")


def load_model(model_path: str, device: torch.device) -> Tuple[nn.Module, Any, Dict[str, Any]]:
    """
    Load model, tokenizer, and configuration.
    
    Args:
        model_path: Path to the saved model
        device: Device to load the model on
        
    Returns:
        Tuple of (model, tokenizer, config)
    """
    model_path = Path(model_path)
    
    # Load configuration
    with open(model_path / "model_config.json", "r") as f:
        model_config = json.load(f)
    
    # Load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    
    # Initialize model
    model = HateSpeechClassifier(
        model_name=model_config["model_name"],
        num_labels=model_config["num_labels"],
        dropout_rate=model_config.get("dropout_rate", 0.1)
    )
    
    # Load model weights
    model.load_state_dict(torch.load(model_path / "pytorch_model.bin", map_location=device))
    model.to(device)
    model.eval()
    
    logger.info(f"Model loaded from {model_path}")
    
    return model, tokenizer, model_config


def get_model_size(model: nn.Module) -> Dict[str, int]:
    """
    Get model size information.
    
    Args:
        model: PyTorch model
        
    Returns:
        Dictionary with model size information
    """
    total_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    
    return {
        "total_parameters": total_params,
        "trainable_parameters": trainable_params,
        "non_trainable_parameters": total_params - trainable_params
    }


def freeze_parameters(model: nn.Module, freeze_bert: bool = True) -> None:
    """
    Freeze model parameters.
    
    Args:
        model: PyTorch model
        freeze_bert: Whether to freeze BERT parameters
    """
    if freeze_bert:
        for param in model.bert.parameters():
            param.requires_grad = False
        logger.info("BERT parameters frozen")
    else:
        for param in model.bert.parameters():
            param.requires_grad = True
        logger.info("BERT parameters unfrozen")


def initialize_weights(model: nn.Module) -> None:
    """
    Initialize model weights.
    
    Args:
        model: PyTorch model
    """
    for name, param in model.named_parameters():
        if 'classifier' in name and param.dim() > 1:
            nn.init.xavier_uniform_(param)
        elif 'bias' in name:
            nn.init.constant_(param, 0)
    
    logger.info("Model weights initialized")


def get_learning_rate_scheduler(optimizer, num_training_steps: int, 
                               num_warmup_steps: int = 0) -> torch.optim.lr_scheduler.LambdaLR:
    """
    Get learning rate scheduler.
    
    Args:
        optimizer: Optimizer
        num_training_steps: Total number of training steps
        num_warmup_steps: Number of warmup steps
        
    Returns:
        Learning rate scheduler
    """
    def lr_lambda(current_step):
        if current_step < num_warmup_steps:
            return float(current_step) / float(max(1, num_warmup_steps))
        return max(
            0.0, float(num_training_steps - current_step) / float(max(1, num_training_steps - num_warmup_steps))
        )
    
    return torch.optim.lr_scheduler.LambdaLR(optimizer, lr_lambda)
