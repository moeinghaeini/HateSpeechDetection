"""
Database schema management for the Hate Speech Detection project.
Handles database creation, migrations, and schema validation.
"""

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
import uuid
from typing import Dict, Any, List
from src.utils.logger import get_logger

logger = get_logger(__name__)

Base = declarative_base()


class SocialMediaPost(Base):
    """Raw social media posts table."""
    __tablename__ = 'social_media_posts'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    platform = Column(String(50), nullable=False)  # twitter, facebook, instagram, tiktok
    post_id = Column(String(255), unique=True, nullable=False)
    user_id = Column(String(255), nullable=True)
    username = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    language = Column(String(10), default='it')
    created_at = Column(DateTime, nullable=False)
    collected_at = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSONB, nullable=True)  # Additional platform-specific data
    is_processed = Column(Boolean, default=False)
    
    # Relationships
    classifications = relationship("HateSpeechClassification", back_populates="post")
    
    # Indexes
    __table_args__ = (
        Index('idx_platform_post_id', 'platform', 'post_id'),
        Index('idx_created_at', 'created_at'),
        Index('idx_is_processed', 'is_processed'),
    )


class HateSpeechClassification(Base):
    """Hate speech classification results table."""
    __tablename__ = 'hate_speech_classifications'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey('social_media_posts.id'), nullable=False)
    model_name = Column(String(100), nullable=False)  # gpt4o, gemini, bert
    label = Column(String(50), nullable=False)  # hate_speech, hatespeech_stereotype, stereotype, normal
    target_group = Column(String(100), nullable=True)  # ebrei, islam, migrazione, genere, etc.
    directness = Column(String(20), nullable=True)  # direct, indirect
    confidence_score = Column(Float, nullable=False)
    keywords = Column(JSONB, nullable=True)  # Extracted keywords
    explanation = Column(Text, nullable=True)  # Model explanation
    processing_time = Column(Float, nullable=True)  # Processing time in seconds
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    post = relationship("SocialMediaPost", back_populates="classifications")
    
    # Indexes
    __table_args__ = (
        Index('idx_post_id', 'post_id'),
        Index('idx_model_name', 'model_name'),
        Index('idx_label', 'label'),
        Index('idx_target_group', 'target_group'),
        Index('idx_confidence_score', 'confidence_score'),
    )


class EnsembleVoting(Base):
    """Ensemble voting results table."""
    __tablename__ = 'ensemble_voting'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    post_id = Column(UUID(as_uuid=True), ForeignKey('social_media_posts.id'), nullable=False)
    final_label = Column(String(50), nullable=False)
    final_confidence = Column(Float, nullable=False)
    voting_results = Column(JSONB, nullable=False)  # Individual model votes
    consensus_score = Column(Float, nullable=False)  # Agreement level
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_post_id', 'post_id'),
        Index('idx_final_label', 'final_label'),
        Index('idx_consensus_score', 'consensus_score'),
    )


class DataQualityMetrics(Base):
    """Data quality metrics table."""
    __tablename__ = 'data_quality_metrics'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    check_name = Column(String(100), nullable=False)
    check_type = Column(String(50), nullable=False)  # completeness, accuracy, consistency, validity
    status = Column(String(20), nullable=False)  # PASS, WARN, FAIL
    score = Column(Float, nullable=True)
    details = Column(JSONB, nullable=True)
    record_count = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_check_name', 'check_name'),
        Index('idx_check_type', 'check_type'),
        Index('idx_status', 'status'),
        Index('idx_created_at', 'created_at'),
    )


class ModelPerformance(Base):
    """Model performance metrics table."""
    __tablename__ = 'model_performance'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    model_name = Column(String(100), nullable=False)
    metric_name = Column(String(100), nullable=False)  # accuracy, precision, recall, f1
    metric_value = Column(Float, nullable=False)
    dataset_size = Column(Integer, nullable=True)
    evaluation_date = Column(DateTime, default=datetime.utcnow)
    metadata = Column(JSONB, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_model_name', 'model_name'),
        Index('idx_metric_name', 'metric_name'),
        Index('idx_evaluation_date', 'evaluation_date'),
    )


class UserSession(Base):
    """User session management table."""
    __tablename__ = 'user_sessions'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=False)
    session_token = Column(String(500), unique=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    expires_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, default=True)
    metadata = Column(JSONB, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
        Index('idx_session_token', 'session_token'),
        Index('idx_expires_at', 'expires_at'),
    )


