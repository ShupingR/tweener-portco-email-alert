# models.py
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, ForeignKey
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class Company(Base):
    __tablename__ = "companies"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    legal_name = Column(String)
    website = Column(String)
    fund = Column(String)
    investment_amount = Column(String)
    investment_state = Column(String)
    completion_date = Column(String)
    founders = Column(Text)
    description = Column(Text)
    is_tweener_portfolio = Column(Boolean, default=True)  # True for Tweener portfolio companies, False for others
    last_update_date = Column(DateTime)  # Track when we last received an update
    # Add more fields as needed

    contacts = relationship("Contact", back_populates="company")
    emails = relationship("EmailUpdate", back_populates="company")

class Contact(Base):
    __tablename__ = "contacts"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    first_name = Column(String)
    last_name = Column(String)
    email = Column(String, nullable=False)
    job_title = Column(String)
    is_primary = Column(Boolean, default=False)
    email_bounced = Column(Boolean, default=False)

    company = relationship("Company", back_populates="contacts")

class EmailUpdate(Base):
    __tablename__ = "email_updates"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    sender = Column(String)
    subject = Column(String)
    body = Column(Text)
    date = Column(DateTime)
    has_attachments = Column(Boolean, default=False)
    processed_at = Column(DateTime, default=datetime.utcnow)

    company = relationship("Company", back_populates="emails")
    attachments = relationship("Attachment", back_populates="email_update")

class Attachment(Base):
    __tablename__ = "attachments"
    id = Column(Integer, primary_key=True)
    email_update_id = Column(Integer, ForeignKey("email_updates.id"))
    filename = Column(String)
    path = Column(String)
    file_size = Column(Integer)

    email_update = relationship("EmailUpdate", back_populates="attachments")

class Alert(Base):
    __tablename__ = "alerts"
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    alert_type = Column(String)  # '1_month', '2_month', '3_month_escalation'
    sent_date = Column(DateTime)
    resolved = Column(Boolean, default=False)
    resolved_date = Column(DateTime)