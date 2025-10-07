"""Financial Summarization Workflow"""
import os
import re
from typing import List, Dict, Any, Optional
from datetime import datetime
import json

from .base import BaseWorkflow
from ..models import FinancialDocument, FinancialSummary, FinancialMetrics


class FinancialSummarizationWorkflow(BaseWorkflow):
    """
    Workflow for summarizing financial documents using LLM
    
    Steps:
    1. Parse text and numeric data from documents
    2. Run LLM summarization to extract key insights
    3. Standardize format into a structured summary report
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.summary_length = config.get('summary_length', 'concise')
        self.include_metrics = config.get('include_metrics', True)
        self.llm_config = config.get('llm', {})
        
        # Initialize LLM client if API key is available
        self.llm_client = None
        if os.getenv('OPENAI_API_KEY'):
            try:
                from openai import OpenAI
                self.llm_client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            except ImportError:
                self.logger.warning("OpenAI library not installed. Using rule-based summarization.")
    
    def execute(self, documents: List[FinancialDocument]) -> FinancialSummary:
        """
        Execute financial summarization workflow
        
        Args:
            documents: List of FinancialDocument objects to summarize
            
        Returns:
            FinancialSummary object with extracted insights
        """
        self.logger.info(f"Starting financial summarization for {len(documents)} documents")
        
        if not documents:
            raise ValueError("No documents provided for summarization")
        
        # Step 1: Parse and aggregate data from all documents
        parsed_data = self._parse_documents(documents)
        self.logger.info("Parsed document data")
        
        # Step 2: Extract financial metrics
        metrics = self._extract_metrics(parsed_data)
        self.logger.info("Extracted financial metrics")
        
        # Step 3: Generate summary using LLM or rule-based approach
        if self.llm_client:
            summary_text = self._generate_llm_summary(parsed_data, metrics)
            insights = self._extract_llm_insights(parsed_data, metrics)
        else:
            summary_text = self._generate_rule_based_summary(parsed_data, metrics)
            insights = self._extract_rule_based_insights(parsed_data, metrics)
        
        self.logger.info("Generated summary")
        
        # Step 4: Identify trends, risks, and opportunities
        trends = self._identify_trends(parsed_data, metrics)
        risks = self._identify_risks(parsed_data, metrics)
        opportunities = self._identify_opportunities(parsed_data, metrics)
        
        # Step 5: Create standardized summary object
        summary = FinancialSummary(
            summary_id=self._generate_summary_id(documents),
            source_document_ids=[doc.document_id for doc in documents],
            executive_summary=summary_text,
            key_insights=insights,
            metrics=metrics,
            period_start=self._get_earliest_date(documents),
            period_end=self._get_latest_date(documents),
            department=documents[0].department if documents else None,
            trends=trends,
            risks=risks,
            opportunities=opportunities,
            generated_at=datetime.now(),
            confidence_score=0.85 if self.llm_client else 0.70
        )
        
        self.logger.info("Financial summarization completed")
        return summary
    
    def _parse_documents(self, documents: List[FinancialDocument]) -> Dict[str, Any]:
        """
        Parse and aggregate data from multiple documents
        
        Args:
            documents: List of documents to parse
            
        Returns:
            Dictionary containing aggregated parsed data
        """
        parsed_data = {
            'documents': documents,
            'combined_content': '',
            'all_key_figures': {},
            'all_tables': [],
            'metadata': {
                'total_documents': len(documents),
                'document_types': {},
                'departments': set()
            }
        }
        
        for doc in documents:
            # Aggregate content
            parsed_data['combined_content'] += f"\n\n--- {doc.title} ---\n{doc.content}"
            
            # Aggregate key figures
            for key, value in doc.key_figures.items():
                if key not in parsed_data['all_key_figures']:
                    parsed_data['all_key_figures'][key] = []
                parsed_data['all_key_figures'][key].append(value)
            
            # Aggregate tables
            parsed_data['all_tables'].extend(doc.tables)
            
            # Track metadata
            doc_type = doc.document_type.value
            parsed_data['metadata']['document_types'][doc_type] = \
                parsed_data['metadata']['document_types'].get(doc_type, 0) + 1
            
            if doc.department:
                parsed_data['metadata']['departments'].add(doc.department)
        
        return parsed_data
    
    def _extract_metrics(self, parsed_data: Dict[str, Any]) -> FinancialMetrics:
        """
        Extract and calculate financial metrics from parsed data
        
        Args:
            parsed_data: Aggregated parsed data
            
        Returns:
            FinancialMetrics object
        """
        key_figures = parsed_data['all_key_figures']
        
        # Calculate aggregate metrics
        revenue = sum(key_figures.get('revenue', []))
        expenses = sum(key_figures.get('expenses', []))
        net_income = sum(key_figures.get('net_income', [])) or (revenue - expenses if revenue or expenses else None)
        
        # Calculate derived metrics
        gross_margin = None
        if revenue and revenue > 0:
            gross_margin = ((revenue - expenses) / revenue * 100) if expenses else None
        
        # Calculate growth rates if we have multiple periods
        revenue_growth = None
        expense_growth = None
        
        if len(key_figures.get('revenue', [])) >= 2:
            revenues = key_figures['revenue']
            revenue_growth = ((revenues[-1] - revenues[0]) / revenues[0] * 100) if revenues[0] != 0 else None
        
        if len(key_figures.get('expenses', [])) >= 2:
            expenses_list = key_figures['expenses']
            expense_growth = ((expenses_list[-1] - expenses_list[0]) / expenses_list[0] * 100) if expenses_list[0] != 0 else None
        
        # Custom metrics
        custom_metrics = {}
        for key, values in key_figures.items():
            if key not in ['revenue', 'expenses', 'net_income']:
                custom_metrics[key] = sum(values)
        
        return FinancialMetrics(
            revenue=revenue if revenue else None,
            expenses=expenses if expenses else None,
            net_income=net_income,
            gross_margin=gross_margin,
            revenue_growth=revenue_growth,
            expense_growth=expense_growth,
            custom_metrics=custom_metrics
        )
    
    def _generate_llm_summary(self, parsed_data: Dict[str, Any], metrics: FinancialMetrics) -> str:
        """Generate executive summary using LLM"""
        content = parsed_data['combined_content']
        
        # Limit content length for API
        max_content_length = 8000
        if len(content) > max_content_length:
            content = content[:max_content_length] + "..."
        
        prompt = f"""Analyze the following financial documents and provide a concise executive summary.

