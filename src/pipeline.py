"""Financial Data Processing Pipeline Orchestrator"""
import os
import json
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
import yaml

from .workflows import (
    FinancialSummarizationWorkflow,
    BudgetInsightsWorkflow
)
from .workflows.document_retrieval_azure import AzureDocumentRetrievalWorkflow
from .models import FinancialDocument, FinancialSummary, BudgetInsight


class FinancialPipeline:
    """
    Main Pipeline Orchestrator for Financial Data Processing
    
    Chains together three workflows:
    1. Document Retrieval (from Azure sources)
    2. Financial Summarization (using LLM)
    3. Budget Insights (anomaly detection and analysis)
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the pipeline
        
        Args:
            config_path: Path to configuration file (YAML)
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self._setup_logging()
        
        # Load configuration
        self.config = self._load_config(config_path)
        
        # Initialize workflows
        self.document_retrieval = None
        self.financial_summarization = None
        self.budget_insights = None
        
        self._initialize_workflows()
        
        self.logger.info("Financial Pipeline initialized")
    
    def _setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler(),
                logging.FileHandler('pipeline.log')
            ]
        )
    
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or environment"""
        config = {}
        
        # Try to load from file
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = yaml.safe_load(f)
            self.logger.info(f"Loaded configuration from {config_path}")
        elif os.path.exists('config.yaml'):
            with open('config.yaml', 'r') as f:
                config = yaml.safe_load(f)
            self.logger.info("Loaded configuration from config.yaml")
        else:
            self.logger.warning("No configuration file found, using defaults")
            config = self._get_default_config()
        
        # Replace environment variable placeholders
        config = self._resolve_env_vars(config)
        
        return config
    
    def _resolve_env_vars(self, config: Any) -> Any:
        """Recursively resolve environment variables in config"""
        if isinstance(config, dict):
            return {k: self._resolve_env_vars(v) for k, v in config.items()}
        elif isinstance(config, list):
            return [self._resolve_env_vars(item) for item in config]
        elif isinstance(config, str) and config.startswith('${') and config.endswith('}'):
            env_var = config[2:-1]
            return os.getenv(env_var, config)
        return config
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration"""
        return {
            'document_storage': {
                'type': 'azure_blob',
                'azure_blob': {
                    'storage_account_name': os.getenv('AZURE_STORAGE_ACCOUNT_NAME'),
                    'container_name': 'financial-documents',
                    'use_managed_identity': True
                }
            },
            'llm': {
                'provider': 'openai',
                'model': 'gpt-4',
                'temperature': 0.3
            },
            'workflows': {
                'document_retrieval': {'enabled': True},
                'financial_summarization': {'enabled': True},
                'budget_insights': {'enabled': True}
            }
        }
    
    def _initialize_workflows(self):
        """Initialize all workflows"""
        try:
            # Document Retrieval
            if self.config.get('workflows', {}).get('document_retrieval', {}).get('enabled', True):
                self.document_retrieval = AzureDocumentRetrievalWorkflow(self.config)
                self.logger.info("Document Retrieval workflow initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Document Retrieval: {e}")
        
        try:
            # Financial Summarization
            if self.config.get('workflows', {}).get('financial_summarization', {}).get('enabled', True):
                summarization_config = {
                    **self.config.get('workflows', {}).get('financial_summarization', {}),
                    'llm': self.config.get('llm', {})
                }
                self.financial_summarization = FinancialSummarizationWorkflow(summarization_config)
                self.logger.info("Financial Summarization workflow initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Financial Summarization: {e}")
        
        try:
            # Budget Insights
            if self.config.get('workflows', {}).get('budget_insights', {}).get('enabled', True):
                insights_config = self.config.get('workflows', {}).get('budget_insights', {})
                self.budget_insights = BudgetInsightsWorkflow(insights_config)
                self.logger.info("Budget Insights workflow initialized")
        except Exception as e:
            self.logger.error(f"Failed to initialize Budget Insights: {e}")
    
    def run_full_pipeline(
        self,
        query: Dict[str, Any],
        budget_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run the complete pipeline: Retrieval -> Summarization -> Insights
        
        Args:
            query: Document query parameters:
                - keywords: List of keywords
                - document_type: Type of documents
                - date_range: (start_date, end_date)
                - department: Optional department filter
                - sources: List of sources ['blob', 'sql', 'synapse', 'dataverse']
            
            budget_data: Budget information:
                - total_budget: Total budgeted amount
                - department_budgets: {department: amount}
                - category_budgets: {category: amount}
        
        Returns:
            Dictionary with all results:
                - documents: List of retrieved documents
                - summary: Financial summary
                - insights: Budget insights
                - metadata: Pipeline execution metadata
        """
        self.logger.info("=" * 80)
        self.logger.info("Starting Full Financial Pipeline")
        self.logger.info("=" * 80)
        
        start_time = datetime.now()
        results = {
            'metadata': {
                'pipeline_id': f"pipeline_{start_time.strftime('%Y%m%d%H%M%S')}",
                'start_time': start_time.isoformat(),
                'query': query,
                'budget_data': {k: v for k, v in budget_data.items() if k != 'department_budgets'}  # Summarize
            }
        }
        
        try:
            # Step 1: Document Retrieval
            self.logger.info("\n[Step 1/3] Document Retrieval")
            documents = self.run_document_retrieval(query)
            results['documents'] = [doc.to_dict() for doc in documents]
            results['documents_count'] = len(documents)
            self.logger.info(f"✓ Retrieved {len(documents)} documents")
            
            if not documents:
                self.logger.warning("No documents retrieved, pipeline stopping")
                return results
            
            # Step 2: Financial Summarization
            self.logger.info("\n[Step 2/3] Financial Summarization")
            summary = self.run_financial_summarization(documents)
            results['summary'] = summary.to_dict()
            self.logger.info(f"✓ Generated summary (confidence: {summary.confidence_score:.2f})")
            
            # Step 3: Budget Insights
            self.logger.info("\n[Step 3/3] Budget Insights Analysis")
            insights = self.run_budget_insights(summary, budget_data)
            results['insights'] = insights.to_dict()
            self.logger.info(f"✓ Generated insights (health score: {insights.budget_health_score:.1f}/100)")
            
            # Add execution metadata
            end_time = datetime.now()
            results['metadata']['end_time'] = end_time.isoformat()
            results['metadata']['duration_seconds'] = (end_time - start_time).total_seconds()
            results['metadata']['status'] = 'success'
            
            # Log critical issues
            critical_issues = insights.get_critical_issues()
            if critical_issues:
                self.logger.warning(f"\n⚠️  {len(critical_issues)} CRITICAL ISSUES DETECTED:")
                for issue in critical_issues:
                    self.logger.warning(f"  - {issue}")
            
            self.logger.info("\n" + "=" * 80)
            self.logger.info("Pipeline Completed Successfully")
            self.logger.info("=" * 80)
            
        except Exception as e:
            self.logger.error(f"Pipeline failed: {e}", exc_info=True)
            results['metadata']['status'] = 'failed'
            results['metadata']['error'] = str(e)
        
        return results
    
    def run_document_retrieval(self, query: Dict[str, Any]) -> List[FinancialDocument]:
        """
        Run only the document retrieval workflow
        
        Args:
            query: Document query parameters
        
        Returns:
            List of FinancialDocument objects
        """
        if not self.document_retrieval:
            raise RuntimeError("Document Retrieval workflow not initialized")
        
        return self.document_retrieval.execute(query)
    
    def run_financial_summarization(self, documents: List[FinancialDocument]) -> FinancialSummary:
        """
        Run only the financial summarization workflow
        
        Args:
            documents: List of documents to summarize
        
        Returns:
            FinancialSummary object
        """
        if not self.financial_summarization:
            raise RuntimeError("Financial Summarization workflow not initialized")
        
        return self.financial_summarization.execute(documents)
    
    def run_budget_insights(
        self,
        summary: FinancialSummary,
        budget_data: Dict[str, Any]
    ) -> BudgetInsight:
        """
        Run only the budget insights workflow
        
        Args:
            summary: Financial summary
            budget_data: Budget information
        
        Returns:
            BudgetInsight object
        """
        if not self.budget_insights:
            raise RuntimeError("Budget Insights workflow not initialized")
        
        return self.budget_insights.execute(summary, budget_data)
    
    def save_results(
        self,
        results: Dict[str, Any],
        output_path: Optional[str] = None
    ) -> str:
        """
        Save pipeline results to file
        
        Args:
            results: Pipeline results dictionary
            output_path: Optional custom output path
        
        Returns:
            Path to saved file
        """
        if output_path is None:
            output_dir = self.config.get('output', {}).get('save_path', './data/output')
            os.makedirs(output_dir, exist_ok=True)
            
            pipeline_id = results.get('metadata', {}).get('pipeline_id', 'unknown')
            output_path = os.path.join(output_dir, f"{pipeline_id}_results.json")
        
        with open(output_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        self.logger.info(f"Results saved to: {output_path}")
        return output_path
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get pipeline status
        
        Returns:
            Status dictionary
        """
        return {
            'workflows': {
                'document_retrieval': 'initialized' if self.document_retrieval else 'not initialized',
                'financial_summarization': 'initialized' if self.financial_summarization else 'not initialized',
                'budget_insights': 'initialized' if self.budget_insights else 'not initialized'
            },
            'config_loaded': bool(self.config)
        }
