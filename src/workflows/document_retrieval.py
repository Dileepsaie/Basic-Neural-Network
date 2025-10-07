"""Document Retrieval Workflow"""
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
import re

from .base import BaseWorkflow
from ..models import FinancialDocument, DocumentType


class DocumentRetrievalWorkflow(BaseWorkflow):
    """
    Workflow for retrieving and preprocessing financial documents
    
    Steps:
    1. Query internal databases or document storage
    2. Retrieve relevant documents
    3. Preprocess/clean them (remove noise, extract tables)
    """
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.storage_path = config.get('storage_path', './data/documents')
        self.max_documents = config.get('max_documents', 100)
        self.supported_formats = config.get('supported_formats', ['txt', 'csv', 'json'])
        self.preprocessing_enabled = config.get('preprocessing', {}).get('remove_noise', True)
        self.extract_tables = config.get('preprocessing', {}).get('extract_tables', True)
    
    def execute(self, query: Dict[str, Any]) -> List[FinancialDocument]:
        """
        Execute document retrieval workflow
        
        Args:
            query: Dictionary containing search parameters:
                - document_type: Type of document to retrieve
                - keywords: List of keywords to search for
                - date_range: Optional date range (start, end)
                - department: Optional department filter
                - limit: Maximum number of documents to retrieve
        
        Returns:
            List of retrieved and preprocessed FinancialDocument objects
        """
        self.logger.info("Starting document retrieval workflow")
        self.logger.info(f"Query parameters: {query}")
        
        if not self.validate_input(query):
            raise ValueError("Invalid query parameters")
        
        # Step 1: Query document storage
        document_paths = self._query_storage(query)
        self.logger.info(f"Found {len(document_paths)} matching documents")
        
        # Step 2: Retrieve documents
        documents = []
        for path in document_paths[:query.get('limit', self.max_documents)]:
            try:
                doc = self._retrieve_document(path, query)
                if doc:
                    documents.append(doc)
            except Exception as e:
                self.logger.error(f"Error retrieving document {path}: {e}")
        
        self.logger.info(f"Successfully retrieved {len(documents)} documents")
        
        # Step 3: Preprocess documents
        if self.preprocessing_enabled:
            documents = [self._preprocess_document(doc) for doc in documents]
            self.logger.info(f"Preprocessed {len(documents)} documents")
        
        return documents
    
    def _query_storage(self, query: Dict[str, Any]) -> List[str]:
        """
        Query document storage to find matching documents
        
        Args:
            query: Search query parameters
            
        Returns:
            List of file paths to matching documents
        """
        storage_path = Path(self.storage_path)
        
        if not storage_path.exists():
            self.logger.warning(f"Storage path does not exist: {storage_path}")
            return []
        
        matching_files = []
        
        # Search for files matching query criteria
        for file_path in storage_path.rglob('*'):
            if file_path.is_file() and file_path.suffix[1:] in self.supported_formats:
                # Check if file matches query criteria
                if self._matches_query(file_path, query):
                    matching_files.append(str(file_path))
        
        return matching_files
    
    def _matches_query(self, file_path: Path, query: Dict[str, Any]) -> bool:
        """
        Check if a file matches the query criteria
        
        Args:
            file_path: Path to the file
            query: Query parameters
            
        Returns:
            True if file matches, False otherwise
        """
        file_name = file_path.name.lower()
        
        # Check keywords
        keywords = query.get('keywords', [])
        if keywords:
            keyword_match = any(keyword.lower() in file_name for keyword in keywords)
            if not keyword_match:
                return False
        
        # Check document type
        doc_type = query.get('document_type')
        if doc_type:
            type_keywords = {
                'quarterly_report': ['quarterly', 'q1', 'q2', 'q3', 'q4', 'quarter'],
                'annual_report': ['annual', 'yearly', 'year'],
                'budget': ['budget', 'forecast'],
                'contract': ['contract', 'agreement'],
                'invoice': ['invoice', 'bill'],
                'expense_report': ['expense', 'spending']
            }
            
            if doc_type in type_keywords:
                if not any(kw in file_name for kw in type_keywords[doc_type]):
                    return False
        
        return True
    
    def _retrieve_document(self, file_path: str, query: Dict[str, Any]) -> Optional[FinancialDocument]:
        """
        Retrieve and parse a document from storage
        
        Args:
            file_path: Path to the document file
            query: Original query for context
            
        Returns:
            FinancialDocument object or None if retrieval fails
        """
        path = Path(file_path)
        
        try:
            # Read file content based on format
            if path.suffix == '.txt':
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
            elif path.suffix == '.json':
                with open(path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    content = json.dumps(data, indent=2)
            elif path.suffix == '.csv':
                with open(path, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                content = f"Binary file: {path.name}"
            
            # Determine document type from filename or query
            doc_type = self._infer_document_type(path.name, query)
            
            # Extract metadata from filename or content
            metadata = self._extract_metadata(path.name, content)
            
            # Create FinancialDocument object
            document = FinancialDocument(
                document_id=self._generate_document_id(path),
                document_type=doc_type,
                title=path.stem,
                content=content,
                metadata=metadata,
                department=query.get('department'),
                retrieved_at=datetime.now(),
                preprocessed=False
            )
            
            return document
            
        except Exception as e:
            self.logger.error(f"Error reading file {file_path}: {e}")
            return None
    
    def _preprocess_document(self, document: FinancialDocument) -> FinancialDocument:
        """
        Preprocess document: clean text, extract tables, identify key figures
        
        Args:
            document: Document to preprocess
            
        Returns:
            Preprocessed document
        """
        # Remove noise from content
        cleaned_content = self._remove_noise(document.content)
        document.content = cleaned_content
        
        # Extract tables if enabled
        if self.extract_tables:
            tables = self._extract_tables(cleaned_content)
            document.tables = tables
        
        # Extract key financial figures
        key_figures = self._extract_key_figures(cleaned_content)
        document.key_figures = key_figures
        
        document.preprocessed = True
        
        return document
    
    def _remove_noise(self, content: str) -> str:
        """Remove noise and clean text content"""
        # Remove extra whitespace
        content = re.sub(r'\s+', ' ', content)
        
        # Remove common noise patterns
        content = re.sub(r'Page \d+ of \d+', '', content)
        content = re.sub(r'Confidential|CONFIDENTIAL', '', content)
        
        return content.strip()
    
    def _extract_tables(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract tables from document content
        
        This is a simplified implementation. In production, you'd use
        libraries like pdfplumber, tabula, or camelot for PDFs.
        """
        tables = []
        
        # Look for CSV-like content
        lines = content.split('\n')
        current_table = []
        
        for line in lines:
            # Check if line looks like a table row (has multiple comma/tab separated values)
            if ',' in line or '\t' in line:
                current_table.append(line)
            elif current_table and len(current_table) > 2:
                # End of table, save it
                tables.append({
                    'rows': current_table,
                    'num_rows': len(current_table)
                })
                current_table = []
        
        return tables
    
    def _extract_key_figures(self, content: str) -> Dict[str, float]:
        """
        Extract key financial figures from content
        
        Looks for common patterns like:
        - Revenue: $X
        - Total expenses: $X
        - Net income: $X
        """
        key_figures = {}
        
        # Common financial terms and patterns
        patterns = {
            'revenue': r'revenue[:\s]+\$?([\d,]+\.?\d*)',
            'expenses': r'(?:total\s+)?expenses?[:\s]+\$?([\d,]+\.?\d*)',
            'net_income': r'net\s+income[:\s]+\$?([\d,]+\.?\d*)',
            'gross_profit': r'gross\s+profit[:\s]+\$?([\d,]+\.?\d*)',
        }
        
        for key, pattern in patterns.items():
            matches = re.findall(pattern, content.lower())
            if matches:
                try:
                    # Take the first match and convert to float
                    value = float(matches[0].replace(',', ''))
                    key_figures[key] = value
                except ValueError:
                    pass
        
        return key_figures
    
    def _infer_document_type(self, filename: str, query: Dict[str, Any]) -> DocumentType:
        """Infer document type from filename or query"""
        filename_lower = filename.lower()
        
        # Check query first
        if 'document_type' in query:
            try:
                return DocumentType(query['document_type'])
            except ValueError:
                pass
        
        # Infer from filename
        if any(kw in filename_lower for kw in ['quarterly', 'q1', 'q2', 'q3', 'q4']):
            return DocumentType.QUARTERLY_REPORT
        elif any(kw in filename_lower for kw in ['annual', 'yearly']):
            return DocumentType.ANNUAL_REPORT
        elif 'budget' in filename_lower:
            return DocumentType.BUDGET
        elif 'contract' in filename_lower:
            return DocumentType.CONTRACT
        elif 'invoice' in filename_lower:
            return DocumentType.INVOICE
        elif 'expense' in filename_lower:
            return DocumentType.EXPENSE_REPORT
        
        return DocumentType.OTHER
    
    def _extract_metadata(self, filename: str, content: str) -> Dict[str, Any]:
        """Extract metadata from filename and content"""
        metadata = {
            'filename': filename,
            'file_size': len(content)
        }
        
        # Try to extract year from filename
        year_match = re.search(r'20\d{2}', filename)
        if year_match:
            metadata['year'] = int(year_match.group())
        
        # Try to extract quarter from filename
        quarter_match = re.search(r'q([1-4])', filename.lower())
        if quarter_match:
            metadata['quarter'] = int(quarter_match.group(1))
        
        return metadata
    
    def _generate_document_id(self, path: Path) -> str:
        """Generate unique document ID"""
        return f"doc_{path.stem}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    def validate_input(self, query: Dict[str, Any]) -> bool:
        """Validate query parameters"""
        if not isinstance(query, dict):
            return False
        
        # Optional validations
        if 'limit' in query and not isinstance(query['limit'], int):
            return False
        
        return True
