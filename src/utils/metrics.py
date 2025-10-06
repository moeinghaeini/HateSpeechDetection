"""
Evaluation metrics and visualization utilities.
"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    confusion_matrix, classification_report, roc_auc_score, roc_curve
)
from typing import List, Dict, Any, Tuple, Optional
import pandas as pd
from pathlib import Path
from loguru import logger


def calculate_metrics(y_true: List[int], y_pred: List[int], 
                     y_prob: Optional[List[float]] = None) -> Dict[str, float]:
    """
    Calculate comprehensive evaluation metrics.
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        y_prob: Predicted probabilities (optional)
        
    Returns:
        Dictionary of metrics
    """
    metrics = {
        'accuracy': accuracy_score(y_true, y_pred),
        'precision': precision_score(y_true, y_pred, average='weighted'),
        'recall': recall_score(y_true, y_pred, average='weighted'),
        'f1': f1_score(y_true, y_pred, average='weighted')
    }
    
    # Add per-class metrics
    precision_per_class = precision_score(y_true, y_pred, average=None)
    recall_per_class = recall_score(y_true, y_pred, average=None)
    f1_per_class = f1_score(y_true, y_pred, average=None)
    
    for i, (p, r, f) in enumerate(zip(precision_per_class, recall_per_class, f1_per_class)):
        metrics[f'precision_class_{i}'] = p
        metrics[f'recall_class_{i}'] = r
        metrics[f'f1_class_{i}'] = f
    
    # Add AUC if probabilities are provided
    if y_prob is not None:
        try:
            metrics['auc'] = roc_auc_score(y_true, y_prob)
        except ValueError:
            logger.warning("Could not calculate AUC - possibly only one class present")
            metrics['auc'] = 0.0
    
    return metrics


def plot_confusion_matrix(y_true: List[int], y_pred: List[int], 
                         class_names: Optional[List[str]] = None,
                         save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot confusion matrix.
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        class_names: Names of classes
        save_path: Path to save the plot
        
    Returns:
        Matplotlib figure
    """
    cm = confusion_matrix(y_true, y_pred)
    
    if class_names is None:
        class_names = [f'Class {i}' for i in range(len(np.unique(y_true)))]
    
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=class_names, yticklabels=class_names, ax=ax)
    ax.set_xlabel('Predicted')
    ax.set_ylabel('Actual')
    ax.set_title('Confusion Matrix')
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Confusion matrix saved to {save_path}")
    
    return fig


def plot_roc_curve(y_true: List[int], y_prob: List[float],
                   class_names: Optional[List[str]] = None,
                   save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot ROC curve.
    
    Args:
        y_true: True labels
        y_prob: Predicted probabilities
        class_names: Names of classes
        save_path: Path to save the plot
        
    Returns:
        Matplotlib figure
    """
    fpr, tpr, _ = roc_curve(y_true, y_prob)
    auc_score = roc_auc_score(y_true, y_prob)
    
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.plot(fpr, tpr, color='darkorange', lw=2, 
            label=f'ROC curve (AUC = {auc_score:.2f})')
    ax.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    ax.set_xlim([0.0, 1.0])
    ax.set_ylim([0.0, 1.05])
    ax.set_xlabel('False Positive Rate')
    ax.set_ylabel('True Positive Rate')
    ax.set_title('Receiver Operating Characteristic (ROC) Curve')
    ax.legend(loc="lower right")
    ax.grid(True, alpha=0.3)
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"ROC curve saved to {save_path}")
    
    return fig


def plot_training_history(history: Dict[str, List[float]], 
                         save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot training history.
    
    Args:
        history: Training history dictionary
        save_path: Path to save the plot
        
    Returns:
        Matplotlib figure
    """
    fig, axes = plt.subplots(1, 2, figsize=(15, 5))
    
    # Plot loss
    axes[0].plot(history.get('train_loss', []), label='Training Loss', color='blue')
    axes[0].plot(history.get('val_loss', []), label='Validation Loss', color='red')
    axes[0].set_xlabel('Epoch')
    axes[0].set_ylabel('Loss')
    axes[0].set_title('Training and Validation Loss')
    axes[0].legend()
    axes[0].grid(True, alpha=0.3)
    
    # Plot accuracy
    axes[1].plot(history.get('train_accuracy', []), label='Training Accuracy', color='blue')
    axes[1].plot(history.get('val_accuracy', []), label='Validation Accuracy', color='red')
    axes[1].set_xlabel('Epoch')
    axes[1].set_ylabel('Accuracy')
    axes[1].set_title('Training and Validation Accuracy')
    axes[1].legend()
    axes[1].grid(True, alpha=0.3)
    
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Training history saved to {save_path}")
    
    return fig


def plot_class_distribution(labels: List[int], class_names: Optional[List[str]] = None,
                           save_path: Optional[str] = None) -> plt.Figure:
    """
    Plot class distribution.
    
    Args:
        labels: List of labels
        class_names: Names of classes
        save_path: Path to save the plot
        
    Returns:
        Matplotlib figure
    """
    if class_names is None:
        class_names = [f'Class {i}' for i in range(len(np.unique(labels)))]
    
    class_counts = pd.Series(labels).value_counts().sort_index()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(class_names, class_counts.values, color=['skyblue', 'lightcoral'])
    ax.set_xlabel('Class')
    ax.set_ylabel('Count')
    ax.set_title('Class Distribution')
    
    # Add count labels on bars
    for bar, count in zip(bars, class_counts.values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.1,
                str(count), ha='center', va='bottom')
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Class distribution saved to {save_path}")
    
    return fig


def generate_classification_report(y_true: List[int], y_pred: List[int],
                                 class_names: Optional[List[str]] = None,
                                 save_path: Optional[str] = None) -> str:
    """
    Generate detailed classification report.
    
    Args:
        y_true: True labels
        y_pred: Predicted labels
        class_names: Names of classes
        save_path: Path to save the report
        
    Returns:
        Classification report string
    """
    if class_names is None:
        class_names = [f'Class {i}' for i in range(len(np.unique(y_true)))]
    
    report = classification_report(y_true, y_pred, target_names=class_names)
    
    if save_path:
        with open(save_path, 'w') as f:
            f.write(report)
        logger.info(f"Classification report saved to {save_path}")
    
    return report


def save_metrics(metrics: Dict[str, float], save_path: str) -> None:
    """
    Save metrics to file.
    
    Args:
        metrics: Dictionary of metrics
        save_path: Path to save metrics
    """
    import json
    
    with open(save_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    logger.info(f"Metrics saved to {save_path}")


def compare_models(results: Dict[str, Dict[str, float]], 
                   metric: str = 'f1',
                   save_path: Optional[str] = None) -> plt.Figure:
    """
    Compare multiple models.
    
    Args:
        results: Dictionary with model names as keys and metrics as values
        metric: Metric to compare
        save_path: Path to save the plot
        
    Returns:
        Matplotlib figure
    """
    model_names = list(results.keys())
    metric_values = [results[model].get(metric, 0) for model in model_names]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(model_names, metric_values, color='lightblue', edgecolor='navy')
    ax.set_xlabel('Model')
    ax.set_ylabel(f'{metric.upper()} Score')
    ax.set_title(f'Model Comparison - {metric.upper()} Score')
    
    # Add value labels on bars
    for bar, value in zip(bars, metric_values):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{value:.3f}', ha='center', va='bottom')
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    if save_path:
        fig.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Model comparison saved to {save_path}")
    
    return fig
