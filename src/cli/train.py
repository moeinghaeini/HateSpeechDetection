"""
Training command-line interface.
"""

import argparse
import sys
from pathlib import Path
from typing import Dict, Any
import torch
from loguru import logger

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.config import load_config, setup_logging
from src.utils.data_utils import get_device
from src.data.loaders import DataLoaderFactory
from src.data.preprocessing import TextPreprocessor
from src.models.hate_speech_classifier import HateSpeechClassifier
from src.models.trainer import Trainer


def main():
    """Main training function."""
    parser = argparse.ArgumentParser(description="Train hate speech detection model")
    parser.add_argument("--config", type=str, default="config/config.yaml",
                       help="Path to configuration file")
    parser.add_argument("--data", type=str, required=True,
                       help="Path to training data")
    parser.add_argument("--text-column", type=str, default="text",
                       help="Name of the text column")
    parser.add_argument("--label-column", type=str, default="label",
                       help="Name of the label column")
    parser.add_argument("--model-name", type=str, default="bert-base-uncased",
                       help="Name of the pre-trained model")
    parser.add_argument("--output-dir", type=str, default="models",
                       help="Directory to save the trained model")
    parser.add_argument("--use-wandb", action="store_true",
                       help="Use Weights & Biases for logging")
    parser.add_argument("--balance-dataset", action="store_true",
                       help="Balance the dataset")
    parser.add_argument("--balance-method", type=str, default="undersample",
                       choices=["undersample", "oversample"],
                       help="Method for balancing dataset")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Setup logging
    setup_logging(config)
    
    # Get device
    device = get_device(config.get('model', {}).get('device', 'auto'))
    
    logger.info("Starting hate speech detection training")
    logger.info(f"Using device: {device}")
    logger.info(f"Model: {args.model_name}")
    
    try:
        # Initialize data loader factory
        data_factory = DataLoaderFactory(
            tokenizer_name=args.model_name,
            max_length=config.get('data', {}).get('max_length', 512),
            batch_size=config.get('model', {}).get('batch_size', 16)
        )
        
        # Initialize text preprocessor
        preprocessor = TextPreprocessor(
            remove_urls=config.get('data', {}).get('remove_urls', True),
            remove_mentions=config.get('data', {}).get('remove_mentions', True),
            remove_hashtags=config.get('data', {}).get('remove_hashtags', False),
            lowercase=config.get('data', {}).get('lowercase', True),
            min_length=config.get('data', {}).get('min_length', 5),
            max_length=config.get('data', {}).get('max_length', 512)
        )
        
        # Load data
        if args.data.endswith('.csv'):
            train_loader, val_loader, test_loader = data_factory.load_from_csv(
                args.data, args.text_column, args.label_column,
                preprocessor=preprocessor,
                balance_dataset=args.balance_dataset,
                balance_method=args.balance_method
            )
        elif args.data.endswith('.json'):
            train_loader, val_loader, test_loader = data_factory.load_from_json(
                args.data, args.text_column, args.label_column,
                preprocessor=preprocessor,
                balance_dataset=args.balance_dataset,
                balance_method=args.balance_method
            )
        else:
            raise ValueError(f"Unsupported file format: {args.data}")
        
        # Initialize model
        model = HateSpeechClassifier(
            model_name=args.model_name,
            num_labels=config.get('model', {}).get('num_labels', 2),
            dropout_rate=config.get('model', {}).get('dropout_rate', 0.1)
        )
        
        # Update config with command line arguments
        config['model']['model_name'] = args.model_name
        config['paths']['models_dir'] = args.output_dir
        
        # Initialize trainer
        trainer = Trainer(
            model=model,
            config=config,
            device=device,
            use_wandb=args.use_wandb
        )
        
        # Train model
        history = trainer.train(train_loader, val_loader)
        
        # Save final model
        from src.utils.model_utils import save_model
        save_model(
            model=trainer.model,
            tokenizer=data_factory.tokenizer,
            save_path=args.output_dir,
            model_config={
                'model_name': args.model_name,
                'num_labels': config.get('model', {}).get('num_labels', 2),
                'dropout_rate': config.get('model', {}).get('dropout_rate', 0.1)
            },
            metadata={
                'training_history': history,
                'config': config
            }
        )
        
        logger.info("Training completed successfully")
        logger.info(f"Model saved to {args.output_dir}")
        
    except Exception as e:
        logger.error(f"Training failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
