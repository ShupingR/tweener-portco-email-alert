"""
Database Connection Management
=============================

This module handles SQLite database connections for the Tweener Fund email tracking system.

Provides:
- SQLAlchemy engine and session management
- Database initialization and connection utilities
- Session factory for database operations

Usage:
    from database.connection import SessionLocal, engine
    
    session = SessionLocal()
    # ... database operations ...
    session.close()
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database.models import Base
from database.financial_models import FinancialMetrics, MetricExtraction

# Database configuration
DATABASE_URL = "sqlite:///tracker.db"

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

# Create session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