Financial Metrics:
- Revenue: ${metrics.revenue:,.2f} if metrics.revenue else 'N/A'}
- Expenses: ${metrics.expenses:,.2f} if metrics.expenses else 'N/A'}
- Net Income: ${metrics.net_income:,.2f} if metrics.net_income else 'N/A'}
- Gross Margin: {metrics.gross_margin:.2f}% if metrics.gross_margin else 'N/A'}

Documents:
{content}

Provide a {self.summary_length} executive summary (2-3 paragraphs) highlighting:
1. Overall financial performance
2. Key metrics and their significance
3. Notable trends or patterns
"""
        
        try:
            response = self.llm_client.chat.completions.create(
                model=self.llm_config.get('model', 'gpt-4'),
                messages=[
                    {"role": "system", "content": "You are a financial analyst expert at summarizing financial documents."},
                    {"role": "user", "content": prompt}
                ],
                temperature=self.llm_config.get('temperature', 0.3),
                max_tokens=self.llm_config.get('max_tokens', 500)
            )
            
            return response.choices[0].message.content.strip()
        
        except Exception as e:
            self.logger.error(f"Error generating LLM summary: {e}")
            return self._generate_rule_based_summary(parsed_data, metrics)
    
    def _generate_rule_based_summary(self, parsed_data: Dict[str, Any], metrics: FinancialMetrics) -> str:
        """Generate executive summary using rule-based approach"""
        summary_parts = []
        
        # Overall performance
        if metrics.net_income and metrics.net_income > 0:
            summary_parts.append(f"The organization demonstrates positive financial performance with a net income of ${metrics.net_income:,.2f}.")
        elif metrics.net_income and metrics.net_income < 0:
            summary_parts.append(f"The organization faces financial challenges with a net loss of ${abs(metrics.net_income):,.2f}.")
        
        # Revenue and expenses
        if metrics.revenue and metrics.expenses:
            summary_parts.append(
                f"Total revenue stands at ${metrics.revenue:,.2f} with expenses of ${metrics.expenses:,.2f}, "
                f"resulting in a gross margin of {metrics.gross_margin:.1f}%." if metrics.gross_margin 
                else f"Total revenue stands at ${metrics.revenue:,.2f} with expenses of ${metrics.expenses:,.2f}."
            )
        
        # Growth trends
        growth_statements = []
        if metrics.revenue_growth:
            direction = "growth" if metrics.revenue_growth > 0 else "decline"
            growth_statements.append(f"revenue {direction} of {abs(metrics.revenue_growth):.1f}%")
        
        if metrics.expense_growth:
            direction = "increase" if metrics.expense_growth > 0 else "decrease"
            growth_statements.append(f"expense {direction} of {abs(metrics.expense_growth):.1f}%")
        
        if growth_statements:
            summary_parts.append(f"Period-over-period analysis shows {' and '.join(growth_statements)}.")
        
        # Document coverage
        num_docs = parsed_data['metadata']['total_documents']
        doc_types = list(parsed_data['metadata']['document_types'].keys())
        summary_parts.append(
            f"This summary analyzes {num_docs} financial document(s) "
            f"including {', '.join(doc_types)}."
        )
        
        return " ".join(summary_parts)
    
    def _extract_llm_insights(self, parsed_data: Dict[str, Any], metrics: FinancialMetrics) -> List[str]:
        """Extract key insights using LLM"""
        content = parsed_data['combined_content'][:8000]
        
        prompt = f"""Based on these financial documents, identify 5-7 key insights:

