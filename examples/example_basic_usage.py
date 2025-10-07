"""
Example: Basic Usage of Financial Data Processing Pipeline
"""
import os
import sys
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.pipeline import FinancialPipeline


def main():
    """Basic example of running the pipeline"""
    
    print("=" * 80)
    print("Example: Basic Financial Pipeline Usage")
    print("=" * 80)
    print()
    
    # Initialize pipeline
    print("1. Initializing pipeline...")
    pipeline = FinancialPipeline(config_path='config.yaml')
    print("   ✓ Pipeline initialized")
    print()
    
    # Define query for document retrieval
    print("2. Preparing query...")
    query = {
        'keywords': ['quarterly', 'budget', 'financial'],
        'document_type': 'quarterly_report',
        'department': 'Engineering',
        'date_range': (
            datetime.now() - timedelta(days=90),
            datetime.now()
        ),
        'sources': ['blob'],  # Query Azure Blob Storage
        'limit': 10
    }
    print(f"   ✓ Query prepared for: {query['department']}")
    print()
    
    # Define budget data for comparison
    print("3. Preparing budget data...")
    budget_data = {
        'total_budget': 5000000,
        'department_budgets': {
            'Engineering': 2000000,
            'Sales': 1500000,
            'Marketing': 1000000,
            'Operations': 500000
        },
        'category_budgets': {
            'Salaries': 2500000,
            'Equipment': 1000000,
            'Marketing': 800000,
            'Travel': 400000,
            'Other': 300000
        },
        'expected_profit': 1000000
    }
    print(f"   ✓ Budget data prepared (Total: ${budget_data['total_budget']:,})")
    print()
    
    # Run the full pipeline
    print("4. Running pipeline...")
    print("-" * 80)
    try:
        results = pipeline.run_full_pipeline(query, budget_data)
        print("-" * 80)
        print()
        
        # Display results
        print("5. Results:")
        print()
        
        if results.get('documents_count'):
            print(f"   📄 Documents Retrieved: {results['documents_count']}")
        
        if results.get('summary'):
            summary = results['summary']
            print(f"\n   📊 Financial Summary:")
            print(f"      - Executive Summary: {summary['executive_summary'][:150]}...")
            
            if summary.get('metrics'):
                metrics = summary['metrics']
                print(f"\n      Financial Metrics:")
                if metrics.get('revenue'):
                    print(f"      - Revenue: ${metrics['revenue']:,.2f}")
                if metrics.get('expenses'):
                    print(f"      - Expenses: ${metrics['expenses']:,.2f}")
                if metrics.get('net_income'):
                    print(f"      - Net Income: ${metrics['net_income']:,.2f}")
        
        if results.get('insights'):
            insights = results['insights']
            print(f"\n   💡 Budget Insights:")
            print(f"      - Health Score: {insights['budget_health_score']:.1f}/100")
            print(f"      - Status: {insights['health_status']}")
            print(f"      - Variance: ${insights['total_variance']:,.2f} ({insights['total_variance_percentage']:.1f}%)")
            
            if insights.get('key_findings'):
                print(f"\n      Key Findings:")
                for finding in insights['key_findings'][:3]:
                    print(f"      • {finding}")
            
            if insights.get('recommendations'):
                print(f"\n      Recommendations:")
                for i, rec in enumerate(insights['recommendations'][:3], 1):
                    print(f"      {i}. {rec}")
        
        # Save results
        print()
        saved_path = pipeline.save_results(results)
        print(f"   💾 Results saved to: {saved_path}")
        
        print()
        print("=" * 80)
        print("✓ Pipeline completed successfully!")
        print("=" * 80)
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
