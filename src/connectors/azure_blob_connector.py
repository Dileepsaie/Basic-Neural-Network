"""Azure Blob Storage Connector"""
import os
import io
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

try:
    from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
    from azure.identity import DefaultAzureCredential, ClientSecretCredential
    from azure.core.exceptions import ResourceNotFoundError
    AZURE_AVAILABLE = True
except ImportError:
    AZURE_AVAILABLE = False


class AzureBlobConnector:
    """
    Connector for Azure Blob Storage to retrieve financial documents
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Azure Blob Storage connector
        
        Args:
            config: Configuration dictionary with Azure Blob settings
        """
        if not AZURE_AVAILABLE:
            raise ImportError(
                "Azure SDK not installed. Install with: pip install azure-storage-blob azure-identity"
            )
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config
        
        self.storage_account_name = config.get('storage_account_name')
        self.container_name = config.get('container_name', 'financial-documents')
        self.use_managed_identity = config.get('use_managed_identity', True)
        self.connection_string = config.get('connection_string')
        
        # Initialize blob service client
        self.blob_service_client = self._create_blob_service_client()
        self.container_client = self.blob_service_client.get_container_client(self.container_name)
        
        self.logger.info(f"Azure Blob connector initialized for container: {self.container_name}")
    
    def _create_blob_service_client(self) -> BlobServiceClient:
        """Create and return BlobServiceClient with appropriate authentication"""
        
        # Option 1: Use connection string (simplest for development)
        if self.connection_string:
            self.logger.info("Using connection string for authentication")
            return BlobServiceClient.from_connection_string(self.connection_string)
        
        # Option 2: Use Managed Identity (recommended for production in Azure)
        elif self.use_managed_identity:
            self.logger.info("Using Managed Identity for authentication")
            credential = DefaultAzureCredential()
            account_url = f"https://{self.storage_account_name}.blob.core.windows.net"
            return BlobServiceClient(account_url=account_url, credential=credential)
        
        # Option 3: Use Service Principal
        elif os.getenv('AZURE_CLIENT_ID') and os.getenv('AZURE_CLIENT_SECRET'):
            self.logger.info("Using Service Principal for authentication")
            credential = ClientSecretCredential(
                tenant_id=os.getenv('AZURE_TENANT_ID'),
                client_id=os.getenv('AZURE_CLIENT_ID'),
                client_secret=os.getenv('AZURE_CLIENT_SECRET')
            )
            account_url = f"https://{self.storage_account_name}.blob.core.windows.net"
            return BlobServiceClient(account_url=account_url, credential=credential)
        
        else:
            raise ValueError(
                "No valid authentication method configured. Provide connection_string, "
                "enable managed_identity, or set AZURE_CLIENT_ID/AZURE_CLIENT_SECRET"
            )
    
    def list_blobs(
        self, 
        prefix: Optional[str] = None,
        name_starts_with: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        List all blobs in the container
        
        Args:
            prefix: Optional prefix to filter blobs
            name_starts_with: Optional name filter
            
        Returns:
            List of blob metadata dictionaries
        """
        try:
            blobs = []
            blob_list = self.container_client.list_blobs(name_starts_with=name_starts_with)
            
            for blob in blob_list:
                if prefix and not blob.name.startswith(prefix):
                    continue
                
                blobs.append({
                    'name': blob.name,
                    'size': blob.size,
                    'last_modified': blob.last_modified,
                    'content_type': blob.content_settings.content_type if blob.content_settings else None,
                    'metadata': blob.metadata or {}
                })
            
            self.logger.info(f"Found {len(blobs)} blobs in container")
            return blobs
            
        except Exception as e:
            self.logger.error(f"Error listing blobs: {e}")
            return []
    
    def download_blob(self, blob_name: str) -> Optional[bytes]:
        """
        Download a blob's content
        
        Args:
            blob_name: Name of the blob to download
            
        Returns:
            Blob content as bytes, or None if error
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            download_stream = blob_client.download_blob()
            content = download_stream.readall()
            
            self.logger.info(f"Downloaded blob: {blob_name} ({len(content)} bytes)")
            return content
            
        except ResourceNotFoundError:
            self.logger.error(f"Blob not found: {blob_name}")
            return None
        except Exception as e:
            self.logger.error(f"Error downloading blob {blob_name}: {e}")
            return None
    
    def download_blob_to_text(self, blob_name: str, encoding: str = 'utf-8') -> Optional[str]:
        """
        Download blob and decode as text
        
        Args:
            blob_name: Name of the blob
            encoding: Text encoding (default: utf-8)
            
        Returns:
            Decoded text content or None
        """
        content = self.download_blob(blob_name)
        if content:
            try:
                return content.decode(encoding)
            except UnicodeDecodeError as e:
                self.logger.error(f"Error decoding blob {blob_name}: {e}")
                return None
        return None
    
    def upload_blob(
        self, 
        blob_name: str, 
        data: bytes, 
        metadata: Optional[Dict[str, str]] = None,
        overwrite: bool = True
    ) -> bool:
        """
        Upload data to a blob
        
        Args:
            blob_name: Name for the blob
            data: Data to upload
            metadata: Optional metadata dictionary
            overwrite: Whether to overwrite existing blob
            
        Returns:
            True if successful, False otherwise
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            blob_client.upload_blob(
                data,
                metadata=metadata,
                overwrite=overwrite
            )
            
            self.logger.info(f"Uploaded blob: {blob_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error uploading blob {blob_name}: {e}")
            return False
    
    def search_blobs(
        self, 
        keywords: List[str],
        document_type: Optional[str] = None,
        date_range: Optional[tuple] = None
    ) -> List[Dict[str, Any]]:
        """
        Search for blobs matching criteria
        
        Args:
            keywords: List of keywords to search for in blob names
            document_type: Optional document type filter
            date_range: Optional tuple of (start_date, end_date)
            
        Returns:
            List of matching blob metadata
        """
        all_blobs = self.list_blobs()
        matching_blobs = []
        
        for blob in all_blobs:
            blob_name_lower = blob['name'].lower()
            
            # Check keywords
            if keywords:
                keyword_match = any(kw.lower() in blob_name_lower for kw in keywords)
                if not keyword_match:
                    continue
            
            # Check document type
            if document_type:
                type_keywords = {
                    'quarterly_report': ['quarterly', 'q1', 'q2', 'q3', 'q4', 'quarter'],
                    'annual_report': ['annual', 'yearly', 'year'],
                    'budget': ['budget', 'forecast'],
                    'contract': ['contract', 'agreement'],
                    'invoice': ['invoice', 'bill'],
                    'expense_report': ['expense', 'spending']
                }
                
                if document_type in type_keywords:
                    if not any(kw in blob_name_lower for kw in type_keywords[document_type]):
                        continue
            
            # Check date range
            if date_range:
                start_date, end_date = date_range
                if blob['last_modified']:
                    # Make last_modified offset-naive if it's offset-aware
                    blob_date = blob['last_modified']
                    if blob_date.tzinfo is not None:
                        blob_date = blob_date.replace(tzinfo=None)
                    
                    if not (start_date <= blob_date <= end_date):
                        continue
            
            matching_blobs.append(blob)
        
        self.logger.info(f"Found {len(matching_blobs)} matching blobs")
        return matching_blobs
    
    def get_blob_metadata(self, blob_name: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for a specific blob
        
        Args:
            blob_name: Name of the blob
            
        Returns:
            Metadata dictionary or None
        """
        try:
            blob_client = self.blob_service_client.get_blob_client(
                container=self.container_name,
                blob=blob_name
            )
            
            properties = blob_client.get_blob_properties()
            
            return {
                'name': blob_name,
                'size': properties.size,
                'last_modified': properties.last_modified,
                'content_type': properties.content_settings.content_type,
                'metadata': properties.metadata or {},
                'etag': properties.etag
            }
            
        except Exception as e:
            self.logger.error(f"Error getting blob metadata for {blob_name}: {e}")
            return None
    
    def create_container_if_not_exists(self) -> bool:
        """
        Create the container if it doesn't exist
        
        Returns:
            True if created or already exists, False on error
        """
        try:
            self.container_client.create_container()
            self.logger.info(f"Created container: {self.container_name}")
            return True
        except Exception as e:
            if "ContainerAlreadyExists" in str(e):
                self.logger.info(f"Container already exists: {self.container_name}")
                return True
            else:
                self.logger.error(f"Error creating container: {e}")
                return False
