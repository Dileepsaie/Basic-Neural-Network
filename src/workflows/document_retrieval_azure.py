"""Azure-Enhanced Document Retrieval Workflow"""
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import re
import pandas as pd

from .base import BaseWorkflow
from ..models import FinancialDocument, DocumentType
from ..connectors import (
    AzureBlobConnector,
    AzureSQLConnector,
    AzureSynapseConnector,
    DataverseConnector
)


class AzureDocumentRetrievalWorkflow(BaseWorkflow):
    """
    Enhanced Document Retrieval Workflow with Azure integrations
    
    Data Sources:
    - Azure Blob Storage: Document files (PDF, Excel, CSV)
    - Azure SQL: Structured financial data
    - Azure Synapse: Aggregated financial data warehouse
    - Dataverse: PowerApps financial records
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        
        # Initialize connectors based on config
        self.blob_connector = None
        self.sql_connector = None
        self.synapse_connector = None
        self.dataverse_connector = None
        
        self._initialize_connectors(config)
        
        self.max_documents = config.get('max_documents', 100)
        self.preprocessing_enabled = config.get('preprocessing', {}).get('remove_noise', True)
        self.extract_tables = config.get('preprocessing', {}).get('extract_tables', True)
    
    def _initialize_connectors(self, config: Dict[str, Any]):
        """Initialize Azure connectors based on configuration"""
        try:
            # Azure Blob Storage
            blob_config = config.get('document_storage', {}).get('azure_blob', {})
            if blob_config:
                self.blob_connector = AzureBlobConnector(blob_config)
                self.logger.info("Azure Blob connector initialized")
        except Exception as e:
            self.logger.warning(f"Could not initialize Azure Blob connector: {e}")
        
        try:
            # Azure SQL
            sql_config = config.get('azure_sql', {})
            if sql_config.get('enabled', False):
                self.sql_connector = AzureSQLConnector(sql_config)
                self.logger.info("Azure SQL connector initialized")
        except Exception as e:
            self.logger.warning(f"Could not initialize Azure SQL connector: {e}")
        
        try:
            # Azure Synapse
            synapse_config = config.get('azure_synapse', {})
            if synapse_config.get('enabled', False):
                self.synapse_connector = AzureSynapseConnector(synapse_config)
                self.logger.info("Azure Synapse connector initialized")
        except Exception as e:
            self.logger.warning(f"Could not initialize Azure Synapse connector: {e}")
        
        try:
            # Dataverse
            dataverse_config = config.get('dataverse', {})
            if dataverse_config.get('enabled', False):
                self.dataverse_connector = DataverseConnector(dataverse_config)
                self.logger.info("Dataverse connector initialized")
        except Exception as e:
            self.logger.warning(f"Could not initialize Dataverse connector: {e}")
    
    def execute(self, query: Dict[str, Any]) -> List[FinancialDocument]:
        """
        Execute document retrieval from Azure sources
        
        Args:
            query: Dictionary containing:
                - document_type: Type of documents to retrieve
                - keywords: Keywords to search for
                - date_range: Optional (start_date, end_date)
                - department: Optional department filter
                - sources: List of sources to query ['blob', 'sql', 'synapse', 'dataverse']
                - limit: Maximum documents to return
        
        Returns:
            List of FinancialDocument objects
        """
        self.logger.info("Starting Azure document retrieval workflow")
        self.logger.info(f"Query parameters: {query}")
        
        sources = query.get('sources', ['blob', 'sql', 'synapse', 'dataverse'])
        documents = []
        
        # Retrieve from Azure Blob Storage
        if 'blob' in sources and self.blob_connector:
            blob_docs = self._retrieve_from_blob(query)
            documents.extend(blob_docs)
            self.logger.info(f"Retrieved {len(blob_docs)} documents from Azure Blob")
        
        # Retrieve from Azure SQL
        if 'sql' in sources and self.sql_connector:
            sql_docs = self._retrieve_from_sql(query)
            documents.extend(sql_docs)
            self.logger.info(f"Retrieved {len(sql_docs)} documents from Azure SQL")
        
        # Retrieve from Azure Synapse
        if 'synapse' in sources and self.synapse_connector:
            synapse_docs = self._retrieve_from_synapse(query)
            documents.extend(synapse_docs)
            self.logger.info(f"Retrieved {len(synapse_docs)} documents from Azure Synapse")
        
        # Retrieve from Dataverse
        if 'dataverse' in sources and self.dataverse_connector:
            dataverse_docs = self._retrieve_from_dataverse(query)
            documents.extend(dataverse_docs)
            self.logger.info(f"Retrieved {len(dataverse_docs)} documents from Dataverse")
        
        # Apply limit
        if query.get('limit'):
            documents = documents[:query['limit']]
        
        # Preprocess documents
        if self.preprocessing_enabled:
            documents = [self._preprocess_document(doc) for doc in documents]
        
        self.logger.info(f"Total documents retrieved and processed: {len(documents)}")
        return documents
    
    def _retrieve_from_blob(self, query: Dict[str, Any]) -> List[FinancialDocument]:
        """Retrieve documents from Azure Blob Storage"""
        documents = []
        
        # Search for matching blobs
        keywords = query.get('keywords', [])
        document_type = query.get('document_type')
        date_range = query.get('date_range')
        
        matching_blobs = self.blob_connector.search_blobs(
            keywords=keywords,
            document_type=document_type,
            date_range=date_range
        )
        
        # Download and convert to FinancialDocument
        for blob in matching_blobs:
            try:
                content = self.blob_connector.download_blob(blob['name'])
                if content:
                    doc = self._blob_to_document(blob, content, query)
                    if doc:
                        documents.append(doc)
            except Exception as e:
                self.logger.error(f"Error processing blob {blob['name']}: {e}")
        
        return documents
    
    def _blob_to_document(
        self, 
        blob_metadata: Dict[str, Any], 
        content: bytes, 
        query: Dict[str, Any]
    ) -> Optional[FinancialDocument]:
        """Convert blob to FinancialDocument"""
        try:
            # Decode content based on file type
            file_name = blob_metadata['name']
            file_ext = Path(file_name).suffix.lower()
            
            if file_ext in ['.txt', '.csv', '.json']:
                text_content = content.decode('utf-8')
            elif file_ext in ['.xlsx', '.xls']:
                # For Excel files, create a summary
                text_content = f"Excel file: {file_name}\nSize: {len(content)} bytes"
            elif file_ext == '.pdf':
                # For PDF files, create a summary (full parsing would use PyPDF2)
                text_content = f"PDF file: {file_name}\nSize: {len(content)} bytes"
            else:
                text_content = f"Binary file: {file_name}"
            
            # Create document
            doc_type = self._infer_document_type(file_name, query)
            
            return FinancialDocument(
                document_id=self._generate_document_id_from_name(file_name),
                document_type=doc_type,
                title=Path(file_name).stem,
                content=text_content,
                metadata={
                    'source': 'azure_blob',
                    'blob_name': file_name,
                    'size': blob_metadata['size'],
                    'last_modified': blob_metadata['last_modified'].isoformat() if blob_metadata.get('last_modified') else None,
                    **blob_metadata.get('metadata', {})
                },
                department=query.get('department'),
                retrieved_at=datetime.now(),
                preprocessed=False
            )
        except Exception as e:
            self.logger.error(f"Error converting blob to document: {e}")
            return None
    
    def _retrieve_from_sql(self, query: Dict[str, Any]) -> List[FinancialDocument]:
        """Retrieve financial data from Azure SQL"""
        documents = []
        
        try:
            date_range = query.get('date_range')
            start_date = date_range[0].isoformat() if date_range else None
            end_date = date_range[1].isoformat() if date_range else None
            
            # Get financial data
            df = self.sql_connector.get_financial_data(
                table_name='FinancialTransactions',
                start_date=start_date,
                end_date=end_date,
                filters={'Department': query.get('department')} if query.get('department') else None
            )
            
            if not df.empty:
                # Convert DataFrame to document
                doc = self._dataframe_to_document(df, 'Azure SQL Financial Data', 'azure_sql', query)
                if doc:
                    documents.append(doc)
        
        except Exception as e:
            self.logger.error(f"Error retrieving from Azure SQL: {e}")
        
        return documents
    
    def _retrieve_from_synapse(self, query: Dict[str, Any]) -> List[FinancialDocument]:
        """Retrieve aggregated financial data from Azure Synapse"""
        documents = []
        
        try:
            date_range = query.get('date_range')
            start_date = date_range[0].isoformat() if date_range else None
            end_date = date_range[1].isoformat() if date_range else None
            
            # Get aggregated data
            df = self.synapse_connector.get_aggregated_financial_data(
                start_date=start_date,
                end_date=end_date,
                filters={'Department': query.get('department')} if query.get('department') else None
            )
            
            if not df.empty:
                doc = self._dataframe_to_document(df, 'Azure Synapse Aggregated Data', 'azure_synapse', query)
                if doc:
                    documents.append(doc)
        
        except Exception as e:
            self.logger.error(f"Error retrieving from Azure Synapse: {e}")
        
        return documents
    
    def _retrieve_from_dataverse(self, query: Dict[str, Any]) -> List[FinancialDocument]:
        """Retrieve financial records from Dataverse (PowerApps)"""
        documents = []
        
        try:
            date_range = query.get('date_range')
            start_date = date_range[0].isoformat() if date_range else None
            end_date = date_range[1].isoformat() if date_range else None
            
            # Get financial records
            records = self.dataverse_connector.get_financial_records(
                start_date=start_date,
                end_date=end_date,
                department=query.get('department')
            )
            
            if records:
                # Convert records to DataFrame then to document
                df = pd.DataFrame(records)
                doc = self._dataframe_to_document(df, 'PowerApps Dataverse Records', 'dataverse', query)
                if doc:
                    documents.append(doc)
        
        except Exception as e:
            self.logger.error(f"Error retrieving from Dataverse: {e}")
        
        return documents
    
    def _dataframe_to_document(
        self,
        df: pd.DataFrame,
        title: str,
        source: str,
        query: Dict[str, Any]
    ) -> Optional[FinancialDocument]:
        """Convert DataFrame to FinancialDocument"""
        try:
            # Create text representation
            content = f"Data from {source}\n\n"
            content += f"Records: {len(df)}\n"
            content += f"Columns: {', '.join(df.columns)}\n\n"
            content += df.to_string(max_rows=50)
            
            # Extract key figures if available
            key_figures = {}
            for col in df.columns:
                col_lower = col.lower()
                if any(term in col_lower for term in ['revenue', 'income', 'sales']):
                    key_figures['revenue'] = float(df[col].sum())
                elif any(term in col_lower for term in ['expense', 'cost', 'spending']):
                    key_figures['expenses'] = float(df[col].sum())
                elif 'amount' in col_lower:
                    key_figures[col] = float(df[col].sum())
            
            # Create document
            return FinancialDocument(
                document_id=self._generate_document_id_from_name(f"{source}_{title}"),
                document_type=DocumentType.OTHER,
                title=title,
                content=content,
                metadata={
                    'source': source,
                    'record_count': len(df),
                    'columns': list(df.columns)
                },
                key_figures=key_figures,
                department=query.get('department'),
                retrieved_at=datetime.now(),
                preprocessed=False
            )
        
        except Exception as e:
            self.logger.error(f"Error converting DataFrame to document: {e}")
            return None
    
    def _preprocess_document(self, document: FinancialDocument) -> FinancialDocument:
        """Preprocess document: clean, extract tables, identify figures"""
        if document.preprocessed:
            return document
        
        # Clean content
        cleaned_content = self._remove_noise(document.content)
        document.content = cleaned_content
        
        # Extract key figures if not already done
        if not document.key_figures:
            document.key_figures = self._extract_key_figures(cleaned_content)
        
        document.preprocessed = True
        return document
    
    def _remove_noise(self, content: str) -> str:
        """Remove noise from content"""
        content = re.sub(r'\s+', ' ', content)
        content = re.sub(r'Page \d+ of \d+', '', content)
        return content.strip()
    
    def _extract_key_figures(self, content: str) -> Dict[str, float]:
        """Extract key financial figures"""
        key_figures = {}
        patterns = {
            'revenue': r'revenue[:\s]+\$?([\d,]+\.?\d*)',
            'expenses': r'(?:total\s+)?expenses?[:\s]+\$?([\d,]+\.?\d*)',
            'net_income': r'net\s+income[:\s]+\$?([\d,]+\.?\d*)',
        }
        
        for key, pattern in patterns.items():
            matches = re.findall(pattern, content.lower())
            if matches:
                try:
                    value = float(matches[0].replace(',', ''))
                    key_figures[key] = value
                except ValueError:
                    pass
        
        return key_figures
    
    def _infer_document_type(self, filename: str, query: Dict[str, Any]) -> DocumentType:
        """Infer document type"""
        if 'document_type' in query:
            try:
                return DocumentType(query['document_type'])
            except ValueError:
                pass
        
        filename_lower = filename.lower()
        if 'budget' in filename_lower:
            return DocumentType.BUDGET
        elif any(q in filename_lower for q in ['q1', 'q2', 'q3', 'q4', 'quarterly']):
            return DocumentType.QUARTERLY_REPORT
        elif 'annual' in filename_lower:
            return DocumentType.ANNUAL_REPORT
        
        return DocumentType.OTHER
    
    def _generate_document_id_from_name(self, name: str) -> str:
        """Generate document ID"""
        safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        return f"doc_{safe_name}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
