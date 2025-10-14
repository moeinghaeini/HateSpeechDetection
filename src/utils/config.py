"""
Configuration management for the Hate Speech Detection project.
Handles environment variables, configuration files, and settings.
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from dotenv import load_dotenv
from pydantic import BaseSettings, Field


class DatabaseConfig(BaseSettings):
    """Database configuration settings."""
    url: str = Field(..., env="DATABASE_URL")
    redis_url: str = Field(..., env="REDIS_URL")
    mongodb_url: str = Field(..., env="MONGODB_URL")
    pool_size: int = Field(10, env="DB_POOL_SIZE")
    max_overflow: int = Field(20, env="DB_MAX_OVERFLOW")
    
    class Config:
        env_file = ".env"


class APIConfig(BaseSettings):
    """API configuration settings."""
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    google_api_key: str = Field(..., env="GOOGLE_API_KEY")
    twitter_api_key: str = Field(..., env="TWITTER_API_KEY")
    twitter_api_secret: str = Field(..., env="TWITTER_API_SECRET")
    twitter_access_token: str = Field(..., env="TWITTER_ACCESS_TOKEN")
    twitter_access_token_secret: str = Field(..., env="TWITTER_ACCESS_TOKEN_SECRET")
    facebook_app_id: str = Field(..., env="FACEBOOK_APP_ID")
    facebook_app_secret: str = Field(..., env="FACEBOOK_APP_SECRET")
    instagram_access_token: str = Field(..., env="INSTAGRAM_ACCESS_TOKEN")
    
    class Config:
        env_file = ".env"


class ModelConfig(BaseSettings):
    """AI/ML model configuration settings."""
    confidence_threshold: float = Field(0.8, env="MODEL_CONFIDENCE_THRESHOLD")
    ensemble_voting_threshold: float = Field(0.6, env="ENSEMBLE_VOTING_THRESHOLD")
    max_tokens: int = Field(2048, env="MAX_TOKENS")
    temperature: float = Field(0.1, env="TEMPERATURE")
    batch_size: int = Field(1000, env="BATCH_SIZE")
    max_retries: int = Field(3, env="MAX_RETRIES")
    retry_delay: int = Field(5, env="RETRY_DELAY")
    
    class Config:
        env_file = ".env"


class AppConfig(BaseSettings):
    """Application configuration settings."""
    flask_env: str = Field("development", env="FLASK_ENV")
    flask_debug: bool = Field(True, env="FLASK_DEBUG")
    secret_key: str = Field(..., env="SECRET_KEY")
    api_rate_limit: int = Field(1000, env="API_RATE_LIMIT")
    log_level: str = Field("INFO", env="LOG_LEVEL")
    upload_folder: str = Field("./data/raw/manual_uploads", env="UPLOAD_FOLDER")
    max_file_size: str = Field("100MB", env="MAX_FILE_SIZE")
    allowed_extensions: str = Field("csv,xlsx,json,txt", env="ALLOWED_EXTENSIONS")
    
    class Config:
        env_file = ".env"


class ConfigManager:
    """Central configuration manager for the application."""
    
    def __init__(self, config_dir: str = "config"):
        self.config_dir = Path(config_dir)
        self._load_env()
        self._load_yaml_configs()
        
        # Initialize configuration objects
        self.database = DatabaseConfig()
        self.api = APIConfig()
        self.model = ModelConfig()
        self.app = AppConfig()
    
    def _load_env(self):
        """Load environment variables from .env file."""
        env_file = Path(".env")
        if env_file.exists():
            load_dotenv(env_file)
    
    def _load_yaml_configs(self):
        """Load YAML configuration files."""
        self.yaml_configs = {}
        
        if self.config_dir.exists():
            for yaml_file in self.config_dir.glob("*.yaml"):
                with open(yaml_file, 'r') as f:
                    self.yaml_configs[yaml_file.stem] = yaml.safe_load(f)
    
    def get_yaml_config(self, config_name: str) -> Dict[str, Any]:
        """Get YAML configuration by name."""
        return self.yaml_configs.get(config_name, {})
    
    def get_database_config(self) -> Dict[str, Any]:
        """Get database configuration."""
        return {
            "url": self.database.url,
            "redis_url": self.database.redis_url,
            "mongodb_url": self.database.mongodb_url,
            "pool_size": self.database.pool_size,
            "max_overflow": self.database.max_overflow
        }
    
    def get_api_config(self) -> Dict[str, Any]:
        """Get API configuration."""
        return {
            "openai_api_key": self.api.openai_api_key,
            "google_api_key": self.api.google_api_key,
            "twitter_api_key": self.api.twitter_api_key,
            "twitter_api_secret": self.api.twitter_api_secret,
            "twitter_access_token": self.api.twitter_access_token,
            "twitter_access_token_secret": self.api.twitter_access_token_secret,
            "facebook_app_id": self.api.facebook_app_id,
            "facebook_app_secret": self.api.facebook_app_secret,
            "instagram_access_token": self.api.instagram_access_token
        }
    
    def get_model_config(self) -> Dict[str, Any]:
        """Get model configuration."""
        return {
            "confidence_threshold": self.model.confidence_threshold,
            "ensemble_voting_threshold": self.model.ensemble_voting_threshold,
            "max_tokens": self.model.max_tokens,
            "temperature": self.model.temperature,
            "batch_size": self.model.batch_size,
            "max_retries": self.model.max_retries,
            "retry_delay": self.model.retry_delay
        }
    
    def get_app_config(self) -> Dict[str, Any]:
        """Get application configuration."""
        return {
            "flask_env": self.app.flask_env,
            "flask_debug": self.app.flask_debug,
            "secret_key": self.app.secret_key,
            "api_rate_limit": self.app.api_rate_limit,
            "log_level": self.app.log_level,
            "upload_folder": self.app.upload_folder,
            "max_file_size": self.app.max_file_size,
            "allowed_extensions": self.app.allowed_extensions.split(",")
        }
    
    def validate_config(self) -> bool:
        """Validate all configuration settings."""
        try:
            # Check required environment variables
            required_vars = [
                "DATABASE_URL", "OPENAI_API_KEY", "GOOGLE_API_KEY",
                "SECRET_KEY"
            ]
            
            for var in required_vars:
                if not os.getenv(var):
                    raise ValueError(f"Required environment variable {var} is not set")
            
            # Validate configuration objects
            self.database.model_validate(self.database.dict())
            self.api.model_validate(self.api.dict())
            self.model.model_validate(self.model.dict())
            self.app.model_validate(self.app.dict())
            
            return True
            
        except Exception as e:
            print(f"Configuration validation failed: {e}")
            return False


# Global configuration instance
config = ConfigManager()


def get_config() -> ConfigManager:
    """Get the global configuration instance."""
    return config


def reload_config():
    """Reload configuration from files."""
    global config
    config = ConfigManager()


if __name__ == "__main__":
    # Test configuration loading
    cfg = get_config()
    
    print("Database Config:", cfg.get_database_config())
    print("API Config Keys:", list(cfg.get_api_config().keys()))
    print("Model Config:", cfg.get_model_config())
    print("App Config:", cfg.get_app_config())
    
    print("Configuration validation:", cfg.validate_config())
