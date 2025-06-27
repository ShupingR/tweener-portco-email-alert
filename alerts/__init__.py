"""
Portfolio Company Alert System
=============================

This module handles monitoring portfolio companies and sending automated alerts
when updates are missing.

Components:
- alert_manager.py - Main alert logic and email sending

Alert Thresholds:
- 31 days: 1-month reminder
- 62 days: 2-month reminder  
- 93 days: 3-month escalation to GPs

Usage:
    from alerts.alert_manager import AlertManager
    
    manager = AlertManager()
    manager.check_and_send_alerts()
"""

__version__ = "1.0.0" 