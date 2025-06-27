# financial_metrics_formatter.py
import re
from decimal import Decimal, InvalidOperation

class FinancialMetricsFormatter:
    def __init__(self):
        self.currency_patterns = [
            (r'\$(\d+(?:\.\d+)?)\s*[Mm](?:illion)?', lambda x: float(x) * 1000000),
            (r'\$(\d+(?:\.\d+)?)\s*[Kk](?:thousand)?', lambda x: float(x) * 1000),
            (r'\$(\d+(?:,\d{3})*(?:\.\d+)?)', lambda x: float(x.replace(',', ''))),
            (r'(\d+(?:\.\d+)?)\s*[Mm](?:illion)?', lambda x: float(x) * 1000000),
            (r'(\d+(?:\.\d+)?)\s*[Kk](?:thousand)?', lambda x: float(x) * 1000),
            (r'(\d+(?:,\d{3})*(?:\.\d+)?)', lambda x: float(x.replace(',', ''))),
        ]
        
        self.percentage_patterns = [
            (r'([+-]?\d+(?:\.\d+)?)\s*%', lambda x: float(x)),
            (r'([+-]?\d+(?:\.\d+)?)\s*percent', lambda x: float(x)),
        ]
        
        self.runway_patterns = [
            (r'(\d+(?:\.\d+)?)\+?\s*months?', lambda x: float(x)),
            (r'(\d+(?:\.\d+)?)\+?\s*years?', lambda x: float(x) * 12),
        ]

    def parse_currency(self, value_str):
        """Parse currency string to standardized float value"""
        if not value_str or value_str == 'N/A':
            return None
            
        value_str = str(value_str).strip()
        
        # Handle special cases
        if 'increased' in value_str.lower() or 'improved' in value_str.lower():
            return None
            
        # Remove common prefixes/suffixes
        value_str = re.sub(r'^~|approximately|about|around', '', value_str, flags=re.IGNORECASE).strip()
        
        for pattern, converter in self.currency_patterns:
            match = re.search(pattern, value_str, re.IGNORECASE)
            if match:
                try:
                    return converter(match.group(1))
                except (ValueError, InvalidOperation):
                    continue
        
        return None

    def parse_percentage(self, value_str):
        """Parse percentage string to standardized float value"""
        if not value_str or value_str == 'N/A':
            return None
            
        value_str = str(value_str).strip()
        
        for pattern, converter in self.percentage_patterns:
            match = re.search(pattern, value_str, re.IGNORECASE)
            if match:
                try:
                    return converter(match.group(1))
                except (ValueError, InvalidOperation):
                    continue
        
        return None

    def parse_runway(self, value_str):
        """Parse runway string to standardized months"""
        if not value_str or value_str == 'N/A':
            return None
            
        value_str = str(value_str).strip()
        
        for pattern, converter in self.runway_patterns:
            match = re.search(pattern, value_str, re.IGNORECASE)
            if match:
                try:
                    return converter(match.group(1))
                except (ValueError, InvalidOperation):
                    continue
        
        return None

    def format_currency(self, value):
        """Format currency value to standardized string"""
        if value is None:
            return None
            
        if value >= 1000000:
            return f"${value/1000000:.1f}M"
        elif value >= 1000:
            return f"${value/1000:.0f}K"
        else:
            return f"${value:,.0f}"

    def format_percentage(self, value):
        """Format percentage to standardized string"""
        if value is None:
            return None
        return f"{value:+.1f}%"

    def format_runway(self, value):
        """Format runway to standardized string"""
        if value is None:
            return None
        if value >= 12:
            years = value / 12
            return f"{years:.1f} years"
        else:
            return f"{value:.0f} months"

    def standardize_metric_values(self, metric_record):
        """Standardize and format values from a financial metrics record"""
        standardized = {}
        
        # Revenue metrics
        for field in ['mrr', 'arr', 'qrr', 'total_revenue', 'gross_revenue', 'net_revenue']:
            raw_value = getattr(metric_record, field)
            parsed_value = self.parse_currency(raw_value)
            standardized[f'{field}_raw'] = raw_value
            standardized[f'{field}_value'] = parsed_value
            standardized[f'{field}_formatted'] = self.format_currency(parsed_value)
        
        # Growth metrics
        for field in ['mrr_growth', 'arr_growth', 'revenue_growth_yoy', 'revenue_growth_mom']:
            raw_value = getattr(metric_record, field)
            parsed_value = self.parse_percentage(raw_value)
            standardized[f'{field}_raw'] = raw_value
            standardized[f'{field}_value'] = parsed_value
            standardized[f'{field}_formatted'] = self.format_percentage(parsed_value)
        
        # Financial health metrics
        for field in ['cash_balance', 'net_burn', 'gross_burn']:
            raw_value = getattr(metric_record, field)
            parsed_value = self.parse_currency(raw_value)
            standardized[f'{field}_raw'] = raw_value
            standardized[f'{field}_value'] = parsed_value
            standardized[f'{field}_formatted'] = self.format_currency(parsed_value)
        
        # Runway
        runway_raw = getattr(metric_record, 'runway_months')
        runway_parsed = self.parse_runway(runway_raw)
        standardized['runway_months_raw'] = runway_raw
        standardized['runway_months_value'] = runway_parsed
        standardized['runway_months_formatted'] = self.format_runway(runway_parsed)
        
        # Profitability metrics
        for field in ['gross_margin', 'ebitda_margin']:
            raw_value = getattr(metric_record, field)
            parsed_value = self.parse_percentage(raw_value)
            standardized[f'{field}_raw'] = raw_value
            standardized[f'{field}_value'] = parsed_value
            standardized[f'{field}_formatted'] = self.format_percentage(parsed_value)
        
        # EBITDA and net income (currency)
        for field in ['ebitda', 'net_income']:
            raw_value = getattr(metric_record, field)
            parsed_value = self.parse_currency(raw_value)
            standardized[f'{field}_raw'] = raw_value
            standardized[f'{field}_value'] = parsed_value
            standardized[f'{field}_formatted'] = self.format_currency(parsed_value)
        
        return standardized


def main():
    """Demo function showing formatter usage"""
    formatter = FinancialMetricsFormatter()
    
    # Example usage
    test_values = {
        'currency': ['$2.5M', '$150K', '$1,250,000', '2.5 million'],
        'percentage': ['15%', '-5.2%', '25 percent'],
        'runway': ['18 months', '2.5 years', '6 months']
    }
    
    print("🔧 FINANCIAL METRICS FORMATTER DEMO")
    print("=" * 50)
    
    print("\n💰 Currency Parsing:")
    for value in test_values['currency']:
        parsed = formatter.parse_currency(value)
        formatted = formatter.format_currency(parsed)
        print(f"   {value:<15} → {parsed:<10} → {formatted}")
    
    print("\n📈 Percentage Parsing:")
    for value in test_values['percentage']:
        parsed = formatter.parse_percentage(value)
        formatted = formatter.format_percentage(parsed)
        print(f"   {value:<15} → {parsed:<10} → {formatted}")
    
    print("\n🛣️  Runway Parsing:")
    for value in test_values['runway']:
        parsed = formatter.parse_runway(value)
        formatted = formatter.format_runway(parsed)
        print(f"   {value:<15} → {parsed:<10} → {formatted}")


if __name__ == "__main__":
    main() 