"""
Example: Running Individual Workflows Separately
"""
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.pipeline import FinancialPipeline


def main():
    """Example of running each workflow separately"""
    
    print("=" * 80)
    print("Example: Individual Workflow Execution")
    print("=" * 80)
    print()
    
    # Initialize pipeline
    pipeline = FinancialPipeline(config_path='config.yaml')
    
    # Query parameters
    query = {
        'keywords': ['budget', 'expense'],
        'date_range': (datetime.now() - timedelta(days=90), datetime.now()),
        'sources': ['blob'],
        'limit': 5
    }
    
    budget_data = {
        'total_budget': 1000000,
        'department_budgets': {'Engineering': 500000, 'Sales': 500000},
        'category_budgets': {'Salaries': 600000, 'Equipment': 400000}
    }
    
    # Workflow 1: Document Retrieval
    print("1. Running Document Retrieval Workflow")
    print("-" * 80)
    try:
        documents = pipeline.run_document_retrieval(query)
        print(f"✓ Retrieved {len(documents)} documents")
        
        for i, doc in enumerate(documents[:3], 1):
            print(f"   {i}. {doc.title} (Type: {doc.document_type.value})")
    except Exception as e:
        print(f"✗ Error: {e}")
        documents = []
    
    print()
    
    # Workflow 2: Financial Summarization
    if documents:
        print("2. Running Financial Summarization Workflow")
        print("-" * 80)
        try:
            summary = pipeline.run_financial_summarization(documents)
            print(f"✓ Generated financial summary")
            print(f"   Executive Summary: {summary.executive_summary[:150]}...")
            print(f"   Key Insights: {len(summary.key_insights)} insights identified")
            
            if summary.metrics.revenue:
                print(f"   Revenue: ${summary.metrics.revenue:,.2f}")
        except Exception as e:
            print(f"✗ Error: {e}")
            summary = None
        
        print()
        
        # Workflow 3: Budget Insights
        if summary:
            print("3. Running Budget Insights Workflow")
            print("-" * 80)
            try:
                insights = pipeline.run_budget_insights(summary, budget_data)
                print(f"✓ Generated budget insights")
                print(f"   Health Score: {insights.budget_health_score:.1f}/100")
                print(f"   Variances Identified: {len(insights.variances)}")
                print(f"   Anomalies Detected: {len(insights.anomalies)}")
                
                # Show critical issues
                critical_issues = insights.get_critical_issues()
                if critical_issues:
                    print(f"\n   ⚠️  Critical Issues:")
                    for issue in critical_issues:
                        print(f"      - {issue}")
            except Exception as e:
                print(f"✗ Error: {e}")
    
    print()
    print("=" * 80)
    print("Individual workflow execution completed!")
    print("=" * 80)


if __name__ == '__main__':
    main()
