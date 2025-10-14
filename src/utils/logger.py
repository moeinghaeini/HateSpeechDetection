"""
Advanced logging system for the Hate Speech Detection project.
Provides structured logging with multiple outputs and monitoring integration.
"""

import logging
import sys
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional
from loguru import logger
import structlog
from rich.console import Console
from rich.logging import RichHandler


class StructuredLogger:
    """Advanced structured logging system with multiple outputs."""
    
    def __init__(self, 
                 log_level: str = "INFO",
                 log_dir: str = "logs",
                 enable_console: bool = True,
                 enable_file: bool = True,
                 enable_json: bool = True):
        
        self.log_level = log_level.upper()
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Configure loguru
        self._setup_loguru()
        
        # Configure structlog
        self._setup_structlog()
        
        # Configure standard logging
        self._setup_standard_logging()
    
    def _setup_loguru(self):
        """Configure loguru logger with multiple outputs."""
        # Remove default handler
        logger.remove()
        
        # Console output with colors
        logger.add(
            sys.stdout,
            level=self.log_level,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                   "<level>{level: <8}</level> | "
                   "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
                   "<level>{message}</level>",
            colorize=True,
            backtrace=True,
            diagnose=True
        )
        
        # File output with rotation
        logger.add(
            self.log_dir / "application.log",
            level=self.log_level,
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            rotation="100 MB",
            retention="30 days",
            compression="zip",
            backtrace=True,
            diagnose=True
        )
        
        # Error file output
        logger.add(
            self.log_dir / "errors.log",
            level="ERROR",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            rotation="50 MB",
            retention="90 days",
            compression="zip",
            backtrace=True,
            diagnose=True
        )
        
        # JSON output for structured logging
        logger.add(
            self.log_dir / "structured.json",
            level=self.log_level,
            format=lambda record: json.dumps({
                "timestamp": record["time"].isoformat(),
                "level": record["level"].name,
                "logger": record["name"],
                "function": record["function"],
                "line": record["line"],
                "message": record["message"],
                "extra": record.get("extra", {})
            }),
            rotation="100 MB",
            retention="30 days",
            compression="zip"
        )
    
    def _setup_structlog(self):
        """Configure structlog for structured logging."""
        structlog.configure(
            processors=[
                structlog.stdlib.filter_by_level,
                structlog.stdlib.add_logger_name,
                structlog.stdlib.add_log_level,
                structlog.stdlib.PositionalArgumentsFormatter(),
                structlog.processors.TimeStamper(fmt="iso"),
                structlog.processors.StackInfoRenderer(),
                structlog.processors.format_exc_info,
                structlog.processors.UnicodeDecoder(),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True,
        )
    
    def _setup_standard_logging(self):
        """Configure standard Python logging."""
        # Create console handler with Rich
        console = Console()
        rich_handler = RichHandler(console=console, rich_tracebacks=True)
        rich_handler.setLevel(getattr(logging, self.log_level))
        
        # Configure root logger
        logging.basicConfig(
            level=getattr(logging, self.log_level),
            format="%(message)s",
            datefmt="[%X]",
            handlers=[rich_handler]
        )
    
    def get_logger(self, name: str) -> Any:
        """Get a logger instance."""
        return logger.bind(name=name)
    
    def get_structured_logger(self, name: str):
        """Get a structured logger instance."""
        return structlog.get_logger(name)


class DataQualityLogger:
    """Specialized logger for data quality monitoring."""
    
    def __init__(self, base_logger: StructuredLogger):
        self.logger = base_logger.get_logger("data_quality")
        self.structured_logger = base_logger.get_structured_logger("data_quality")
    
    def log_data_quality_check(self, 
                              check_name: str,
                              status: str,
                              details: Dict[str, Any],
                              record_count: int = None):
        """Log data quality check results."""
        log_data = {
            "check_name": check_name,
            "status": status,
            "details": details,
            "record_count": record_count,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if status == "PASS":
            self.logger.info(f"Data quality check passed: {check_name}", **log_data)
        elif status == "WARN":
            self.logger.warning(f"Data quality check warning: {check_name}", **log_data)
        else:
            self.logger.error(f"Data quality check failed: {check_name}", **log_data)
    
    def log_pipeline_metrics(self, 
                           pipeline_name: str,
                           metrics: Dict[str, Any],
                           duration: float = None):
        """Log pipeline execution metrics."""
        log_data = {
            "pipeline_name": pipeline_name,
            "metrics": metrics,
            "duration_seconds": duration,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"Pipeline metrics: {pipeline_name}", **log_data)


class ModelLogger:
    """Specialized logger for AI/ML model operations."""
    
    def __init__(self, base_logger: StructuredLogger):
        self.logger = base_logger.get_logger("model")
        self.structured_logger = base_logger.get_structured_logger("model")
    
    def log_model_prediction(self,
                           model_name: str,
                           input_text: str,
                           prediction: str,
                           confidence: float,
                           processing_time: float = None):
        """Log model prediction results."""
        log_data = {
            "model_name": model_name,
            "input_length": len(input_text),
            "prediction": prediction,
            "confidence": confidence,
            "processing_time": processing_time,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"Model prediction: {model_name}", **log_data)
    
    def log_model_performance(self,
                            model_name: str,
                            metrics: Dict[str, float],
                            dataset_size: int = None):
        """Log model performance metrics."""
        log_data = {
            "model_name": model_name,
            "metrics": metrics,
            "dataset_size": dataset_size,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"Model performance: {model_name}", **log_data)


class APILogger:
    """Specialized logger for API operations."""
    
    def __init__(self, base_logger: StructuredLogger):
        self.logger = base_logger.get_logger("api")
        self.structured_logger = base_logger.get_structured_logger("api")
    
    def log_api_request(self,
                       endpoint: str,
                       method: str,
                       status_code: int,
                       response_time: float,
                       user_id: str = None):
        """Log API request details."""
        log_data = {
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "response_time": response_time,
            "user_id": user_id,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        if 200 <= status_code < 300:
            self.logger.info(f"API request: {method} {endpoint}", **log_data)
        elif 400 <= status_code < 500:
            self.logger.warning(f"API client error: {method} {endpoint}", **log_data)
        else:
            self.logger.error(f"API server error: {method} {endpoint}", **log_data)
    
    def log_rate_limit(self, endpoint: str, limit: int, remaining: int):
        """Log API rate limit information."""
        log_data = {
            "endpoint": endpoint,
            "limit": limit,
            "remaining": remaining,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        self.logger.info(f"Rate limit status: {endpoint}", **log_data)


# Global logger instances
_structured_logger = StructuredLogger()
data_quality_logger = DataQualityLogger(_structured_logger)
model_logger = ModelLogger(_structured_logger)
api_logger = APILogger(_structured_logger)


def get_logger(name: str):
    """Get a logger instance."""
    return _structured_logger.get_logger(name)


def get_structured_logger(name: str):
    """Get a structured logger instance."""
    return _structured_logger.get_structured_logger(name)


# Convenience functions
def log_data_quality(check_name: str, status: str, details: Dict[str, Any], record_count: int = None):
    """Log data quality check results."""
    data_quality_logger.log_data_quality_check(check_name, status, details, record_count)


def log_pipeline_metrics(pipeline_name: str, metrics: Dict[str, Any], duration: float = None):
    """Log pipeline execution metrics."""
    data_quality_logger.log_pipeline_metrics(pipeline_name, metrics, duration)


def log_model_prediction(model_name: str, input_text: str, prediction: str, confidence: float, processing_time: float = None):
    """Log model prediction results."""
    model_logger.log_model_prediction(model_name, input_text, prediction, confidence, processing_time)


def log_api_request(endpoint: str, method: str, status_code: int, response_time: float, user_id: str = None):
    """Log API request details."""
    api_logger.log_api_request(endpoint, method, status_code, response_time, user_id)


if __name__ == "__main__":
    # Test logging system
    logger = get_logger("test")
    
    logger.info("Testing basic logging")
    logger.warning("Testing warning logging")
    logger.error("Testing error logging")
    
    # Test structured logging
    structured = get_structured_logger("test")
    structured.info("Testing structured logging", extra_data={"key": "value"})
    
    # Test specialized loggers
    log_data_quality("test_check", "PASS", {"completeness": 0.95}, 1000)
    log_model_prediction("test_model", "sample text", "hate_speech", 0.85, 0.5)
    log_api_request("/api/test", "GET", 200, 0.1, "user123")
