#!/usr/bin/env python3
"""
Financial Metrics Dashboard

A simple web dashboard for viewing portfolio company financial metrics.
Built with Flask and displays data from the SQLite database.

Usage:
    python dashboard/app.py
    
Then open: http://localhost:5000
"""

import os
import sys
from datetime import datetime, timedelta
from flask import Flask, render_template, jsonify, request
import json

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import Company, EmailUpdate
from database.financial_models import FinancialMetrics
from database.connection import SessionLocal

app = Flask(__name__)

def get_dashboard_data():
    """Get all data needed for the dashboard"""
    session = SessionLocal()
    
    try:
        # Basic statistics
        total_metrics = session.query(FinancialMetrics).count()
        companies_with_metrics = session.query(FinancialMetrics.company_id).distinct().count()
        total_companies = session.query(Company).filter(Company.is_tweener_portfolio == True).count()
        
        # Recent metrics (last 30 days)
        recent_cutoff = datetime.now() - timedelta(days=30)
        recent_metrics = session.query(FinancialMetrics).filter(
            FinancialMetrics.extracted_date >= recent_cutoff
        ).count()
        
        # Get all metrics with company info
        metrics_query = session.query(FinancialMetrics).join(Company).order_by(
            FinancialMetrics.extracted_date.desc()
        ).all()
        
        # Format metrics for display
        metrics_data = []
        for metric in metrics_query:
            metrics_data.append({
                'id': metric.id,
                'company_name': metric.company.name,
                'reporting_period': metric.reporting_period or 'N/A',
                'reporting_date': metric.reporting_date.strftime('%Y-%m-%d') if metric.reporting_date else 'N/A',
                'extracted_date': metric.extracted_date.strftime('%Y-%m-%d'),
                'mrr': metric.mrr or 'N/A',
                'arr': metric.arr or 'N/A',
                'cash_balance': metric.cash_balance or 'N/A',
                'runway_months': metric.runway_months or 'N/A',
                'customer_count': metric.customer_count or 'N/A',
                'team_size': metric.team_size or 'N/A',
                'arr_growth': metric.arr_growth or 'N/A',
                'mrr_growth': metric.mrr_growth or 'N/A',
                'gross_margin': metric.gross_margin or 'N/A',
                'key_highlights': metric.key_highlights or 'N/A',
                'key_challenges': metric.key_challenges or 'N/A',
                'source_type': metric.source_type or 'N/A',
                'source_file': metric.source_file or 'N/A',
                'extraction_confidence': metric.extraction_confidence or 'N/A'
            })
        
        # Company summary stats
        from sqlalchemy import func
        company_stats = session.query(
            Company.name,
            func.count(FinancialMetrics.id).label('metric_count'),
            func.max(FinancialMetrics.extracted_date).label('last_update')
        ).join(FinancialMetrics).group_by(Company.id, Company.name).order_by(
            func.count(FinancialMetrics.id).desc()
        ).all()
        
        company_summary = []
        for company_name, count, last_update in company_stats:
            company_summary.append({
                'name': company_name,
                'metric_count': count,
                'last_update': last_update.strftime('%Y-%m-%d') if last_update else 'N/A'
            })
        
        return {
            'stats': {
                'total_metrics': total_metrics,
                'companies_with_metrics': companies_with_metrics,
                'total_companies': total_companies,
                'recent_metrics': recent_metrics,
                'coverage_percent': round((companies_with_metrics/total_companies)*100, 1) if total_companies > 0 else 0
            },
            'metrics': metrics_data,
            'companies': company_summary
        }
        
    except Exception as e:
        print(f"Error getting dashboard data: {e}")
        return {
            'stats': {'total_metrics': 0, 'companies_with_metrics': 0, 'total_companies': 0, 'recent_metrics': 0, 'coverage_percent': 0},
            'metrics': [],
            'companies': []
        }
    finally:
        session.close()

@app.route('/')
def dashboard():
    """Main dashboard page"""
    data = get_dashboard_data()
    return render_template('dashboard.html', **data)

@app.route('/api/metrics')
def api_metrics():
    """API endpoint for metrics data"""
    data = get_dashboard_data()
    return jsonify(data)

@app.route('/api/company/<company_name>')
def api_company_metrics(company_name):
    """API endpoint for specific company metrics"""
    session = SessionLocal()
    
    try:
        # Get company
        company = session.query(Company).filter(
            Company.name.ilike(f"%{company_name}%")
        ).first()
        
        if not company:
            return jsonify({'error': 'Company not found'}), 404
        
        # Get metrics for this company
        metrics = session.query(FinancialMetrics).filter(
            FinancialMetrics.company_id == company.id
        ).order_by(FinancialMetrics.extracted_date.desc()).all()
        
        metrics_data = []
        for metric in metrics:
            metrics_data.append({
                'id': metric.id,
                'reporting_period': metric.reporting_period or 'N/A',
                'reporting_date': metric.reporting_date.strftime('%Y-%m-%d') if metric.reporting_date else 'N/A',
                'extracted_date': metric.extracted_date.strftime('%Y-%m-%d'),
                'mrr': metric.mrr or 'N/A',
                'arr': metric.arr or 'N/A',
                'cash_balance': metric.cash_balance or 'N/A',
                'runway_months': metric.runway_months or 'N/A',
                'customer_count': metric.customer_count or 'N/A',
                'team_size': metric.team_size or 'N/A',
                'source_type': metric.source_type or 'N/A',
                'extraction_confidence': metric.extraction_confidence or 'N/A'
            })
        
        return jsonify({
            'company': company.name,
            'metrics': metrics_data
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

if __name__ == '__main__':
    print("🚀 Starting Financial Metrics Dashboard")
    print("📊 Dashboard will be available at: http://localhost:8888")
    print("🔄 Press Ctrl+C to stop")
    
    app.run(debug=True, host='0.0.0.0', port=8888) 