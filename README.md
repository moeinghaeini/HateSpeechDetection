# Hate Speech Detection - MSc Thesis Project

A comprehensive machine learning framework for detecting hate speech in text using state-of-the-art transformer models and advanced NLP techniques.

## 🎯 Project Overview

This project implements a robust hate speech detection system designed for academic research and practical applications. It provides a complete pipeline from data preprocessing to model training, evaluation, and deployment.

## ✨ Features

- **Multiple Model Architectures**: BERT, RoBERTa, and custom transformer-based models
- **Advanced Text Preprocessing**: URL removal, mention handling, sentiment analysis
- **Comprehensive Evaluation**: Multiple metrics, confusion matrices, ROC curves
- **Flexible Training**: Support for different loss functions, optimizers, and schedulers
- **Easy-to-Use CLI**: Simple command-line interface for training and prediction
- **Extensive Testing**: Comprehensive test suite with high coverage
- **Documentation**: Detailed documentation and examples

## 🚀 Quick Start

### Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/HateSpeechDetection.git
cd HateSpeechDetection
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Install the package in development mode:
```bash
pip install -e .
```

### Basic Usage

#### Training a Model

```bash
python -m src.cli.train \
    --data data/train.csv \
    --text-column text \
    --label-column label \
    --model-name bert-base-uncased \
    --output-dir models/bert_model
```

#### Evaluating a Model

```bash
python -m src.cli.evaluate \
    --model-path models/bert_model \
    --data data/test.csv \
    --output-dir results/
```

#### Making Predictions

```bash
python -m src.cli.predict \
    --model-path models/bert_model \
    --text "This is a hateful comment" \
    --output-file predictions.json
```

## 📁 Project Structure

```
HateSpeechDetection/
├── config/                 # Configuration files
│   └── config.yaml
├── data/                   # Data directories
│   ├── raw/               # Raw datasets
│   ├── processed/         # Processed datasets
│   └── external/          # External datasets
├── models/                # Saved models
├── results/               # Evaluation results
├── logs/                  # Training logs
├── src/                   # Source code
│   ├── cli/              # Command-line interfaces
│   ├── data/             # Data processing modules
│   ├── models/           # Model implementations
│   └── utils/             # Utility functions
├── tests/                 # Test suite
├── requirements.txt       # Python dependencies
├── setup.py              # Package setup
└── README.md             # This file
```

## 🔧 Configuration

The project uses YAML configuration files for easy customization. Key configuration options include:

- **Model Settings**: Architecture, hyperparameters, training configuration
- **Data Settings**: Preprocessing options, data splits, augmentation
- **Training Settings**: Optimizer, scheduler, early stopping
- **Logging Settings**: TensorBoard, Weights & Biases integration

See `config/config.yaml` for detailed configuration options.

## 📊 Model Architectures

### 1. Base Hate Speech Classifier
- Standard BERT-based classification
- Configurable dropout and hidden layers
- Support for binary and multi-class classification

### 2. Multi-Task Classifier
- Joint learning with auxiliary tasks
- Improved generalization through shared representations
- Configurable task weights

### 3. Hierarchical Classifier
- Multi-level classification approach
- Category-aware classification
- Enhanced interpretability

### 4. Attention-Based Classifier
- Multi-head attention mechanisms
- Improved focus on relevant text segments
- Better handling of long sequences

### 5. Ensemble Classifier
- Combination of multiple models
- Voting and averaging strategies
- Improved robustness and performance

## 🧪 Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_models.py
```

## 📈 Evaluation Metrics

The framework provides comprehensive evaluation including:

- **Accuracy**: Overall classification accuracy
- **Precision/Recall**: Per-class and weighted metrics
- **F1-Score**: Harmonic mean of precision and recall
- **AUC-ROC**: Area under the ROC curve
- **Confusion Matrix**: Detailed classification breakdown
- **Classification Report**: Per-class metrics

## 🔬 Research Features

### Data Preprocessing
- Advanced text cleaning and normalization
- URL, mention, and hashtag handling
- Contraction expansion and slang replacement
- Configurable preprocessing pipelines

### Model Training
- Multiple loss functions (Cross-Entropy, Focal Loss)
- Learning rate scheduling
- Early stopping and model checkpointing
- Gradient clipping and mixed precision training

### Evaluation
- Cross-validation support
- Error analysis and visualization
- Attention weight visualization
- Model comparison utilities

## 📚 Usage Examples

### Custom Model Training

```python
from src.models.hate_speech_classifier import HateSpeechClassifier
from src.models.trainer import Trainer
from src.data.loaders import DataLoaderFactory

# Initialize model
model = HateSpeechClassifier(
    model_name="bert-base-uncased",
    num_labels=2,
    dropout_rate=0.1
)

# Create data loaders
data_factory = DataLoaderFactory("bert-base-uncased")
train_loader, val_loader, test_loader = data_factory.load_from_csv(
    "data/train.csv", "text", "label"
)

# Initialize trainer
trainer = Trainer(model, config, device)

# Train model
history = trainer.train(train_loader, val_loader)
```

### Custom Evaluation

```python
from src.models.evaluator import Evaluator

# Initialize evaluator
evaluator = Evaluator(model, device, class_names=['Non-Hate', 'Hate'])

# Evaluate model
results = evaluator.evaluate(test_loader, save_results=True)

print(f"F1 Score: {results['metrics']['f1']:.4f}")
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

- **Author**: Your Name
- **Email**: your.email@example.com
- **University**: Your University
- **Thesis**: MSc in [Your Field]

## 🙏 Acknowledgments

- Hugging Face for the Transformers library
- PyTorch team for the deep learning framework
- The open-source community for various tools and libraries
- Academic researchers whose work inspired this project

## 📖 References

1. Devlin, J., et al. (2019). BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding.
2. Davidson, T., et al. (2017). Hate Speech Detection on Twitter.
3. Waseem, Z., & Hovy, D. (2016). Hateful Symbols or Hateful People? Predictive Features for Hate Speech Detection on Twitter.

---

**Note**: This is a research project for academic purposes. Please ensure responsible use of hate speech detection technology and consider the ethical implications of automated content moderation.
