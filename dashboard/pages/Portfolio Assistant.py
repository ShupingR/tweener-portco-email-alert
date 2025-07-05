#!/usr/bin/env python3
"""
Portfolio Assistant - AI Chatbot for Tweener Fund Portfolio Analysis

Interactive chatbot that can answer questions about portfolio companies,
financial metrics, growth rates, and operational data.
"""

import os
import sys
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import re
from sqlalchemy import func, text

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from database.models import Company, EmailUpdate
from database.financial_models import FinancialMetrics
from database.connection import SessionLocal

# Page configuration
st.set_page_config(
    page_title="Portfolio Assistant - Tweener Insights",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply theme-responsive styling
st.markdown("""
<style>
    /* Tweener Fund Brand Theme - Theme Responsive */
    :root {
        --tweener-primary: #4fd1c7;
        --tweener-secondary: #38b2ac;
        --tweener-accent: #81e6d9;
        --tweener-dark-green: #2d5016;
        --tweener-orange: #ed8936;
        --tweener-success: #48bb78;
        --tweener-warning: #ed8936;
        --tweener-danger: #f56565;
    }
    
    /* Theme-responsive styling that works with Streamlit's dark/light mode */
    .stApp {
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    }
    
    /* Header styling - theme responsive */
    h1 {
        color: var(--tweener-primary);
        font-weight: 700;
        border-bottom: 3px solid var(--tweener-primary);
        padding-bottom: 0.5rem;
        margin-bottom: 0.5rem;
    }
    
    /* Button styling - theme responsive */
    .stButton > button {
        background-color: var(--tweener-orange);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.5rem 1.5rem;
        transition: all 0.2s ease;
    }
    
    .stButton > button:hover {
        background-color: #dd7324;
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(237, 137, 54, 0.3);
    }
    
    /* Text input styling - theme responsive */
    .stTextInput > div > div {
        border-radius: 8px;
        border: 2px solid;
        border-color: rgba(49, 51, 63, 0.2);
    }
    
    .stTextInput > div > div:focus {
        border-color: var(--tweener-primary);
        box-shadow: 0 0 0 2px rgba(79, 209, 199, 0.2);
    }
    
    /* Chat message styling - theme responsive */
    .chat-message {
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0 0.5rem 2rem;
        border-left: 4px solid var(--tweener-secondary);
    }
    
    .chat-message.user {
        background: var(--tweener-primary);
        color: white;
    }
    
    .chat-message.assistant {
        background: rgba(49, 51, 63, 0.05);
        color: inherit;
    }
    
    /* Welcome message styling - theme responsive */
    .welcome-message {
        background: linear-gradient(135deg, var(--tweener-primary), var(--tweener-secondary));
        color: white;
        padding: 2rem;
        border-radius: 12px;
        text-align: center;
        margin-bottom: 2rem;
    }
</style>
""", unsafe_allow_html=True)

# Chatbot Functionality
class DatabaseChatbot:
    def __init__(self):
        self.session = SessionLocal()
        self.conversation_history = []
    
    def close_session(self):
        """Close database session"""
        if self.session:
            self.session.close()
    
    def query_database(self, question):
        """Process natural language questions about the portfolio data"""
        question_lower = question.lower()
        
        try:
            # Performance queries (check FIRST to avoid conflicts with "companies")
            if any(term in question_lower for term in ["performance", "best", "worst", "top", "bottom"]):
                return self._handle_performance_queries(question_lower)
            
            # Company-specific queries
            elif "company" in question_lower or "companies" in question_lower:
                return self._handle_company_queries(question_lower)
            
            # Financial metrics queries
            elif any(term in question_lower for term in ["arr", "revenue", "mrr", "financial"]):
                return self._handle_financial_queries(question_lower)
            
            # Growth queries
            elif "growth" in question_lower:
                return self._handle_growth_queries(question_lower)
            
            # Cash and runway queries
            elif any(term in question_lower for term in ["cash", "runway", "burn"]):
                return self._handle_cash_queries(question_lower)
            
            # Team and customer queries
            elif any(term in question_lower for term in ["team", "employees", "customers", "hiring"]):
                return self._handle_operational_queries(question_lower)
            
            # General portfolio overview
            elif any(term in question_lower for term in ["overview", "summary", "portfolio", "total"]):
                return self._handle_portfolio_overview()
            
            # Recent updates
            elif any(term in question_lower for term in ["recent", "latest", "new", "updates"]):
                return self._handle_recent_updates()
            
            else:
                return self._provide_help()
                
        except Exception as e:
            return f"I encountered an error while processing your question: {str(e)}. Please try rephrasing your question."
    
    def _handle_company_queries(self, question):
        """Handle company-related queries"""
        try:
            companies = self.session.query(Company).filter(Company.is_tweener_portfolio == True).all()
            
            if "how many" in question or "count" in question:
                total_companies = len(companies)
                companies_with_metrics = self.session.query(FinancialMetrics.company_id).distinct().count()
                return f"We track {total_companies} portfolio companies in total, with {companies_with_metrics} companies having financial metrics data."
            
            elif "list" in question or "all companies" in question:
                company_names = [c.name for c in companies]
                if len(company_names) > 10:
                    return f"Here are our portfolio companies: {', '.join(company_names[:10])}... and {len(company_names)-10} more. Total: {len(company_names)} companies."
                else:
                    return f"Our portfolio companies: {', '.join(company_names)}"
            
            else:
                # Check if asking about a specific company
                for company in companies:
                    if company.name.lower() in question:
                        return self._get_company_details(company.name)
                
                return "I can help you with company information. Try asking 'How many companies?' or 'List all companies' or ask about a specific company by name."
        
        except Exception as e:
            return f"Error retrieving company data: {str(e)}"
    
    def _handle_financial_queries(self, question):
        """Handle financial metrics queries"""
        try:
            # Get latest financial metrics (only portfolio companies)
            latest_metrics = self.session.query(FinancialMetrics).join(Company).filter(
                Company.is_tweener_portfolio == True
            ).order_by(FinancialMetrics.extracted_date.desc()).limit(10).all()
            
            if not latest_metrics:
                return "No financial metrics data available yet."
            
            if "arr" in question:
                arr_data = [m for m in latest_metrics if m.arr and m.arr != 'N/A' and m.arr != '-']
                if arr_data:
                    total_arr = sum(self._parse_financial_value(m.arr) for m in arr_data if self._parse_financial_value(m.arr) > 0)
                    return f"Based on latest data, our portfolio companies have a combined ARR of approximately ${total_arr:,.0f}. Data from {len(arr_data)} companies."
                else:
                    return "No ARR data available in recent metrics."
            
            elif "mrr" in question:
                mrr_data = [m for m in latest_metrics if m.mrr and m.mrr != 'N/A' and m.mrr != '-']
                if mrr_data:
                    total_mrr = sum(self._parse_financial_value(m.mrr) for m in mrr_data if self._parse_financial_value(m.mrr) > 0)
                    return f"Based on latest data, our portfolio companies have a combined MRR of approximately ${total_mrr:,.0f}. Data from {len(mrr_data)} companies."
                else:
                    return "No MRR data available in recent metrics."
            
            else:
                return "I can help with ARR, MRR, and other financial metrics. Try asking 'What's our total ARR?' or 'Show me MRR data'."
        
        except Exception as e:
            return f"Error retrieving financial data: {str(e)}"
    
    def _handle_growth_queries(self, question):
        """Handle growth-related queries"""
        try:
            growth_data = self.session.query(FinancialMetrics).join(Company).filter(
                Company.is_tweener_portfolio == True,
                FinancialMetrics.arr_growth.isnot(None),
                FinancialMetrics.arr_growth != 'N/A',
                FinancialMetrics.arr_growth != '-'
            ).order_by(FinancialMetrics.extracted_date.desc()).limit(20).all()
            
            if not growth_data:
                return "No growth data available in recent metrics."
            
            # Parse growth rates
            growth_rates = []
            for metric in growth_data:
                try:
                    # Extract percentage from strings like "+25%" or "148.509%"
                    growth_str = str(metric.arr_growth).replace('+', '').replace('%', '')
                    growth_rate = float(growth_str)
                    growth_rates.append((metric.company.name, growth_rate))
                except:
                    continue
            
            if growth_rates:
                avg_growth = sum(rate for _, rate in growth_rates) / len(growth_rates)
                best_growth = max(growth_rates, key=lambda x: x[1])
                
                return f"Portfolio growth insights:\n• Average growth rate: {avg_growth:.1f}%\n• Best performing: {best_growth[0]} at {best_growth[1]:.1f}%\n• Data from {len(growth_rates)} companies"
            else:
                return "Unable to parse growth data from recent metrics."
        
        except Exception as e:
            return f"Error retrieving growth data: {str(e)}"
    
    def _handle_cash_queries(self, question):
        """Handle cash and runway queries"""
        try:
            cash_data = self.session.query(FinancialMetrics).join(Company).filter(
                Company.is_tweener_portfolio == True,
                FinancialMetrics.cash_balance.isnot(None),
                FinancialMetrics.cash_balance != 'N/A',
                FinancialMetrics.cash_balance != '-'
            ).order_by(FinancialMetrics.extracted_date.desc()).limit(20).all()
            
            if "runway" in question:
                runway_data = [m for m in cash_data if m.runway_months and m.runway_months not in ['N/A', '-']]
                if runway_data:
                    avg_runway = sum(self._parse_runway_months(m.runway_months) for m in runway_data) / len(runway_data)
                    return f"Portfolio runway insights:\n• Average runway: {avg_runway:.1f} months\n• Data from {len(runway_data)} companies\n• Companies should maintain 12+ months runway"
                else:
                    return "No runway data available in recent metrics."
            
            elif "cash" in question:
                if cash_data:
                    total_cash = sum(self._parse_financial_value(m.cash_balance) for m in cash_data if self._parse_financial_value(m.cash_balance) > 0)
                    return f"Portfolio cash insights:\n• Combined cash balance: ${total_cash:,.0f}\n• Data from {len(cash_data)} companies"
                else:
                    return "No cash balance data available in recent metrics."
        
        except Exception as e:
            return f"Error retrieving cash/runway data: {str(e)}"
    
    def _handle_operational_queries(self, question):
        """Handle team size and customer queries"""
        try:
            if "team" in question or "employees" in question:
                team_data = self.session.query(FinancialMetrics).join(Company).filter(
                    Company.is_tweener_portfolio == True,
                    FinancialMetrics.team_size.isnot(None),
                    FinancialMetrics.team_size != 'N/A',
                    FinancialMetrics.team_size != '-'
                ).order_by(FinancialMetrics.extracted_date.desc()).limit(20).all()
                
                if team_data:
                    total_employees = sum(int(float(str(m.team_size))) for m in team_data if str(m.team_size).replace('.', '').isdigit())
                    return f"Portfolio team insights:\n• Total employees across portfolio: {total_employees}\n• Data from {len(team_data)} companies"
                else:
                    return "No team size data available in recent metrics."
            
            elif "customer" in question:
                customer_data = self.session.query(FinancialMetrics).join(Company).filter(
                    Company.is_tweener_portfolio == True,
                    FinancialMetrics.customer_count.isnot(None),
                    FinancialMetrics.customer_count != 'N/A',
                    FinancialMetrics.customer_count != '-'
                ).order_by(FinancialMetrics.extracted_date.desc()).limit(20).all()
                
                if customer_data:
                    total_customers = sum(int(float(str(m.customer_count))) for m in customer_data if str(m.customer_count).replace('.', '').isdigit())
                    return f"Portfolio customer insights:\n• Total customers across portfolio: {total_customers:,}\n• Data from {len(customer_data)} companies"
                else:
                    return "No customer count data available in recent metrics."
        
        except Exception as e:
            return f"Error retrieving operational data: {str(e)}"
    
    def _handle_portfolio_overview(self):
        """Provide portfolio overview"""
        try:
            total_companies = self.session.query(Company).filter(Company.is_tweener_portfolio == True).count()
            companies_with_metrics = self.session.query(FinancialMetrics).join(Company).filter(
                Company.is_tweener_portfolio == True
            ).distinct(FinancialMetrics.company_id).count()
            recent_updates = self.session.query(FinancialMetrics).join(Company).filter(
                Company.is_tweener_portfolio == True,
                FinancialMetrics.extracted_date >= datetime.now() - timedelta(days=30)
            ).count()
            
            overview = f"""📊 **Portfolio Overview:**
• **Total Companies:** {total_companies}
• **Companies with Metrics:** {companies_with_metrics}
• **Coverage:** {(companies_with_metrics/total_companies*100):.1f}%
• **Recent Updates (30 days):** {recent_updates}

The dashboard shows detailed financial metrics, growth rates, and operational data for our portfolio companies."""
            
            return overview
        
        except Exception as e:
            return f"Error generating portfolio overview: {str(e)}"
    
    def _handle_recent_updates(self):
        """Show recent updates"""
        try:
            recent = self.session.query(FinancialMetrics).join(Company).filter(
                Company.is_tweener_portfolio == True
            ).order_by(
                FinancialMetrics.extracted_date.desc()
            ).limit(5).all()
            
            if not recent:
                return "No recent updates available."
            
            updates = "📅 **Recent Updates:**\n"
            for metric in recent:
                updates += f"• **{metric.company.name}** - {metric.extracted_date.strftime('%Y-%m-%d')}"
                if metric.arr and metric.arr not in ['N/A', '-']:
                    updates += f" (ARR: {metric.arr})"
                updates += "\n"
            
            return updates
        
        except Exception as e:
            return f"Error retrieving recent updates: {str(e)}"
    
    def _handle_performance_queries(self, question):
        """Handle performance comparison queries"""
        try:
            if "best" in question or "top" in question or "perform" in question:
                # Check if asking for both ARR and growth
                if "arr and growth" in question.lower() or "performance companies" in question.lower():
                    return self._get_top_companies_combined()
                # Check if asking specifically about ARR
                elif "arr" in question.lower():
                    return self._get_top_companies_by_arr()
                # Check if asking specifically about growth
                elif "growth" in question.lower():
                    return self._get_top_companies_by_growth()
                else:
                    # Default to combined performance
                    return self._get_top_companies_combined()
            
            return "I can help identify top performers. Try asking 'Which companies are performing best?' or 'Show me top companies by ARR'."
        
        except Exception as e:
            return f"Error analyzing performance: {str(e)}"
    
    def _get_top_companies_combined(self):
        """Get top 3 companies by both ARR and growth rate"""
        try:
            arr_result = self._get_top_companies_by_arr()
            growth_result = self._get_top_companies_by_growth()
            
            # Combine both results
            combined_result = "🏆 **TOP PERFORMANCE COMPANIES**\n\n"
            combined_result += arr_result + "\n\n"
            combined_result += growth_result
            
            return combined_result
            
        except Exception as e:
            return f"Error retrieving combined performance data: {str(e)}"
    
    def _get_top_companies_by_arr(self):
        """Get top 3 companies by ARR"""
        try:
            # Get latest ARR data for each company (only portfolio companies)
            arr_data = self.session.query(FinancialMetrics).join(Company).filter(
                Company.is_tweener_portfolio == True,
                FinancialMetrics.arr.isnot(None),
                FinancialMetrics.arr != 'N/A',
                FinancialMetrics.arr != '-'
            ).order_by(FinancialMetrics.extracted_date.desc()).limit(50).all()
            
            if not arr_data:
                return "No ARR data available for comparison."
            
            # Get latest ARR for each company
            company_arr = {}
            for metric in arr_data:
                arr_value = self._parse_financial_value(metric.arr)
                if arr_value > 0:
                    if metric.company.name not in company_arr or arr_value > company_arr[metric.company.name]:
                        company_arr[metric.company.name] = arr_value
            
            if company_arr:
                top_performers = sorted(company_arr.items(), key=lambda x: x[1], reverse=True)[:3]
                result = "💰 **Top 3 Companies by ARR:**\n"
                for i, (company, arr) in enumerate(top_performers, 1):
                    result += f"{i}. **{company}**: ${arr:,.0f} ARR\n"
                return result
            else:
                return "Unable to parse ARR data for comparison."
                
        except Exception as e:
            return f"Error retrieving ARR data: {str(e)}"
    
    def _get_top_companies_by_growth(self):
        """Get top 3 companies by growth rate"""
        try:
            # Find companies with highest growth (only portfolio companies)
            growth_data = self.session.query(FinancialMetrics).join(Company).filter(
                Company.is_tweener_portfolio == True,
                FinancialMetrics.arr_growth.isnot(None),
                FinancialMetrics.arr_growth != 'N/A',
                FinancialMetrics.arr_growth != '-'
            ).order_by(FinancialMetrics.extracted_date.desc()).limit(50).all()
            
            if not growth_data:
                return "No growth data available for comparison."
            
            company_growth = {}
            for metric in growth_data:
                try:
                    growth_str = str(metric.arr_growth).replace('+', '').replace('%', '')
                    growth_rate = float(growth_str)
                    if metric.company.name not in company_growth or growth_rate > company_growth[metric.company.name]:
                        company_growth[metric.company.name] = growth_rate
                except:
                    continue
            
            if company_growth:
                top_performers = sorted(company_growth.items(), key=lambda x: x[1], reverse=True)[:3]
                result = "🚀 **Top 3 Companies by Growth Rate:**\n"
                for i, (company, growth) in enumerate(top_performers, 1):
                    result += f"{i}. **{company}**: {growth:.1f}% growth\n"
                return result
            else:
                return "Unable to parse growth data for comparison."
                
        except Exception as e:
            return f"Error retrieving growth data: {str(e)}"
    
    def _get_company_details(self, company_name):
        """Get detailed information about a specific company"""
        try:
            company = self.session.query(Company).filter(
                Company.is_tweener_portfolio == True,
                Company.name.ilike(f"%{company_name}%")
            ).first()
            if not company:
                return f"Company '{company_name}' not found in our portfolio."
            
            # Get latest metrics for this company
            latest_metric = self.session.query(FinancialMetrics).filter(
                FinancialMetrics.company_id == company.id
            ).order_by(FinancialMetrics.extracted_date.desc()).first()
            
            if not latest_metric:
                return f"**{company.name}** is in our portfolio, but no financial metrics are available yet."
            
            details = f"""📈 **{company.name} - Latest Metrics:**
• **Last Updated:** {latest_metric.extracted_date.strftime('%Y-%m-%d')}
• **ARR:** {latest_metric.arr if latest_metric.arr not in ['N/A', '-'] else 'Not available'}
• **MRR:** {latest_metric.mrr if latest_metric.mrr not in ['N/A', '-'] else 'Not available'}
• **Growth:** {latest_metric.arr_growth if latest_metric.arr_growth not in ['N/A', '-'] else 'Not available'}
• **Cash Balance:** {latest_metric.cash_balance if latest_metric.cash_balance not in ['N/A', '-'] else 'Not available'}
• **Runway:** {latest_metric.runway_months if latest_metric.runway_months not in ['N/A', '-'] else 'Not available'}
• **Team Size:** {latest_metric.team_size if latest_metric.team_size not in ['N/A', '-'] else 'Not available'}
• **Customers:** {latest_metric.customer_count if latest_metric.customer_count not in ['N/A', '-'] else 'Not available'}"""
            
            return details
        
        except Exception as e:
            return f"Error retrieving company details: {str(e)}"
    
    def _provide_help(self):
        """Provide help information"""
        return """🤖 **I can help you with:**

**Company Information:**
• "How many companies do we track?"
• "List all companies"
• "Tell me about [Company Name]"

**Financial Metrics:**
• "What's our total ARR?"
• "Show me MRR data"
• "Financial overview"

**Growth Analysis:**
• "Which companies are growing fastest?"
• "Show me growth rates"

**Cash & Runway:**
• "How much cash do we have?"
• "What's our average runway?"

**Operations:**
• "How many employees across portfolio?"
• "Customer count summary"

**General:**
• "Portfolio overview"
• "Recent updates"
• "Top performance companies" (shows both ARR and growth rankings)

Just ask me a question about our portfolio companies!"""
    
    def _parse_financial_value(self, value_str):
        """Parse financial values like '$1.2M' or '$50K' to numbers"""
        if not value_str or value_str in ['N/A', '-']:
            return 0
        
        try:
            # Remove currency symbols and spaces
            clean_str = str(value_str).replace('$', '').replace(',', '').strip()
            
            # Handle K/M suffixes
            if clean_str.upper().endswith('K'):
                return float(clean_str[:-1]) * 1000
            elif clean_str.upper().endswith('M'):
                return float(clean_str[:-1]) * 1000000
            else:
                return float(clean_str)
        except:
            return 0
    
    def _parse_runway_months(self, runway_str):
        """Parse runway months from strings like '12-18' or '12 months'"""
        if not runway_str or runway_str in ['N/A', '-']:
            return 0
        
        try:
            runway_str = str(runway_str).replace('months', '').strip()
            
            # Handle range values like "12-18"
            if '-' in runway_str:
                parts = runway_str.split('-')
                return (float(parts[0]) + float(parts[1])) / 2
            else:
                return float(runway_str)
        except:
            return 0

def main():
    # Simple header
    st.title("🤖 Tweener Portfolio Assistant")
    st.markdown("**Ask me anything about your Tweener Fund portfolio companies**")
    
    st.markdown("---")
    
    # Initialize chatbot in session state
    if 'chatbot' not in st.session_state:
        st.session_state.chatbot = DatabaseChatbot()
    
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []
    
    # Welcome message and instructions
    if not st.session_state.chat_history:
        st.markdown("""
        <div class="welcome-message">
            <h2 style="margin: 0; color: white;">👋 Welcome to Tweener Portfolio Assistant!</h2>
            <p style="margin: 0.5rem 0 0 0; color: white;">I'm your AI assistant for analyzing Tweener Fund portfolio companies. Ask me anything about financial metrics, growth rates, team sizes, and more!</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick action buttons
    st.markdown("### 🚀 Quick Questions")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📊 Portfolio Overview", key="quick_overview"):
            response = st.session_state.chatbot.query_database("portfolio overview")
            st.session_state.chat_history.append(("Portfolio Overview", response))
            st.rerun()
    
    with col2:
        if st.button("🏢 List Companies", key="quick_companies"):
            response = st.session_state.chatbot.query_database("list all companies")
            st.session_state.chat_history.append(("List Companies", response))
            st.rerun()
    
    with col3:
        if st.button("🚀 Top Performance Companies", key="quick_performers"):
            response = st.session_state.chatbot.query_database("top performance companies by ARR and growth")
            st.session_state.chat_history.append(("Top Performance Companies", response))
            st.rerun()
    
    st.markdown("---")
    
    # Chat interface
    st.markdown("### 💬 Chat with Your Portfolio Data")
    
    # Chat input
    user_input = st.text_input(
        "Ask me anything about your portfolio...",
        placeholder="e.g., 'How is Altis Biosystems performing?' or 'Which companies need more runway?'",
        key="chat_input_field"
    )
    
    col1, col2, col3 = st.columns([1, 1, 4])
    with col1:
        send_button = st.button("Send 💬", key="send_chat")
    with col2:
        if st.button("Clear Chat 🗑️", key="clear_chat"):
            st.session_state.chat_history = []
            st.rerun()
    
    # Process chat input
    if send_button and user_input.strip():
        with st.spinner("🤔 Analyzing your portfolio data..."):
            response = st.session_state.chatbot.query_database(user_input)
        
        # Add to chat history
        st.session_state.chat_history.append((user_input, response))
        st.rerun()
    
    # Chat history display
    if st.session_state.chat_history:
        st.markdown("### 💭 Conversation History")
        
        for i, (user_msg, bot_msg) in enumerate(reversed(st.session_state.chat_history)):
            # User message
            st.markdown(f"""
            <div class="chat-message user">
                <strong>You:</strong> {user_msg}
            </div>
            """, unsafe_allow_html=True)
            
            # Bot response - use markdown container with styling
            st.markdown("""
            <div class="chat-message assistant">
                <strong>Assistant:</strong>
            </div>
            """, unsafe_allow_html=True)
            
            # Display bot message as markdown to properly render formatting
            st.markdown(bot_msg)
            
            if i < len(st.session_state.chat_history) - 1:
                st.markdown("---")
    
    # Footer
    st.markdown("---")
    st.markdown(f"**Last updated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    st.markdown("**Data source:** Portfolio company email updates and financial metrics")

if __name__ == "__main__":
    main() 