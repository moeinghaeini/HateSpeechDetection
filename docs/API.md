# API Documentation

## Core Modules

### Data Processing

#### `src.data.dataset.HateSpeechDataset`
Custom PyTorch dataset for hate speech detection.

```python
class HateSpeechDataset(Dataset):
    def __init__(self, texts: List[str], labels: List[int], tokenizer, 
                 max_length: int = 512, label_mapping: Optional[Dict[str, int]] = None)
```

**Parameters:**
- `texts`: List of text samples
- `labels`: List of corresponding labels
- `tokenizer`: Tokenizer for text processing
- `max_length`: Maximum sequence length
- `label_mapping`: Optional mapping from label names to integers

**Methods:**
- `get_class_weights()`: Calculate class weights for imbalanced datasets
- `get_class_distribution()`: Get the distribution of classes
- `to_dataframe()`: Convert dataset to pandas DataFrame

#### `src.data.preprocessing.TextPreprocessor`
Advanced text preprocessing pipeline.

```python
class TextPreprocessor:
    def __init__(self, remove_urls: bool = True, remove_mentions: bool = True,
                 remove_hashtags: bool = False, remove_numbers: bool = False,
                 remove_punctuation: bool = False, lowercase: bool = True,
                 remove_stopwords: bool = False, stem_words: bool = False,
                 lemmatize_words: bool = False, min_length: int = 3,
                 max_length: int = 512)
```

**Methods:**
- `preprocess(text: str) -> str`: Preprocess a single text
- `preprocess_batch(texts: List[str]) -> List[str]`: Preprocess a batch of texts
- `preprocess_dataframe(df: pd.DataFrame, text_column: str) -> pd.DataFrame`: Preprocess DataFrame

### Model Architectures

#### `src.models.hate_speech_classifier.HateSpeechClassifier`
Base hate speech classification model.

```python
class HateSpeechClassifier(nn.Module):
    def __init__(self, model_name: str, num_labels: int = 2, dropout_rate: float = 0.1)
    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor
    def get_embeddings(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> torch.Tensor
```

#### `src.models.hate_speech_classifier.MultiTaskHateSpeechClassifier`
Multi-task hate speech classifier with auxiliary tasks.

```python
class MultiTaskHateSpeechClassifier(nn.Module):
    def __init__(self, model_name: str, num_labels: int = 2, 
                 num_auxiliary_labels: int = 3, dropout_rate: float = 0.1)
    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]
```

#### `src.models.hate_speech_classifier.HierarchicalHateSpeechClassifier`
Hierarchical hate speech classifier with multiple levels.

```python
class HierarchicalHateSpeechClassifier(nn.Module):
    def __init__(self, model_name: str, num_labels: int = 2, 
                 num_categories: int = 5, dropout_rate: float = 0.1)
    def forward(self, input_ids: torch.Tensor, attention_mask: torch.Tensor) -> Tuple[torch.Tensor, torch.Tensor]
```

### Training and Evaluation

#### `src.models.trainer.Trainer`
Training utilities for hate speech detection models.

```python
class Trainer:
    def __init__(self, model: nn.Module, config: Dict[str, Any], 
                 device: torch.device, use_wandb: bool = False)
    def train_epoch(self, train_loader: DataLoader) -> Dict[str, float]
    def validate(self, val_loader: DataLoader) -> Dict[str, float]
    def train(self, train_loader: DataLoader, val_loader: DataLoader) -> Dict[str, List[float]]
```

#### `src.models.evaluator.Evaluator`
Evaluation utilities for hate speech detection models.

```python
class Evaluator:
    def __init__(self, model: nn.Module, device: torch.device, 
                 class_names: Optional[List[str]] = None)
    def evaluate(self, test_loader: DataLoader, save_results: bool = True, 
                results_dir: str = "results") -> Dict[str, Any]
    def evaluate_on_samples(self, texts: List[str], labels: List[int]) -> Dict[str, Any]
    def analyze_errors(self, test_loader: DataLoader, num_samples: int = 10) -> Dict[str, List[Dict[str, Any]]]
```

### Utilities

#### `src.utils.metrics`
Evaluation metrics and visualization utilities.

```python
def calculate_metrics(y_true: List[int], y_pred: List[int], 
                     y_prob: Optional[List[float]] = None) -> Dict[str, float]
def plot_confusion_matrix(y_true: List[int], y_pred: List[int], 
                         class_names: Optional[List[str]] = None,
                         save_path: Optional[str] = None) -> plt.Figure
def plot_roc_curve(y_true: List[int], y_prob: List[float],
                   class_names: Optional[List[str]] = None,
                   save_path: Optional[str] = None) -> plt.Figure
```

#### `src.utils.model_utils`
Model utilities and helper functions.

```python
def get_device(device: str = "auto") -> torch.device
def save_model(model: nn.Module, tokenizer, save_path: str, 
               model_config: Dict[str, Any], metadata: Optional[Dict[str, Any]] = None) -> None
def load_model(model_path: str, device: torch.device) -> Tuple[nn.Module, Any, Dict[str, Any]]
def get_model_size(model: nn.Module) -> Dict[str, int]
```

#### `src.utils.config`
Configuration management utilities.

```python
def load_config(config_path: str = "config/config.yaml") -> Dict[str, Any]
def setup_logging(config: Dict[str, Any]) -> None
```

## Command Line Interface

### Training
```bash
python -m src.cli.train --data data/train.csv --text-column text --label-column label
```

### Evaluation
```bash
python -m src.cli.evaluate --model-path models/bert_model --data data/test.csv
```

### Prediction
```bash
python -m src.cli.predict --model-path models/bert_model --text "This is hate speech"
```

## Configuration

The project uses YAML configuration files. Key sections include:

### Model Configuration
```yaml
model:
  name: "bert-base-uncased"
  num_labels: 2
  dropout_rate: 0.1
  learning_rate: 2e-5
  weight_decay: 0.01
  max_epochs: 10
  batch_size: 16
```

### Data Configuration
```yaml
data:
  raw_data_path: "data/raw"
  processed_data_path: "data/processed"
  train_split: 0.7
  val_split: 0.15
  test_split: 0.15
  max_length: 512
  min_length: 5
```

### Training Configuration
```yaml
training:
  device: "auto"
  mixed_precision: true
  save_best_model: true
  early_stopping_patience: 3
```

## Examples

### Basic Training Example
```python
from src.models.hate_speech_classifier import HateSpeechClassifier
from src.models.trainer import Trainer
from src.data.loaders import DataLoaderFactory

# Initialize model
model = HateSpeechClassifier("bert-base-uncased", num_labels=2)

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

### Custom Evaluation Example
```python
from src.models.evaluator import Evaluator

# Initialize evaluator
evaluator = Evaluator(model, device, class_names=['Non-Hate', 'Hate'])

# Evaluate model
results = evaluator.evaluate(test_loader, save_results=True)

print(f"F1 Score: {results['metrics']['f1']:.4f}")
```

### Text Preprocessing Example
```python
from src.data.preprocessing import TextPreprocessor

# Initialize preprocessor
preprocessor = TextPreprocessor(
    remove_urls=True,
    remove_mentions=True,
    lowercase=True
)

# Preprocess text
text = "This is a hateful comment @user #hate"
processed = preprocessor.preprocess(text)
print(processed)  # "this is a hateful comment"
```
