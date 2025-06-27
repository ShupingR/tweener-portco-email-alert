"""
Tweener Fund Database Layer
==========================

This module handles all data persistence for the email tracking system.

Components:
- models.py - Core database models (Company, Contact, EmailUpdate, etc.)
- financial_models.py - Financial metrics specific models
- connection.py - Database connection and session management
- migrations/ - Database schema updates and setup scripts

Database: SQLite (tracker.db)
ORM: SQLAlchemy

Usage:
    from database.connection import SessionLocal
    from database.models import Company, EmailUpdate
"""

__version__ = "1.0.0" 