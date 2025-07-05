"""
External Service Integrations
=============================

This module contains clients for external services used by the email tracking system.

Components:
- gmail_client.py - Gmail IMAP/SMTP connectivity and email operations
- claude_client.py - Anthropic Claude AI integration for email analysis

These modules provide clean interfaces to external APIs and handle authentication,
error handling, and rate limiting.

Usage:
    from integrations.gmail_client import GmailClient
    from integrations.claude_client import ClaudeClient
"""

__version__ = "1.0.0" 