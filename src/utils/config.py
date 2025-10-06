"""
Configuration management utilities.
"""

import yaml
import os
from pathlib import Path
from typing import Dict, Any
from loguru import logger


def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to the configuration file
        
    Returns:
        Dictionary containing configuration parameters
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config = yaml.safe_load(file)
        
        # Create necessary directories
        _create_directories(config)
        
        logger.info(f"Configuration loaded from {config_path}")
        return config
        
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        raise
    except yaml.YAMLError as e:
        logger.error(f"Error parsing YAML configuration: {e}")
        raise


def _create_directories(config: Dict[str, Any]) -> None:
    """Create necessary directories from configuration."""
    directories = [
        config.get("data", {}).get("raw_data_path", "data/raw"),
        config.get("data", {}).get("processed_data_path", "data/processed"),
        config.get("data", {}).get("external_data_path", "data/external"),
        config.get("paths", {}).get("models_dir", "models"),
        config.get("paths", {}).get("logs_dir", "logs"),
        config.get("paths", {}).get("results_dir", "results"),
        config.get("paths", {}).get("checkpoints_dir", "checkpoints"),
        config.get("paths", {}).get("tensorboard_dir", "tensorboard_logs"),
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)


def setup_logging(config: Dict[str, Any]) -> None:
    """
    Setup logging configuration.
    
    Args:
        config: Configuration dictionary
    """
    log_config = config.get("logging", {})
    
    # Remove default handler
    logger.remove()
    
    # Add console handler
    logger.add(
        sink=lambda msg: print(msg, end=""),
        level=log_config.get("level", "INFO"),
        format=log_config.get("format", "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"),
        colorize=True
    )
    
    # Add file handler
    log_file = log_config.get("file_path", "logs/training.log")
    logger.add(
        sink=log_file,
        level=log_config.get("level", "INFO"),
        format=log_config.get("format", "{time:YYYY-MM-DD HH:mm:ss} | {level} | {name}:{function}:{line} - {message}"),
        rotation=log_config.get("max_file_size", "10 MB"),
        retention=log_config.get("backup_count", 5),
        compression="zip"
    )
    
    logger.info("Logging setup completed")
