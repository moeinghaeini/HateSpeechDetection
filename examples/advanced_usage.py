"""
Advanced usage example for hate speech detection.
"""

import sys
from pathlib import Path
import pandas as pd
import torch
import numpy as np
from loguru import logger

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

from src.utils.config import load_config, setup_logging
from src.utils.data_utils import get_device
from src.data.loaders import DataLoaderFactory
from src.data.preprocessing import TextPreprocessor, AdvancedTextPreprocessor
from src.models.hate_speech_classifier import (
    HateSpeechClassifier, MultiTaskHateSpeechClassifier, 
    HierarchicalHateSpeechClassifier, AttentionHateSpeechClassifier
)
from src.models.trainer import Trainer
from src.models.evaluator import Evaluator
from src.utils.metrics import plot_confusion_matrix, plot_roc_curve


def main():
    """Advanced example function."""
    # Load configuration
    config = load_config("config/config.yaml")
    
    # Setup logging
    setup_logging(config)
    
    # Get device
    device = get_device(config.get('model', {}).get('device', 'auto'))
    logger.info(f"Using device: {device}")
    
    # Create more comprehensive sample data
    sample_data = {
        'text': [
            "This is a normal comment about the weather",
            "I hate you so much, you are worthless",
            "Have a great day everyone!",
            "You are stupid and I wish you would die",
            "Thanks for the help, much appreciated",
            "I hate everyone here, they are all idiots",
            "What a beautiful sunset today",
            "You are a terrible person and should be ashamed",
            "Looking forward to the weekend",
            "I despise you and hope you suffer",
            "Great job on the project!",
            "You are a complete failure and waste of space"
        ],
        'label': [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1]
    }
    
    df = pd.DataFrame(sample_data)
    logger.info(f"Created sample dataset with {len(df)} samples")
    
    # Initialize advanced text preprocessor
    preprocessor = AdvancedTextPreprocessor(
        remove_urls=True,
        remove_mentions=True,
        remove_hashtags=False,
        lowercase=True,
        remove_stopwords=False,
        lemmatize_words=True
    )
    
    # Preprocess data
    df_processed = preprocessor.preprocess_dataframe(df, 'text')
    logger.info(f"Preprocessed {len(df_processed)} texts")
    
    # Get preprocessing statistics
    stats = preprocessor.get_preprocessing_stats(df['text'].tolist(), df_processed['text'].tolist())
    logger.info(f"Preprocessing stats: {stats}")
    
    # Initialize data loader factory
    data_factory = DataLoaderFactory(
        tokenizer_name="bert-base-uncased",
        max_length=512,
        batch_size=4
    )
    
    # Create data loaders
    train_loader, val_loader, test_loader = data_factory.load_from_dataframe(
        df_processed, 'text', 'label'
    )
    
    logger.info("Data loaders created successfully")
    
    # Test different model architectures
    models = {
        'Base BERT': HateSpeechClassifier("bert-base-uncased", num_labels=2),
        'Multi-Task': MultiTaskHateSpeechClassifier("bert-base-uncased", num_labels=2, num_auxiliary_labels=3),
        'Hierarchical': HierarchicalHateSpeechClassifier("bert-base-uncased", num_labels=2, num_categories=3),
        'Attention': AttentionHateSpeechClassifier("bert-base-uncased", num_labels=2, attention_heads=8)
    }
    
    results = {}
    
    for model_name, model in models.items():
        logger.info(f"Training {model_name}...")
        
        # Initialize trainer
        trainer = Trainer(
            model=model,
            config=config,
            device=device,
            use_wandb=False
        )
        
        # Train model
        history = trainer.train(train_loader, val_loader)
        
        # Initialize evaluator
        evaluator = Evaluator(
            model=model,
            device=device,
            class_names=['Non-Hate', 'Hate']
        )
        
        # Evaluate model
        eval_results = evaluator.evaluate(test_loader, save_results=False)
        
        # Store results
        results[model_name] = {
            'metrics': eval_results['metrics'],
            'history': history
        }
        
        logger.info(f"{model_name} - F1: {eval_results['metrics']['f1']:.4f}")
    
    # Compare models
    logger.info("Model Comparison:")
    for model_name, result in results.items():
        metrics = result['metrics']
        logger.info(f"{model_name}:")
        logger.info(f"  Accuracy: {metrics['accuracy']:.4f}")
        logger.info(f"  Precision: {metrics['precision']:.4f}")
        logger.info(f"  Recall: {metrics['recall']:.4f}")
        logger.info(f"  F1 Score: {metrics['f1']:.4f}")
        if 'auc' in metrics:
            logger.info(f"  AUC: {metrics['auc']:.4f}")
        logger.info("")
    
    # Find best model
    best_model_name = max(results.keys(), key=lambda x: results[x]['metrics']['f1'])
    logger.info(f"Best model: {best_model_name} (F1: {results[best_model_name]['metrics']['f1']:.4f})")
    
    # Advanced evaluation with the best model
    best_model = models[best_model_name]
    evaluator = Evaluator(best_model, device, class_names=['Non-Hate', 'Hate'])
    
    # Get detailed evaluation results
    detailed_results = evaluator.evaluate(test_loader, save_results=True, results_dir="results/")
    
    # Create visualizations
    logger.info("Creating visualizations...")
    
    # Confusion matrix
    cm_fig = plot_confusion_matrix(
        detailed_results['labels'],
        detailed_results['predictions'],
        class_names=['Non-Hate', 'Hate'],
        save_path="results/confusion_matrix.png"
    )
    
    # ROC curve
    if len(np.unique(detailed_results['labels'])) == 2:
        roc_fig = plot_roc_curve(
            detailed_results['labels'],
            [prob[1] for prob in detailed_results['probabilities']],
            class_names=['Non-Hate', 'Hate'],
            save_path="results/roc_curve.png"
        )
    
    logger.info("Visualizations saved to results/")
    
    # Error analysis
    logger.info("Performing error analysis...")
    errors = evaluator.analyze_errors(test_loader, num_samples=5)
    
    logger.info(f"False Positives: {len(errors['false_positives'])}")
    logger.info(f"False Negatives: {len(errors['false_negatives'])}")
    
    # Attention visualization (for attention-based model)
    if isinstance(best_model, AttentionHateSpeechClassifier):
        logger.info("Analyzing attention weights...")
        sample_text = "I hate you so much"
        attention_weights = evaluator.get_attention_weights(sample_text)
        logger.info(f"Attention weights shape: {attention_weights.shape}")
    
    # Cross-validation example
    logger.info("Performing cross-validation...")
    cv_splits = data_factory.create_cross_validation_splits(
        df_processed, 'text', 'label', n_splits=3
    )
    
    cv_results = []
    for i, (train_loader_cv, val_loader_cv) in enumerate(cv_splits):
        logger.info(f"Training on fold {i+1}")
        
        # Train model on this fold
        model_cv = HateSpeechClassifier("bert-base-uncased", num_labels=2)
        trainer_cv = Trainer(model_cv, config, device, use_wandb=False)
        trainer_cv.train(train_loader_cv, val_loader_cv)
        
        # Evaluate on validation set
        evaluator_cv = Evaluator(model_cv, device, class_names=['Non-Hate', 'Hate'])
        cv_result = evaluator_cv.evaluate(val_loader_cv, save_results=False)
        cv_results.append(cv_result['metrics']['f1'])
        
        logger.info(f"Fold {i+1} F1: {cv_result['metrics']['f1']:.4f}")
    
    logger.info(f"Cross-validation F1: {np.mean(cv_results):.4f} ± {np.std(cv_results):.4f}")
    
    # Model ensemble example
    logger.info("Creating model ensemble...")
    ensemble_models = {
        'BERT': models['Base BERT'],
        'Multi-Task': models['Multi-Task'],
        'Attention': models['Attention']
    }
    
    ensemble_results = evaluator.compare_models(ensemble_models, test_loader)
    
    logger.info("Ensemble comparison:")
    for model_name, metrics in ensemble_results.items():
        logger.info(f"{model_name}: F1={metrics['f1']:.4f}")
    
    logger.info("Advanced usage example completed!")


if __name__ == "__main__":
    main()
