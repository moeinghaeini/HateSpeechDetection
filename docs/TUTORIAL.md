# Tutorial: Getting Started with Hate Speech Detection

This tutorial will guide you through setting up and using the hate speech detection framework for your MSc thesis project.

## Table of Contents

1. [Installation and Setup](#installation-and-setup)
2. [Data Preparation](#data-preparation)
3. [Model Training](#model-training)
4. [Model Evaluation](#model-evaluation)
5. [Making Predictions](#making-predictions)
6. [Advanced Features](#advanced-features)
7. [Troubleshooting](#troubleshooting)

## Installation and Setup

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/HateSpeechDetection.git
cd HateSpeechDetection
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
pip install -e .
```

### 4. Download NLTK Data

```python
import nltk
nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
```

## Data Preparation

### 1. Data Format

Your dataset should be in CSV or JSON format with at least two columns:
- Text column (e.g., 'text', 'comment', 'tweet')
- Label column (e.g., 'label', 'class', 'hate')

Example CSV format:
```csv
text,label
"This is a normal comment",0
"This is hate speech",1
"Another normal comment",0
```

### 2. Data Preprocessing

The framework provides advanced text preprocessing:

```python
from src.data.preprocessing import TextPreprocessor

# Initialize preprocessor
preprocessor = TextPreprocessor(
    remove_urls=True,
    remove_mentions=True,
    remove_hashtags=False,
    lowercase=True,
    remove_stopwords=False
)

# Preprocess a single text
text = "This is a hateful comment @user #hate http://example.com"
processed = preprocessor.preprocess(text)
print(processed)  # "this is a hateful comment"
```

### 3. Data Loading

```python
from src.data.loaders import DataLoaderFactory

# Initialize data loader factory
data_factory = DataLoaderFactory(
    tokenizer_name="bert-base-uncased",
    max_length=512,
    batch_size=16
)

# Load data
train_loader, val_loader, test_loader = data_factory.load_from_csv(
    "data/train.csv",
    text_column="text",
    label_column="label"
)
```

## Model Training

### 1. Basic Training

```bash
python -m src.cli.train \
    --data data/train.csv \
    --text-column text \
    --label-column label \
    --model-name bert-base-uncased \
    --output-dir models/bert_model
```

### 2. Advanced Training with Custom Configuration

Create a custom configuration file:

```yaml
# config/custom_config.yaml
model:
  name: "bert-base-uncased"
  num_labels: 2
  dropout_rate: 0.1
  learning_rate: 2e-5
  weight_decay: 0.01
  max_epochs: 10
  batch_size: 16

data:
  max_length: 512
  min_length: 5
  remove_urls: true
  remove_mentions: true

training:
  device: "auto"
  mixed_precision: true
  early_stopping_patience: 3
```

Train with custom configuration:

```bash
python -m src.cli.train \
    --config config/custom_config.yaml \
    --data data/train.csv \
    --text-column text \
    --label-column label \
    --output-dir models/custom_model
```

### 3. Training with Weights & Biases

```bash
python -m src.cli.train \
    --data data/train.csv \
    --text-column text \
    --label-column label \
    --use-wandb \
    --output-dir models/bert_model
```

### 4. Training with Dataset Balancing

```bash
python -m src.cli.train \
    --data data/train.csv \
    --text-column text \
    --label-column label \
    --balance-dataset \
    --balance-method undersample \
    --output-dir models/balanced_model
```

## Model Evaluation

### 1. Basic Evaluation

```bash
python -m src.cli.evaluate \
    --model-path models/bert_model \
    --data data/test.csv \
    --text-column text \
    --label-column label \
    --output-dir results/
```

### 2. Custom Evaluation

```python
from src.models.evaluator import Evaluator
from src.utils.model_utils import load_model
import torch

# Load model
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model, tokenizer, config = load_model("models/bert_model", device)

# Initialize evaluator
evaluator = Evaluator(model, device, class_names=['Non-Hate', 'Hate'])

# Evaluate model
results = evaluator.evaluate(test_loader, save_results=True)

# Print results
print(f"Accuracy: {results['metrics']['accuracy']:.4f}")
print(f"F1 Score: {results['metrics']['f1']:.4f}")
print(f"Precision: {results['metrics']['precision']:.4f}")
print(f"Recall: {results['metrics']['recall']:.4f}")
```

### 3. Error Analysis

```python
# Analyze prediction errors
errors = evaluator.analyze_errors(test_loader, num_samples=10)

print("False Positives:")
for error in errors['false_positives']:
    print(f"Prediction: {error['prediction']}, True: {error['true_label']}")

print("False Negatives:")
for error in errors['false_negatives']:
    print(f"Prediction: {error['prediction']}, True: {error['true_label']}")
```

## Making Predictions

### 1. Single Text Prediction

```bash
python -m src.cli.predict \
    --model-path models/bert_model \
    --text "This is a hateful comment" \
    --output-file prediction.json
```

### 2. Batch Prediction

```bash
python -m src.cli.predict \
    --model-path models/bert_model \
    --input-file data/test_texts.json \
    --output-file predictions.json
```

### 3. Custom Prediction

```python
from src.utils.model_utils import load_model
from transformers import AutoTokenizer
import torch

# Load model
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model, tokenizer, config = load_model("models/bert_model", device)

# Prepare text
text = "This is a hateful comment"
encoding = tokenizer(
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
    
    print(f"Prediction: {prediction.item()}")
    print(f"Probabilities: {probabilities.cpu().numpy()}")
```

## Advanced Features

### 1. Multi-Task Learning

```python
from src.models.hate_speech_classifier import MultiTaskHateSpeechClassifier

# Initialize multi-task model
model = MultiTaskHateSpeechClassifier(
    model_name="bert-base-uncased",
    num_labels=2,
    num_auxiliary_labels=3,
    dropout_rate=0.1
)

# Training with auxiliary tasks
# (Implementation depends on your specific auxiliary tasks)
```

### 2. Hierarchical Classification

```python
from src.models.hate_speech_classifier import HierarchicalHateSpeechClassifier

# Initialize hierarchical model
model = HierarchicalHateSpeechClassifier(
    model_name="bert-base-uncased",
    num_labels=2,
    num_categories=5,
    dropout_rate=0.1
)
```

### 3. Attention Visualization

```python
# Get attention weights for a text
attention_weights = evaluator.get_attention_weights(
    "This is a hateful comment",
    layer_idx=-1
)

# Visualize attention weights
import matplotlib.pyplot as plt
plt.imshow(attention_weights, cmap='Blues')
plt.title('Attention Weights')
plt.show()
```

### 4. Cross-Validation

```python
from src.data.loaders import DataLoaderFactory

# Create cross-validation splits
data_factory = DataLoaderFactory("bert-base-uncased")
cv_splits = data_factory.create_cross_validation_splits(
    df, text_column="text", label_column="label", n_splits=5
)

# Train on each split
for i, (train_loader, val_loader) in enumerate(cv_splits):
    print(f"Training on fold {i+1}")
    # Train model on this fold
    # ...
```

### 5. Model Comparison

```python
from src.models.evaluator import Evaluator

# Compare multiple models
models = {
    'BERT': bert_model,
    'RoBERTa': roberta_model,
    'Custom': custom_model
}

comparison_results = evaluator.compare_models(models, test_loader)

for model_name, metrics in comparison_results.items():
    print(f"{model_name}: F1={metrics['f1']:.4f}")
```

## Troubleshooting

### Common Issues

1. **CUDA Out of Memory**
   - Reduce batch size in configuration
   - Use gradient accumulation
   - Enable mixed precision training

2. **Data Loading Issues**
   - Check file format (CSV/JSON)
   - Verify column names
   - Ensure text column contains strings

3. **Model Loading Issues**
   - Check model path exists
   - Verify model was saved correctly
   - Ensure compatible PyTorch version

4. **Training Issues**
   - Check learning rate (try 2e-5 for BERT)
   - Verify data preprocessing
   - Check for class imbalance

### Performance Optimization

1. **Use Mixed Precision Training**
   ```yaml
   training:
     mixed_precision: true
   ```

2. **Enable Gradient Accumulation**
   ```yaml
   model:
     gradient_accumulation_steps: 2
   ```

3. **Use Data Parallel Training**
   ```python
   model = torch.nn.DataParallel(model)
   ```

### Debugging Tips

1. **Enable Detailed Logging**
   ```yaml
   logging:
     level: "DEBUG"
   ```

2. **Save Model Checkpoints**
   ```yaml
   training:
     save_best_model: true
     save_last_model: true
   ```

3. **Monitor Training Progress**
   ```bash
   tensorboard --logdir tensorboard_logs
   ```

## Next Steps

1. **Experiment with Different Models**: Try RoBERTa, DistilBERT, or custom architectures
2. **Hyperparameter Tuning**: Use Optuna or similar tools for optimization
3. **Data Augmentation**: Implement text augmentation techniques
4. **Ensemble Methods**: Combine multiple models for better performance
5. **Deployment**: Create API endpoints for real-time prediction

## Resources

- [PyTorch Documentation](https://pytorch.org/docs/)
- [Transformers Library](https://huggingface.co/transformers/)
- [Weights & Biases](https://wandb.ai/)
- [TensorBoard](https://www.tensorflow.org/tensorboard)

For more advanced usage and research applications, refer to the [API Documentation](API.md) and [Research Examples](RESEARCH.md).
