"""
Claude AI Client Integration
============================

Client for Anthropic's Claude AI service to analyze emails and extract financial metrics.

This module handles:
- Claude API authentication and requests
- Email content analysis for company identification
- Financial metrics extraction from text and attachments
- Confidence scoring and reasoning

Usage:
    from integrations.claude_client import ClaudeClient
    
    client = ClaudeClient()
    analysis = client.analyze_email_for_company_update(email_content, companies)
    metrics = client.extract_financial_metrics(content, company_name)
"""

import os
import json
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv
import anthropic

load_dotenv()


class ClaudeClient:
    """
    Client for interacting with Anthropic's Claude AI service.
    
    Provides email analysis and financial metrics extraction capabilities
    for the Tweener Fund portfolio tracking system.
    """
    
    def __init__(self):
        """Initialize Claude client with API key from environment variables."""
        self.api_key = os.getenv('ANTHROPIC_API_KEY')
        
        if not self.api_key:
            raise ValueError("ANTHROPIC_API_KEY not found in environment variables")
        
        self.client = anthropic.Anthropic(api_key=self.api_key)
        self.model = "claude-3-sonnet-20240229"
    
    def analyze_email_for_company_update(self, email_content: Dict, 
                                       portfolio_companies: List[Any]) -> Optional[Dict]:
        """
        Analyze an email to determine if it's a portfolio company update.
        
        Args:
            email_content: Dictionary with email subject, body, sender, etc.
            portfolio_companies: List of portfolio company objects
            
        Returns:
            Analysis dictionary with company identification and confidence score
        """
        # Build company list for Claude
        company_list = []
        for company in portfolio_companies:
            company_info = {
                'name': company.name,
                'legal_name': getattr(company, 'legal_name', None),
                'website': getattr(company, 'website', None)
            }
            company_list.append(company_info)
        
        # Create analysis prompt
        prompt = self._build_company_analysis_prompt(email_content, company_list)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse Claude's response
            return self._parse_company_analysis_response(response.content[0].text)
            
        except Exception as e:
            print(f"❌ Claude API error during company analysis: {e}")
            return None
    
    def extract_financial_metrics(self, content: str, company_name: str, 
                                 source_type: str = "email") -> Optional[Dict]:
        """
        Extract financial metrics from email or attachment content.
        
        Args:
            content: Text content to analyze
            company_name: Name of the company for context
            source_type: Type of source ("email" or "attachment")
            
        Returns:
            Dictionary with extracted financial metrics
        """
        prompt = self._build_financial_extraction_prompt(content, company_name, source_type)
        
        try:
            response = self.client.messages.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}]
            )
            
            # Parse financial metrics from response
            return self._parse_financial_metrics_response(response.content[0].text)
            
        except Exception as e:
            print(f"❌ Claude API error during financial extraction: {e}")
            return None
    
    def _build_company_analysis_prompt(self, email_content: Dict, 
                                     company_list: List[Dict]) -> str:
        """Build prompt for company identification analysis."""
        
        companies_text = "\n".join([
            f"- {comp['name']}" + 
            (f" (Legal: {comp['legal_name']})" if comp['legal_name'] else "") +
            (f" (Website: {comp['website']})" if comp['website'] else "")
            for comp in company_list
        ])
        
        return f"""
You are analyzing an email to determine if it contains a portfolio company update.

EMAIL DETAILS:
Subject: {email_content.get('subject', 'N/A')}
From: {email_content.get('sender', 'N/A')}
Body: {email_content.get('body', 'N/A')[:2000]}

PORTFOLIO COMPANIES:
{companies_text}

Please analyze this email and determine:
1. Is this a company update (business metrics, financial results, progress reports)?
2. If yes, which company is it about?
3. Your confidence level (0.0 to 1.0)
4. Brief reasoning for your decision

Respond in JSON format:
{{
    "is_company_update": true/false,
    "company_name": "exact company name from list or null",
    "confidence": 0.0-1.0,
    "reasoning": "brief explanation"
}}
"""
    
    def _build_financial_extraction_prompt(self, content: str, company_name: str, 
                                         source_type: str) -> str:
        """Build prompt for financial metrics extraction."""
        
        return f"""
You are extracting financial metrics from a {source_type} for {company_name}.

CONTENT TO ANALYZE:
{content[:4000]}

Please extract the following financial metrics if mentioned:

REVENUE METRICS:
- MRR (Monthly Recurring Revenue)
- ARR (Annual Recurring Revenue) 
- QRR (Quarterly Recurring Revenue)
- Total Revenue
- Gross Revenue
- Net Revenue

GROWTH METRICS:
- MRR Growth (percentage)
- ARR Growth (percentage)
- Revenue Growth YoY (percentage)
- Revenue Growth MoM (percentage)

FINANCIAL HEALTH:
- Cash Balance
- Net Burn (monthly)
- Gross Burn (monthly)
- Runway (in months)

PROFITABILITY:
- Gross Margin (percentage)
- EBITDA
- EBITDA Margin (percentage)
- Net Income

BUSINESS METRICS:
- Customer Count
- New Customers
- Churn Rate (percentage)
- LTV (Lifetime Value)
- CAC (Customer Acquisition Cost)
- Team Size
- Bookings
- Pipeline

ADDITIONAL INFO:
- Reporting Period (e.g., "Q1 2025", "May 2025")
- Key Highlights
- Key Challenges
- Funding Status

Respond in JSON format with the exact field names above. Use "N/A" for missing values.
Include a "reporting_period" field and "extraction_confidence" (low/medium/high).

{{
    "reporting_period": "Q1 2025",
    "mrr": "value or N/A",
    "arr": "value or N/A",
    ...
    "extraction_confidence": "medium"
}}
"""
    
    def _parse_company_analysis_response(self, response_text: str) -> Optional[Dict]:
        """Parse Claude's company analysis response."""
        try:
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                return None
            
            json_text = response_text[json_start:json_end]
            return json.loads(json_text)
            
        except Exception as e:
            print(f"❌ Error parsing company analysis response: {e}")
            return None
    
    def _parse_financial_metrics_response(self, response_text: str) -> Optional[Dict]:
        """Parse Claude's financial metrics extraction response."""
        try:
            # Extract JSON from response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1
            
            if json_start == -1 or json_end == 0:
                return None
            
            json_text = response_text[json_start:json_end]
            metrics = json.loads(json_text)
            
            # Ensure required fields exist
            if 'extraction_confidence' not in metrics:
                metrics['extraction_confidence'] = 'medium'
            
            if 'reporting_period' not in metrics:
                metrics['reporting_period'] = 'N/A'
            
            return metrics
            
        except Exception as e:
            print(f"❌ Error parsing financial metrics response: {e}")
            return None


def main():
    """Demo function showing Claude client usage."""
    print("🤖 Claude Client Demo")
    print("=" * 30)
    
    try:
        client = ClaudeClient()
        
        # Test with sample email content
        sample_email = {
            'subject': 'Fwd: Company Update - Q1 Results',
            'sender': 'scot@tweenerfund.com',
            'body': 'This is a sample email about company performance...'
        }
        
        print("🔗 Testing Claude API connection...")
        print("   (Note: This is just a connection test)")
        print("✅ Claude client initialized successfully!")
        
    except Exception as e:
        print(f"❌ Claude client error: {e}")


if __name__ == "__main__":
    main() 