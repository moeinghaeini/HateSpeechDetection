"""
Tests for model components.
"""

import pytest
import torch
import torch.nn as nn
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.models.hate_speech_classifier import HateSpeechClassifier, MultiTaskHateSpeechClassifier
from src.models.trainer import Trainer, FocalLoss
from src.models.evaluator import Evaluator


class TestHateSpeechClassifier:
    """Test cases for HateSpeechClassifier."""
    
    def test_model_initialization(self):
        """Test model initialization."""
        model = HateSpeechClassifier(
            model_name="bert-base-uncased",
            num_labels=2,
            dropout_rate=0.1
        )
        
        assert model.num_labels == 2
        assert model.dropout_rate == 0.1
        assert isinstance(model.classifier, nn.Linear)
    
    def test_forward_pass(self):
        """Test forward pass."""
        model = HateSpeechClassifier(
            model_name="bert-base-uncased",
            num_labels=2,
            dropout_rate=0.1
        )
        
        # Create dummy inputs
        batch_size = 2
        seq_length = 10
        input_ids = torch.randint(0, 1000, (batch_size, seq_length))
        attention_mask = torch.ones(batch_size, seq_length)
        
        # Forward pass
        outputs = model(input_ids, attention_mask)
        
        assert outputs.shape == (batch_size, 2)
        assert torch.is_tensor(outputs)
    
    def test_get_embeddings(self):
        """Test embedding extraction."""
        model = HateSpeechClassifier(
            model_name="bert-base-uncased",
            num_labels=2,
            dropout_rate=0.1
        )
        
        # Create dummy inputs
        batch_size = 2
        seq_length = 10
        input_ids = torch.randint(0, 1000, (batch_size, seq_length))
        attention_mask = torch.ones(batch_size, seq_length)
        
        # Get embeddings
        embeddings = model.get_embeddings(input_ids, attention_mask)
        
        assert embeddings.shape == (batch_size, model.config.hidden_size)
        assert torch.is_tensor(embeddings)


class TestMultiTaskHateSpeechClassifier:
    """Test cases for MultiTaskHateSpeechClassifier."""
    
    def test_model_initialization(self):
        """Test multi-task model initialization."""
        model = MultiTaskHateSpeechClassifier(
            model_name="bert-base-uncased",
            num_labels=2,
            num_auxiliary_labels=3,
            dropout_rate=0.1
        )
        
        assert model.num_labels == 2
        assert model.num_auxiliary_labels == 3
        assert isinstance(model.main_classifier, nn.Linear)
        assert isinstance(model.auxiliary_classifier, nn.Linear)
    
    def test_forward_pass(self):
        """Test multi-task forward pass."""
        model = MultiTaskHateSpeechClassifier(
            model_name="bert-base-uncased",
            num_labels=2,
            num_auxiliary_labels=3,
            dropout_rate=0.1
        )
        
        # Create dummy inputs
        batch_size = 2
        seq_length = 10
        input_ids = torch.randint(0, 1000, (batch_size, seq_length))
        attention_mask = torch.ones(batch_size, seq_length)
        
        # Forward pass
        main_outputs, aux_outputs = model(input_ids, attention_mask)
        
        assert main_outputs.shape == (batch_size, 2)
        assert aux_outputs.shape == (batch_size, 3)
        assert torch.is_tensor(main_outputs)
        assert torch.is_tensor(aux_outputs)


class TestFocalLoss:
    """Test cases for FocalLoss."""
    
    def test_focal_loss_initialization(self):
        """Test focal loss initialization."""
        focal_loss = FocalLoss(alpha=1.0, gamma=2.0)
        
        assert focal_loss.alpha == 1.0
        assert focal_loss.gamma == 2.0
    
    def test_focal_loss_forward(self):
        """Test focal loss forward pass."""
        focal_loss = FocalLoss(alpha=1.0, gamma=2.0)
        
        # Create dummy inputs
        batch_size = 4
        num_classes = 2
        inputs = torch.randn(batch_size, num_classes)
        targets = torch.randint(0, num_classes, (batch_size,))
        
        # Forward pass
        loss = focal_loss(inputs, targets)
        
        assert torch.is_tensor(loss)
        assert loss.item() >= 0


class TestTrainer:
    """Test cases for Trainer."""
    
    def test_trainer_initialization(self):
        """Test trainer initialization."""
        model = HateSpeechClassifier(
            model_name="bert-base-uncased",
            num_labels=2,
            dropout_rate=0.1
        )
        
        config = {
            'model': {
                'learning_rate': 2e-5,
                'weight_decay': 0.01,
                'max_epochs': 5
            },
            'paths': {
                'tensorboard_dir': 'test_logs'
            }
        }
        
        device = torch.device('cpu')
        
        trainer = Trainer(model, config, device)
        
        assert trainer.model == model
        assert trainer.config == config
        assert trainer.device == device
        assert isinstance(trainer.optimizer, torch.optim.Optimizer)
        assert isinstance(trainer.criterion, nn.Module)


class TestEvaluator:
    """Test cases for Evaluator."""
    
    def test_evaluator_initialization(self):
        """Test evaluator initialization."""
        model = HateSpeechClassifier(
            model_name="bert-base-uncased",
            num_labels=2,
            dropout_rate=0.1
        )
        
        device = torch.device('cpu')
        class_names = ['Non-Hate', 'Hate']
        
        evaluator = Evaluator(model, device, class_names)
        
        assert evaluator.model == model
        assert evaluator.device == device
        assert evaluator.class_names == class_names


if __name__ == "__main__":
    pytest.main([__file__])
