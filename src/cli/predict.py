"""
Prediction command-line interface.
"""

import argparse
import sys
from pathlib import Path
from typing import List, Dict, Any
import torch
import json
from loguru import logger

# Add src to path
sys.path.append(str(Path(__file__).parent.parent.parent))

from src.utils.config import load_config, setup_logging
from src.utils.data_utils import get_device
from src.utils.model_utils import load_model
from src.models.evaluator import Evaluator


def main():
    """Main prediction function."""
    parser = argparse.ArgumentParser(description="Predict hate speech using trained model")
    parser.add_argument("--config", type=str, default="config/config.yaml",
                       help="Path to configuration file")
    parser.add_argument("--model-path", type=str, required=True,
                       help="Path to trained model")
    parser.add_argument("--text", type=str, help="Single text to predict")
    parser.add_argument("--input-file", type=str, help="File containing texts to predict")
    parser.add_argument("--output-file", type=str, help="File to save predictions")
    parser.add_argument("--class-names", nargs='+', default=['Non-Hate', 'Hate'],
                       help="Names of classes")
    parser.add_argument("--threshold", type=float, default=0.5,
                       help="Threshold for binary classification")
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.text and not args.input_file:
        logger.error("Either --text or --input-file must be provided")
        sys.exit(1)
    
    # Load configuration
    config = load_config(args.config)
    
    # Setup logging
    setup_logging(config)
    
    # Get device
    device = get_device(config.get('model', {}).get('device', 'auto'))
    
    logger.info("Starting hate speech prediction")
    logger.info(f"Using device: {device}")
    logger.info(f"Model path: {args.model_path}")
    
    try:
        # Load model
        model, tokenizer, model_config = load_model(args.model_path, device)
        
        # Initialize evaluator
        evaluator = Evaluator(
            model=model,
            device=device,
            class_names=args.class_names
        )
        
        # Get texts to predict
        if args.text:
            texts = [args.text]
        else:
            with open(args.input_file, 'r', encoding='utf-8') as f:
                if args.input_file.endswith('.json'):
                    data = json.load(f)
                    if isinstance(data, list):
                        texts = [item['text'] if isinstance(item, dict) else item for item in data]
                    else:
                        texts = [data['text']]
                else:
                    texts = [line.strip() for line in f if line.strip()]
        
        logger.info(f"Predicting on {len(texts)} texts")
        
        # Make predictions
        predictions = []
        probabilities = []
        
        for text in texts:
            # Tokenize text
            encoding = tokenizer(
                text,
                truncation=True,
                padding=True,
                max_length=512,
                return_tensors='pt'
            )
            
            input_ids = encoding['input_ids'].to(device)
            attention_mask = encoding['attention_mask'].to(device)
            
            # Get prediction
            with torch.no_grad():
                outputs = model(input_ids, attention_mask)
                probs = torch.softmax(outputs, dim=-1)
                pred = torch.argmax(outputs, dim=-1)
                
                predictions.append(pred.cpu().item())
                probabilities.append(probs.cpu().numpy()[0].tolist())
        
        # Create results
        results = []
        for i, (text, pred, prob) in enumerate(zip(texts, predictions, probabilities)):
            result = {
                'text': text,
                'prediction': pred,
                'predicted_class': args.class_names[pred],
                'probabilities': {
                    args.class_names[j]: prob[j] for j in range(len(args.class_names))
                },
                'confidence': max(prob)
            }
            
            # Add binary classification result
            if len(args.class_names) == 2:
                result['is_hate_speech'] = pred == 1
                result['hate_probability'] = prob[1]
                result['meets_threshold'] = prob[1] >= args.threshold
            
            results.append(result)
        
        # Print results
        for i, result in enumerate(results):
            logger.info(f"Text {i+1}:")
            logger.info(f"  Text: {result['text'][:100]}...")
            logger.info(f"  Prediction: {result['predicted_class']}")
            logger.info(f"  Confidence: {result['confidence']:.4f}")
            if 'is_hate_speech' in result:
                logger.info(f"  Is Hate Speech: {result['is_hate_speech']}")
                logger.info(f"  Hate Probability: {result['hate_probability']:.4f}")
            logger.info("")
        
        # Save results
        if args.output_file:
            with open(args.output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            logger.info(f"Results saved to {args.output_file}")
        
        logger.info("Prediction completed successfully")
        
    except Exception as e:
        logger.error(f"Prediction failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
