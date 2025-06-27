# financial_metrics_formatter.py
import re
import pandas as pd
from decimal import Decimal, InvalidOperation
from datetime import datetime
from financial_metrics_models import FinancialMetrics
from db import SessionLocal

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

    def standardize_metric_record(self, metric_record):
        """Standardize a single financial metrics record"""
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
        
        # Add metadata
        standardized['company_name'] = metric_record.company.name
        standardized['reporting_period'] = metric_record.reporting_period
        standardized['reporting_date'] = metric_record.reporting_date
        standardized['extraction_confidence'] = metric_record.extraction_confidence
        standardized['source_type'] = metric_record.source_type
        
        return standardized

    def create_unified_dataset(self):
        """Create a unified, standardized dataset of all financial metrics"""
        session = SessionLocal()
        
        try:
            # Get all financial metrics with company info
            metrics = session.query(FinancialMetrics).join(FinancialMetrics.company).all()
            
            print(f"💰 Standardizing {len(metrics)} financial metric records...")
            
            standardized_data = []
            
            for metric in metrics:
                standardized = self.standardize_metric_record(metric)
                standardized_data.append(standardized)
            
            # Convert to DataFrame for easy analysis
            df = pd.DataFrame(standardized_data)
            
            return df
            
        finally:
            session.close()

    def generate_unified_report(self):
        """Generate a comprehensive unified financial metrics report"""
        df = self.create_unified_dataset()
        
        print("📊 UNIFIED FINANCIAL METRICS REPORT")
        print("=" * 70)
        
        # Summary statistics
        print(f"📈 Total Records: {len(df)}")
        print(f"🏢 Companies: {df['company_name'].nunique()}")
        print(f"📅 Reporting Periods: {df['reporting_period'].nunique()}")
        print()
        
        # ARR Analysis
        arr_data = df[df['arr_value'].notna()].copy()
        if not arr_data.empty:
            print("💰 ANNUAL RECURRING REVENUE (ARR)")
            print("-" * 40)
            arr_summary = arr_data.groupby('company_name').agg({
                'arr_value': 'max',
                'arr_formatted': 'first',
                'reporting_period': 'first'
            }).sort_values('arr_value', ascending=False)
            
            for company, row in arr_summary.iterrows():
                print(f"   {company:<20} {row['arr_formatted']:<10} ({row['reporting_period']})")
            print()
        
        # Cash Balance Analysis
        cash_data = df[df['cash_balance_value'].notna()].copy()
        if not cash_data.empty:
            print("💵 CASH BALANCE")
            print("-" * 40)
            cash_summary = cash_data.groupby('company_name').agg({
                'cash_balance_value': 'max',
                'cash_balance_formatted': 'first',
                'reporting_period': 'first'
            }).sort_values('cash_balance_value', ascending=False)
            
            for company, row in cash_summary.iterrows():
                print(f"   {company:<20} {row['cash_balance_formatted']:<10} ({row['reporting_period']})")
            print()
        
        # Runway Analysis
        runway_data = df[df['runway_months_value'].notna()].copy()
        if not runway_data.empty:
            print("🛣️  CASH RUNWAY")
            print("-" * 40)
            runway_summary = runway_data.groupby('company_name').agg({
                'runway_months_value': 'max',
                'runway_months_formatted': 'first',
                'reporting_period': 'first'
            }).sort_values('runway_months_value', ascending=False)
            
            for company, row in runway_summary.iterrows():
                print(f"   {company:<20} {row['runway_months_formatted']:<12} ({row['reporting_period']})")
            print()
        
        # Growth Analysis
        growth_data = df[df['arr_growth_value'].notna()].copy()
        if not growth_data.empty:
            print("📈 ARR GROWTH RATES")
            print("-" * 40)
            growth_summary = growth_data.groupby('company_name').agg({
                'arr_growth_value': 'first',
                'arr_growth_formatted': 'first',
                'reporting_period': 'first'
            }).sort_values('arr_growth_value', ascending=False)
            
            for company, row in growth_summary.iterrows():
                print(f"   {company:<20} {row['arr_growth_formatted']:<10} ({row['reporting_period']})")
            print()
        
        # Data Quality Summary
        print("🎯 DATA QUALITY SUMMARY")
        print("-" * 40)
        confidence_counts = df['extraction_confidence'].value_counts()
        for confidence, count in confidence_counts.items():
            print(f"   {confidence.title():<15} {count:>3} records")
        
        print()
        source_counts = df['source_type'].value_counts()
        for source, count in source_counts.items():
            print(f"   {source.title():<15} {count:>3} records")
        
        return df

    def export_to_excel(self, filename="unified_financial_metrics.xlsx"):
        """Export unified metrics to Excel for further analysis"""
        df = self.create_unified_dataset()
        
        # Create multiple sheets
        with pd.ExcelWriter(filename, engine='openpyxl') as writer:
            # Full dataset
            df.to_excel(writer, sheet_name='All_Metrics', index=False)
            
            # Summary by company
            summary_data = []
            for company in df['company_name'].unique():
                company_data = df[df['company_name'] == company]
                latest_record = company_data.iloc[-1]  # Most recent
                
                summary_data.append({
                    'Company': company,
                    'Latest_Period': latest_record['reporting_period'],
                    'ARR': latest_record['arr_formatted'],
                    'MRR': latest_record['mrr_formatted'],
                    'Cash_Balance': latest_record['cash_balance_formatted'],
                    'Runway': latest_record['runway_months_formatted'],
                    'ARR_Growth': latest_record['arr_growth_formatted'],
                    'Confidence': latest_record['extraction_confidence'],
                    'Source': latest_record['source_type']
                })
            
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_excel(writer, sheet_name='Company_Summary', index=False)
        
        print(f"📊 Unified metrics exported to: {filename}")
        return filename


def main():
    """Main function to demonstrate unified formatting"""
    formatter = FinancialMetricsFormatter()
    
    # Generate unified report
    df = formatter.generate_unified_report()
    
    # Export to Excel
    filename = formatter.export_to_excel()
    
    print(f"\n✅ Unified formatting complete!")
    print(f"📁 Excel export: {filename}")
    print(f"📊 Processed {len(df)} records from {df['company_name'].nunique()} companies")


if __name__ == "__main__":
    main() 