class AuditLog(Base):
    """Audit logging table."""
    __tablename__ = 'audit_logs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(String(255), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(100), nullable=False)
    resource_id = Column(String(255), nullable=True)
    details = Column(JSONB, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Indexes
    __table_args__ = (
        Index('idx_user_id', 'user_id'),
        Index('idx_action', 'action'),
        Index('idx_resource_type', 'resource_type'),
        Index('idx_created_at', 'created_at'),
    )


class SchemaManager:
    """Database schema management class."""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_engine(database_url, echo=False)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        self.metadata = MetaData()
    
    def create_all_tables(self):
        """Create all database tables."""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("All database tables created successfully")
            return True
        except Exception as e:
            logger.error(f"Error creating database tables: {e}")
            return False
    
    def drop_all_tables(self):
        """Drop all database tables."""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.info("All database tables dropped successfully")
            return True
        except Exception as e:
            logger.error(f"Error dropping database tables: {e}")
            return False
    
    def get_session(self):
        """Get database session."""
        return self.SessionLocal()
    
    def validate_schema(self) -> Dict[str, Any]:
        """Validate database schema."""
        validation_results = {
            "status": "PASS",
            "tables": {},
            "errors": []
        }
        
        try:
            # Check if all tables exist
            inspector = self.engine.dialect.inspector(self.engine)
            existing_tables = inspector.get_table_names()
            
            expected_tables = [
                'social_media_posts',
                'hate_speech_classifications',
                'ensemble_voting',
                'data_quality_metrics',
                'model_performance',
                'user_sessions',
                'audit_logs'
            ]
            
            for table_name in expected_tables:
                if table_name in existing_tables:
                    validation_results["tables"][table_name] = "EXISTS"
                else:
                    validation_results["tables"][table_name] = "MISSING"
                    validation_results["errors"].append(f"Table {table_name} is missing")
            
            if validation_results["errors"]:
                validation_results["status"] = "FAIL"
            
            logger.info(f"Schema validation completed: {validation_results['status']}")
            return validation_results
            
        except Exception as e:
            logger.error(f"Error validating schema: {e}")
            validation_results["status"] = "ERROR"
            validation_results["errors"].append(str(e))
            return validation_results
    
    def get_table_info(self, table_name: str) -> Dict[str, Any]:
        """Get detailed information about a table."""
        try:
            inspector = self.engine.dialect.inspector(self.engine)
            
            if table_name not in inspector.get_table_names():
                return {"error": f"Table {table_name} does not exist"}
            
            columns = inspector.get_columns(table_name)
            indexes = inspector.get_indexes(table_name)
            foreign_keys = inspector.get_foreign_keys(table_name)
            
            return {
                "table_name": table_name,
                "columns": columns,
                "indexes": indexes,
                "foreign_keys": foreign_keys
            }
            
        except Exception as e:
            logger.error(f"Error getting table info for {table_name}: {e}")
            return {"error": str(e)}
    
    def get_database_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        try:
            session = self.get_session()
            
            stats = {}
            
            # Get table row counts
            tables = [
                'social_media_posts',
                'hate_speech_classifications',
                'ensemble_voting',
                'data_quality_metrics',
                'model_performance',
                'user_sessions',
                'audit_logs'
            ]
            
            for table in tables:
                try:
                    result = session.execute(f"SELECT COUNT(*) FROM {table}")
                    count = result.scalar()
                    stats[table] = count
                except Exception as e:
                    stats[table] = f"Error: {e}"
            
            session.close()
            return stats
            
        except Exception as e:
            logger.error(f"Error getting database stats: {e}")
            return {"error": str(e)}


def create_schema_manager(database_url: str) -> SchemaManager:
    """Create a schema manager instance."""
    return SchemaManager(database_url)


if __name__ == "__main__":
    # Test schema management
    from src.utils.config import get_config
    
    config = get_config()
    db_config = config.get_database_config()
    
    schema_manager = create_schema_manager(db_config["url"])
    
    # Create tables
    schema_manager.create_all_tables()
    
    # Validate schema
    validation = schema_manager.validate_schema()
    print("Schema validation:", validation)
    
    # Get database stats
    stats = schema_manager.get_database_stats()
    print("Database stats:", stats)
