"""
Tests for utility functions.
"""

import pytest
import torch
import numpy as np
from unittest.mock import Mock, patch
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.metrics import calculate_metrics, plot_confusion_matrix
from src.utils.model_utils import get_device, get_model_size
from src.utils.config import load_config


class TestMetrics:
    """Test cases for metrics utilities."""
    
    def test_calculate_metrics(self):
        """Test metrics calculation."""
        y_true = [0, 1, 0, 1, 0]
        y_pred = [0, 1, 1, 1, 0]
        y_prob = [0.1, 0.9, 0.8, 0.7, 0.2]
        
        metrics = calculate_metrics(y_true, y_pred, y_prob)
        
        assert 'accuracy' in metrics
        assert 'precision' in metrics
        assert 'recall' in metrics
        assert 'f1' in metrics
        assert 'auc' in metrics
        
        assert 0 <= metrics['accuracy'] <= 1
        assert 0 <= metrics['precision'] <= 1
        assert 0 <= metrics['recall'] <= 1
        assert 0 <= metrics['f1'] <= 1
    
    def test_calculate_metrics_without_probabilities(self):
        """Test metrics calculation without probabilities."""
        y_true = [0, 1, 0, 1, 0]
        y_pred = [0, 1, 1, 1, 0]
        
        metrics = calculate_metrics(y_true, y_pred)
        
        assert 'accuracy' in metrics
        assert 'precision' in metrics
        assert 'recall' in metrics
        assert 'f1' in metrics
        assert 'auc' not in metrics
    
    def test_plot_confusion_matrix(self):
        """Test confusion matrix plotting."""
        y_true = [0, 1, 0, 1, 0]
        y_pred = [0, 1, 1, 1, 0]
        class_names = ['Non-Hate', 'Hate']
        
        # This should not raise an error
        fig = plot_confusion_matrix(y_true, y_pred, class_names)
        
        assert fig is not None


class TestModelUtils:
    """Test cases for model utilities."""
    
    def test_get_device(self):
        """Test device selection."""
        # Test auto device selection
        device = get_device("auto")
        assert isinstance(device, torch.device)
        
        # Test specific device
        device = get_device("cpu")
        assert device == torch.device("cpu")
    
    def test_get_model_size(self):
        """Test model size calculation."""
        model = torch.nn.Linear(10, 2)
        
        size_info = get_model_size(model)
        
        assert 'total_parameters' in size_info
        assert 'trainable_parameters' in size_info
        assert 'non_trainable_parameters' in size_info
        
        assert size_info['total_parameters'] > 0
        assert size_info['trainable_parameters'] > 0
        assert size_info['non_trainable_parameters'] == 0


class TestConfig:
    """Test cases for configuration utilities."""
    
    def test_load_config(self):
        """Test configuration loading."""
        # Create a temporary config file
        import tempfile
        import yaml
        
        config_data = {
            'model': {
                'learning_rate': 2e-5,
                'num_labels': 2
            },
            'data': {
                'max_length': 512
            }
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config_data, f)
            config_path = f.name
        
        try:
            config = load_config(config_path)
            assert config['model']['learning_rate'] == 2e-5
            assert config['model']['num_labels'] == 2
            assert config['data']['max_length'] == 512
        finally:
            import os
            os.unlink(config_path)
    
    def test_load_config_file_not_found(self):
        """Test configuration loading with non-existent file."""
        with pytest.raises(FileNotFoundError):
            load_config("non_existent_config.yaml")


if __name__ == "__main__":
    pytest.main([__file__])
