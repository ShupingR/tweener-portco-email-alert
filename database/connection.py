"""
Database Connection Management
=============================

This module handles SQLite database connections for the Tweener Fund email tracking system.

Provides:
- SQLAlchemy engine and session management
- Database initialization and connection utilities
- Session factory for database operations
- Cloud Storage sync for persistence

Usage:
    from database.connection import SessionLocal, engine
    
    session = SessionLocal()
    # ... database operations ...
    session.close()
"""

import os
import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base
from database.financial_models import FinancialMetrics, MetricExtraction

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = "sqlite:///tracker.db"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Initialize Cloud Storage sync
_db_sync = None

def get_db_sync():
    """Get database sync instance (lazy initialization)"""
    global _db_sync
    if _db_sync is None:
        try:
            from database.storage_sync import DatabaseSync
            _db_sync = DatabaseSync()
        except ImportError as e:
            logger.warning(f"Cloud Storage sync not available: {e}")
            _db_sync = None
    return _db_sync

def init_db():
    """Initialize database with Cloud Storage sync"""
    # Try to sync data from cloud storage first
    db_sync = get_db_sync()
    if db_sync:
        try:
            db_downloaded, attachments_downloaded = db_sync.sync_on_startup()
            if db_downloaded:
                logger.info("Using database from Cloud Storage")
            else:
                logger.info("No database found in Cloud Storage, creating new one")
        except Exception as e:
            logger.warning(f"Cloud Storage sync failed: {e}")
    
    # Create tables (this won't overwrite existing data)
    Base.metadata.create_all(bind=engine)

def sync_to_cloud():
    """Sync current database state to Cloud Storage"""
    db_sync = get_db_sync()
    if db_sync:
        try:
            success = db_sync.sync_on_changes()
            if success:
                logger.info("Successfully synced database to Cloud Storage")
            else:
                logger.warning("Failed to sync database to Cloud Storage")
            return success
        except Exception as e:
            logger.error(f"Error syncing to Cloud Storage: {e}")
            return False
    return False

def upload_attachment_to_cloud(attachment_path):
    """Upload a single attachment to Cloud Storage"""
    db_sync = get_db_sync()
    if db_sync and os.path.exists(attachment_path):
        try:
            return db_sync.upload_single_attachment(attachment_path)
        except Exception as e:
            logger.error(f"Error uploading attachment to Cloud Storage: {e}")
    return False
