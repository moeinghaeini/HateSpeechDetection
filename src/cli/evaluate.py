"""
Evaluation command-line interface.
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
from src.models.evaluator import Evaluator
from src.utils.model_utils import load_model


def main():
    """Main evaluation function."""
    parser = argparse.ArgumentParser(description="Evaluate hate speech detection model")
    parser.add_argument("--config", type=str, default="config/config.yaml",
                       help="Path to configuration file")
    parser.add_argument("--model-path", type=str, required=True,
                       help="Path to trained model")
    parser.add_argument("--data", type=str, required=True,
                       help="Path to test data")
    parser.add_argument("--text-column", type=str, default="text",
                       help="Name of the text column")
    parser.add_argument("--label-column", type=str, default="label",
                       help="Name of the label column")
    parser.add_argument("--output-dir", type=str, default="results",
                       help="Directory to save evaluation results")
    parser.add_argument("--class-names", nargs='+', default=['Non-Hate', 'Hate'],
                       help="Names of classes")
    
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    
    # Setup logging
    setup_logging(config)
    
    # Get device
    device = get_device(config.get('model', {}).get('device', 'auto'))
    
    logger.info("Starting hate speech detection evaluation")
    logger.info(f"Using device: {device}")
    logger.info(f"Model path: {args.model_path}")
    
    try:
        # Load model
        model, tokenizer, model_config = load_model(args.model_path, device)
        
        # Initialize data loader factory
        data_factory = DataLoaderFactory(
            tokenizer_name=model_config['model_name'],
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
        
        # Load test data
        if args.data.endswith('.csv'):
            _, _, test_loader = data_factory.load_from_csv(
                args.data, args.text_column, args.label_column,
                preprocessor=preprocessor
            )
        elif args.data.endswith('.json'):
            _, _, test_loader = data_factory.load_from_json(
                args.data, args.text_column, args.label_column,
                preprocessor=preprocessor
            )
        else:
            raise ValueError(f"Unsupported file format: {args.data}")
        
        # Initialize evaluator
        evaluator = Evaluator(
            model=model,
            device=device,
            class_names=args.class_names
        )
        
        # Evaluate model
        results = evaluator.evaluate(
            test_loader=test_loader,
            save_results=True,
            results_dir=args.output_dir
        )
        
        # Print results
        logger.info("Evaluation Results:")
        logger.info(f"Accuracy: {results['metrics']['accuracy']:.4f}")
        logger.info(f"Precision: {results['metrics']['precision']:.4f}")
        logger.info(f"Recall: {results['metrics']['recall']:.4f}")
        logger.info(f"F1 Score: {results['metrics']['f1']:.4f}")
        
        if 'auc' in results['metrics']:
            logger.info(f"AUC: {results['metrics']['auc']:.4f}")
        
        logger.info("Evaluation completed successfully")
        logger.info(f"Results saved to {args.output_dir}")
        
    except Exception as e:
        logger.error(f"Evaluation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