Financial Metrics:
- Revenue: ${metrics.revenue:,.2f} if metrics.revenue else 'N/A'}
- Expenses: ${metrics.expenses:,.2f} if metrics.expenses else 'N/A'}
- Net Income: ${metrics.net_income:,.2f} if metrics.net_income else 'N/A'}

Documents:
{content}

Provide specific, actionable insights as a bullet list."""
        
        try:
            response = self.llm_client.chat.completions.create(
                model=self.llm_config.get('model', 'gpt-4'),
                messages=[
                    {"role": "system", "content": "You are a financial analyst. Provide specific, quantifiable insights."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            content = response.choices[0].message.content.strip()
            # Parse bullet points
            insights = [line.strip('- •*').strip() for line in content.split('\n') if line.strip()]
            return [insight for insight in insights if len(insight) > 10]
        
        except Exception as e:
            self.logger.error(f"Error extracting LLM insights: {e}")
            return self._extract_rule_based_insights(parsed_data, metrics)
    
    def _extract_rule_based_insights(self, parsed_data: Dict[str, Any], metrics: FinancialMetrics) -> List[str]:
        """Extract key insights using rule-based approach"""
        insights = []
        
        if metrics.revenue:
            insights.append(f"Total revenue of ${metrics.revenue:,.2f} represents the organization's income generation capacity.")
        
        if metrics.gross_margin:
            if metrics.gross_margin > 40:
                insights.append(f"Strong gross margin of {metrics.gross_margin:.1f}% indicates healthy profitability.")
            elif metrics.gross_margin < 20:
                insights.append(f"Gross margin of {metrics.gross_margin:.1f}% suggests potential profitability concerns.")
        
        if metrics.revenue_growth:
            if metrics.revenue_growth > 10:
                insights.append(f"Revenue growth of {metrics.revenue_growth:.1f}% demonstrates strong business expansion.")
            elif metrics.revenue_growth < -10:
                insights.append(f"Revenue decline of {abs(metrics.revenue_growth):.1f}% requires strategic attention.")
        
        if metrics.expense_growth and metrics.revenue_growth:
            if metrics.expense_growth > metrics.revenue_growth:
                insights.append("Expenses are growing faster than revenue, impacting profitability.")
        
        return insights
    
    def _identify_trends(self, parsed_data: Dict[str, Any], metrics: FinancialMetrics) -> List[str]:
        """Identify financial trends"""
        trends = []
        
        if metrics.revenue_growth and metrics.revenue_growth > 5:
            trends.append("Upward revenue trend indicating business growth")
        elif metrics.revenue_growth and metrics.revenue_growth < -5:
            trends.append("Downward revenue trend requiring corrective action")
        
        if metrics.expense_growth:
            if metrics.expense_growth > 10:
                trends.append("Significant increase in operational expenses")
            elif metrics.expense_growth < -10:
                trends.append("Successful cost reduction initiatives")
        
        return trends
    
    def _identify_risks(self, parsed_data: Dict[str, Any], metrics: FinancialMetrics) -> List[str]:
        """Identify financial risks"""
        risks = []
        
        if metrics.net_income and metrics.net_income < 0:
            risks.append("Negative net income indicates financial sustainability risk")
        
        if metrics.gross_margin and metrics.gross_margin < 15:
            risks.append("Low gross margin limits financial flexibility")
        
        if metrics.expense_growth and metrics.revenue_growth:
            if metrics.expense_growth > metrics.revenue_growth + 5:
                risks.append("Expense growth outpacing revenue growth threatens profitability")
        
        return risks
    
    def _identify_opportunities(self, parsed_data: Dict[str, Any], metrics: FinancialMetrics) -> List[str]:
        """Identify opportunities for improvement"""
        opportunities = []
        
        if metrics.revenue_growth and metrics.revenue_growth > 0:
            opportunities.append("Leverage positive revenue momentum for market expansion")
        
        if metrics.gross_margin and metrics.gross_margin > 30:
            opportunities.append("Strong margins provide capacity for strategic investments")
        
        if metrics.expense_growth and metrics.expense_growth < 0:
            opportunities.append("Cost optimization success can be replicated across other areas")
        
        return opportunities
    
    def _get_earliest_date(self, documents: List[FinancialDocument]) -> Optional[datetime]:
        """Get earliest period start date from documents"""
        dates = [doc.period_start for doc in documents if doc.period_start]
        return min(dates) if dates else None
    
    def _get_latest_date(self, documents: List[FinancialDocument]) -> Optional[datetime]:
        """Get latest period end date from documents"""
        dates = [doc.period_end for doc in documents if doc.period_end]
        return max(dates) if dates else None
    
    def _generate_summary_id(self, documents: List[FinancialDocument]) -> str:
        """Generate unique summary ID"""
        doc_ids = "_".join([doc.document_id[:8] for doc in documents[:3]])
        return f"summary_{doc_ids}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
