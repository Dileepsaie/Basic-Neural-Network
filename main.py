"""
Main Entry Point for Financial Data Processing Pipeline
"""
import os
import sys
import argparse
import json
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.pipeline import FinancialPipeline


def main():
    """Main entry point"""
    
    # Load environment variables
    load_dotenv()
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(
        description='Financial Data Processing Pipeline - Azure Edition'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='Path to configuration file (default: config.yaml)'
    )
    
    parser.add_argument(
        '--workflow',
        type=str,
        choices=['full', 'retrieval', 'summarization', 'insights'],
        default='full',
        help='Workflow to run (default: full)'
    )
    
    parser.add_argument(
        '--keywords',
        type=str,
        nargs='+',
        help='Keywords to search for documents'
    )
    
    parser.add_argument(
        '--document-type',
        type=str,
        choices=['quarterly_report', 'annual_report', 'budget', 'contract', 'invoice', 'expense_report'],
        help='Type of documents to retrieve'
    )
    
    parser.add_argument(
        '--department',
        type=str,
        help='Department filter'
    )
    
    parser.add_argument(
        '--days-back',
        type=int,
        default=90,
        help='Number of days back to search (default: 90)'
    )
    
    parser.add_argument(
        '--sources',
        type=str,
        nargs='+',
        default=['blob', 'sql', 'synapse', 'dataverse'],
        choices=['blob', 'sql', 'synapse', 'dataverse'],
        help='Data sources to query (default: all)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path for results'
    )
    
    parser.add_argument(
        '--example',
        action='store_true',
        help='Run with example data'
    )
    
    args = parser.parse_args()
    
    print("=" * 80)
    print("Financial Data Processing Pipeline - Azure Edition")
    print("=" * 80)
    print()
    
    # Initialize pipeline
    print(f"Loading configuration from: {args.config}")
    pipeline = FinancialPipeline(config_path=args.config)
    
    # Check status
    status = pipeline.get_status()
    print("\nPipeline Status:")
    for workflow, state in status['workflows'].items():
        print(f"  - {workflow}: {state}")
    print()
    
    # Prepare query
    if args.example:
        print("Running with EXAMPLE data...")
        query = get_example_query()
        budget_data = get_example_budget_data()
    else:
        # Build query from arguments
        end_date = datetime.now()
        start_date = end_date - timedelta(days=args.days_back)
        
        query = {
            'keywords': args.keywords or ['financial', 'budget', 'expense'],
            'document_type': args.document_type,
            'department': args.department,
            'date_range': (start_date, end_date),
            'sources': args.sources,
            'limit': 50
        }
        
        # Default budget data (should be customized)
        budget_data = {
            'total_budget': 1000000,
            'department_budgets': {
                'Engineering': 400000,
                'Sales': 300000,
                'Marketing': 200000,
                'Operations': 100000
            },
            'category_budgets': {
                'Salaries': 500000,
                'Equipment': 200000,
                'Marketing': 150000,
                'Travel': 100000,
                'Other': 50000
            },
            'expected_profit': 200000
        }
        
        print(f"Query Configuration:")
        print(f"  - Keywords: {query['keywords']}")
        print(f"  - Date Range: {start_date.date()} to {end_date.date()}")
        print(f"  - Department: {args.department or 'All'}")
        print(f"  - Sources: {', '.join(args.sources)}")
        print()
    
    # Run pipeline
    if args.workflow == 'full':
        print("Running FULL pipeline (Retrieval → Summarization → Insights)")
        print("-" * 80)
        results = pipeline.run_full_pipeline(query, budget_data)
    else:
        print(f"Running {args.workflow.upper()} workflow only")
        print("-" * 80)
        results = run_single_workflow(pipeline, args.workflow, query, budget_data)
    
    # Display results summary
    print()
    print("=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    
    if 'documents_count' in results:
        print(f"\n📄 Documents Retrieved: {results['documents_count']}")
    
    if 'summary' in results:
        summary = results['summary']
        print(f"\n📊 Financial Summary:")
        print(f"   Executive Summary: {summary['executive_summary'][:200]}...")
        if summary.get('metrics'):
            metrics = summary['metrics']
            if metrics.get('revenue'):
                print(f"   Revenue: ${metrics['revenue']:,.2f}")
            if metrics.get('expenses'):
                print(f"   Expenses: ${metrics['expenses']:,.2f}")
            if metrics.get('net_income'):
                print(f"   Net Income: ${metrics['net_income']:,.2f}")
    
    if 'insights' in results:
        insights = results['insights']
        print(f"\n💡 Budget Insights:")
        print(f"   Health Score: {insights['budget_health_score']:.1f}/100")
        print(f"   Status: {insights['health_status']}")
        print(f"   Total Budget: ${insights['total_budget']:,.2f}")
        print(f"   Total Actual: ${insights['total_actual']:,.2f}")
        print(f"   Variance: ${insights['total_variance']:,.2f} ({insights['total_variance_percentage']:.1f}%)")
        
        if insights.get('anomalies'):
            print(f"\n   ⚠️  Anomalies Detected: {len(insights['anomalies'])}")
            for anomaly in insights['anomalies'][:3]:
                print(f"      - {anomaly['anomaly_type']}: {anomaly['description']}")
        
        if insights.get('recommendations'):
            print(f"\n   💭 Top Recommendations:")
            for i, rec in enumerate(insights['recommendations'][:3], 1):
                print(f"      {i}. {rec}")
    
    # Save results
    if args.output:
        output_path = args.output
    else:
        output_path = None
    
    saved_path = pipeline.save_results(results, output_path)
    print(f"\n💾 Full results saved to: {saved_path}")
    
    print("\n" + "=" * 80)
    print("Pipeline execution completed!")
    print("=" * 80)


def run_single_workflow(pipeline, workflow_name, query, budget_data):
    """Run a single workflow"""
    results = {'metadata': {'workflow': workflow_name}}
    
    if workflow_name == 'retrieval':
        documents = pipeline.run_document_retrieval(query)
        results['documents'] = [doc.to_dict() for doc in documents]
        results['documents_count'] = len(documents)
    
    elif workflow_name == 'summarization':
        # First need to retrieve documents
        documents = pipeline.run_document_retrieval(query)
        summary = pipeline.run_financial_summarization(documents)
        results['documents_count'] = len(documents)
        results['summary'] = summary.to_dict()
    
    elif workflow_name == 'insights':
        # Need documents and summary first
        documents = pipeline.run_document_retrieval(query)
        summary = pipeline.run_financial_summarization(documents)
        insights = pipeline.run_budget_insights(summary, budget_data)
        results['documents_count'] = len(documents)
        results['summary'] = summary.to_dict()
        results['insights'] = insights.to_dict()
    
    return results


def get_example_query():
    """Get example query for testing"""
    return {
        'keywords': ['quarterly', 'budget', '2024'],
        'document_type': 'quarterly_report',
        'department': 'Engineering',
        'date_range': (
            datetime(2024, 1, 1),
            datetime(2024, 12, 31)
        ),
        'sources': ['blob'],  # Only blob for example
        'limit': 10
    }


def get_example_budget_data():
    """Get example budget data for testing"""
    return {
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
            'Office': 200000,
            'Other': 100000
        },
        'expected_profit': 1000000
    }


if __name__ == '__main__':
    main()
