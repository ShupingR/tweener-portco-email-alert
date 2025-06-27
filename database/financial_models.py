# financial_metrics_models.py
from sqlalchemy import (
    Column, Integer, String, Text, DateTime, Boolean, ForeignKey, Float, Numeric
)
from sqlalchemy.orm import relationship
from models import Base
from datetime import datetime
from decimal import Decimal

class FinancialMetrics(Base):
    __tablename__ = "financial_metrics"
    
    id = Column(Integer, primary_key=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    email_update_id = Column(Integer, ForeignKey("email_updates.id"), nullable=True)
    
    # Reporting period information
    reporting_period = Column(String)  # e.g., "Q1 2025", "May 2025", "2024 Annual"
    reporting_date = Column(DateTime)  # When the metrics are for
    extracted_date = Column(DateTime, default=datetime.utcnow)  # When we extracted them
    
    # Revenue Metrics (stored as strings to preserve formatting like "$1.2M", "~$8.000M")
    mrr = Column(String)  # Monthly Recurring Revenue
    arr = Column(String)  # Annual Recurring Revenue  
    qrr = Column(String)  # Quarterly Recurring Revenue
    total_revenue = Column(String)  # Total revenue for period
    gross_revenue = Column(String)  # Gross revenue
    net_revenue = Column(String)  # Net revenue
    
    # Revenue Growth Metrics
    mrr_growth = Column(String)  # MRR growth rate
    arr_growth = Column(String)  # ARR growth rate
    revenue_growth_yoy = Column(String)  # Year over year growth
    revenue_growth_mom = Column(String)  # Month over month growth
    
    # Financial Health Metrics
    cash_balance = Column(String)  # Current cash balance
    net_burn = Column(String)  # Monthly net burn rate
    gross_burn = Column(String)  # Monthly gross burn rate
    runway_months = Column(String)  # Cash runway in months
    
    # Profitability Metrics
    gross_margin = Column(String)  # Gross margin percentage
    ebitda = Column(String)  # EBITDA
    ebitda_margin = Column(String)  # EBITDA margin
    net_income = Column(String)  # Net income/loss
    
    # Customer Metrics
    customer_count = Column(String)  # Total customers
    new_customers = Column(String)  # New customers in period
    churn_rate = Column(String)  # Customer churn rate
    ltv = Column(String)  # Lifetime value
    cac = Column(String)  # Customer acquisition cost
    
    # Operational Metrics
    team_size = Column(String)  # Number of employees
    bookings = Column(String)  # New bookings/contracts
    pipeline = Column(String)  # Sales pipeline value
    
    # Additional Context
    key_highlights = Column(Text)  # Key achievements/highlights
    key_challenges = Column(Text)  # Challenges mentioned
    funding_status = Column(String)  # Current funding status/notes
    
    # Data Source Information
    source_type = Column(String)  # 'email', 'attachment', 'manual'
    source_file = Column(String)  # Filename if from attachment
    extraction_confidence = Column(String)  # 'high', 'medium', 'low'
    extraction_notes = Column(Text)  # Notes about extraction process
    
    # Relationships
    company = relationship("Company")
    email_update = relationship("EmailUpdate")

class MetricExtraction(Base):
    __tablename__ = "metric_extractions"
    
    id = Column(Integer, primary_key=True)
    email_update_id = Column(Integer, ForeignKey("email_updates.id"))
    attachment_id = Column(Integer, ForeignKey("attachments.id"), nullable=True)
    
    # Extraction metadata
    extracted_at = Column(DateTime, default=datetime.utcnow)
    extraction_method = Column(String)  # 'claude_ai', 'regex', 'manual'
    extraction_status = Column(String)  # 'success', 'partial', 'failed'
    raw_extraction = Column(Text)  # Raw extracted text/data
    processed_metrics_id = Column(Integer, ForeignKey("financial_metrics.id"), nullable=True)
    
    # Error handling
    error_message = Column(Text)  # If extraction failed
    retry_count = Column(Integer, default=0)
    
    # Relationships
    email_update = relationship("EmailUpdate")
    attachment = relationship("Attachment")
    financial_metrics = relationship("FinancialMetrics") 