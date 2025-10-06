"""
Basic usage example for hate speech detection.
"""

import sys
from pathlib import Path
import pandas as pd
import torch
from loguru import logger

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.config import load_config, setup_logging
from src.utils.data_utils import get_device
from src.data.loaders import DataLoaderFactory
from src.data.preprocessing import TextPreprocessor
from src.models.hate_speech_classifier import HateSpeechClassifier
from src.models.trainer import Trainer
from src.models.evaluator import Evaluator


def main():
    """Main example function."""
    # Load configuration
    config = load_config("config/config.yaml")
    
    # Setup logging
    setup_logging(config)
    
    # Get device
    device = get_device(config.get('model', {}).get('device', 'auto'))
    logger.info(f"Using device: {device}")
    
    # Create sample data
    sample_data = {
        'text': [
            "This is a normal comment",
            "I hate you so much",
            "Have a great day!",
            "You are stupid and worthless",
            "Thanks for the help",
            "I wish you would die"
        ],
        'label': [0, 1, 0, 1, 0, 1]
    }
    
    df = pd.DataFrame(sample_data)
    logger.info(f"Created sample dataset with {len(df)} samples")
    
    # Initialize text preprocessor
    preprocessor = TextPreprocessor(
        remove_urls=True,
        remove_mentions=True,
        lowercase=True
    )
    
    # Preprocess data
    df_processed = preprocessor.preprocess_dataframe(df, 'text')
    logger.info(f"Preprocessed {len(df_processed)} texts")
    
    # Initialize data loader factory
    data_factory = DataLoaderFactory(
        tokenizer_name="bert-base-uncased",
        max_length=512,
        batch_size=2
    )
    
    # Create data loaders
    train_loader, val_loader, test_loader = data_factory.load_from_dataframe(
        df_processed, 'text', 'label'
    )
    
    logger.info("Data loaders created successfully")
    
    # Initialize model
    model = HateSpeechClassifier(
        model_name="bert-base-uncased",
        num_labels=2,
        dropout_rate=0.1
    )
    
    logger.info("Model initialized")
    
    # Initialize trainer
    trainer = Trainer(
        model=model,
        config=config,
        device=device,
        use_wandb=False
    )
    
    logger.info("Trainer initialized")
    
    # Train model (short training for example)
    logger.info("Starting training...")
    history = trainer.train(train_loader, val_loader)
    
    logger.info("Training completed")
    logger.info(f"Final training loss: {history['train_loss'][-1]:.4f}")
    logger.info(f"Final validation loss: {history['val_loss'][-1]:.4f}")
    
    # Initialize evaluator
    evaluator = Evaluator(
        model=model,
        device=device,
        class_names=['Non-Hate', 'Hate']
    )
    
    # Evaluate model
    logger.info("Starting evaluation...")
    results = evaluator.evaluate(test_loader, save_results=False)
    
    # Print results
    logger.info("Evaluation Results:")
    logger.info(f"Accuracy: {results['metrics']['accuracy']:.4f}")
    logger.info(f"Precision: {results['metrics']['precision']:.4f}")
    logger.info(f"Recall: {results['metrics']['recall']:.4f}")
    logger.info(f"F1 Score: {results['metrics']['f1']:.4f}")
    
    # Make predictions on new texts
    new_texts = [
        "This is a wonderful day",
        "I hate everyone here"
    ]
    
    logger.info("Making predictions on new texts:")
    for text in new_texts:
        # Tokenize text
        encoding = data_factory.tokenizer(
            text,
            truncation=True,
            padding=True,
            max_length=512,
            return_tensors='pt'
        )
        
        # Make prediction
        with torch.no_grad():
            input_ids = encoding['input_ids'].to(device)
            attention_mask = encoding['attention_mask'].to(device)
            
            outputs = model(input_ids, attention_mask)
            probabilities = torch.softmax(outputs, dim=-1)
            prediction = torch.argmax(outputs, dim=-1)
            
            logger.info(f"Text: {text}")
            logger.info(f"Prediction: {'Hate' if prediction.item() == 1 else 'Non-Hate'}")
            logger.info(f"Confidence: {probabilities.max().item():.4f}")
            logger.info("")


if __name__ == "__main__":
    main()
