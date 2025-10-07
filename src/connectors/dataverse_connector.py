"""PowerApps Dataverse Connector"""
import os
import logging
from typing import List, Dict, Any, Optional
import json

try:
    import requests
    from msal import ConfidentialClientApplication
    DATAVERSE_AVAILABLE = True
except ImportError:
    DATAVERSE_AVAILABLE = False


class DataverseConnector:
    """
    Connector for PowerApps Dataverse to retrieve financial data from PowerApps
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Dataverse connector
        
        Args:
            config: Configuration dictionary with Dataverse settings
        """
        if not DATAVERSE_AVAILABLE:
            raise ImportError(
                "Required packages not installed. Install with: pip install requests msal"
            )
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config
        
        self.environment_url = config.get('environment_url')
        self.client_id = config.get('client_id')
        self.client_secret = config.get('client_secret')
        self.tenant_id = config.get('tenant_id')
        
        # Dataverse API base URL
        self.api_url = f"{self.environment_url}/api/data/v9.2"
        
        # Initialize authentication
        self.access_token = None
        self._authenticate()
        
        self.logger.info(f"Dataverse connector initialized for environment: {self.environment_url}")
    
    def _authenticate(self):
        """Authenticate with Dataverse using MSAL"""
        try:
            # Create MSAL app
            authority = f"https://login.microsoftonline.com/{self.tenant_id}"
            app = ConfidentialClientApplication(
                client_id=self.client_id,
                client_credential=self.client_secret,
                authority=authority
            )
            
            # Get token for Dataverse
            scope = [f"{self.environment_url}/.default"]
            result = app.acquire_token_for_client(scopes=scope)
            
            if "access_token" in result:
                self.access_token = result["access_token"]
                self.logger.info("Successfully authenticated with Dataverse")
            else:
                error = result.get("error_description", "Unknown error")
                raise Exception(f"Authentication failed: {error}")
                
        except Exception as e:
            self.logger.error(f"Error authenticating with Dataverse: {e}")
            raise
    
    def _get_headers(self) -> Dict[str, str]:
        """Get HTTP headers for API requests"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "OData-MaxVersion": "4.0",
            "OData-Version": "4.0",
            "Accept": "application/json",
            "Content-Type": "application/json; charset=utf-8",
            "Prefer": "return=representation"
        }
    
    def _make_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Make HTTP request to Dataverse API
        
        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            endpoint: API endpoint
            data: Optional request body
            params: Optional query parameters
            
        Returns:
            Response JSON
        """
        url = f"{self.api_url}/{endpoint}"
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=self._get_headers(),
                json=data,
                params=params
            )
            
            response.raise_for_status()
            
            if response.status_code == 204:  # No content
                return {}
            
            return response.json()
            
        except requests.exceptions.HTTPError as e:
            self.logger.error(f"HTTP error: {e}")
            self.logger.error(f"Response: {e.response.text if e.response else 'No response'}")
            raise
        except Exception as e:
            self.logger.error(f"Error making request to Dataverse: {e}")
            raise
    
    def query_table(
        self,
        table_name: str,
        select: Optional[List[str]] = None,
        filter_query: Optional[str] = None,
        order_by: Optional[str] = None,
        top: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Query a Dataverse table
        
        Args:
            table_name: Name of the table (e.g., 'accounts', 'cr123_financialrecords')
            select: List of columns to select
            filter_query: OData filter query (e.g., "statecode eq 0")
            order_by: Column to order by
            top: Maximum number of records to return
            
        Returns:
            List of records
        """
        params = {}
        
        if select:
            params['$select'] = ','.join(select)
        
        if filter_query:
            params['$filter'] = filter_query
        
        if order_by:
            params['$orderby'] = order_by
        
        if top:
            params['$top'] = str(top)
        
        try:
            response = self._make_request('GET', table_name, params=params)
            records = response.get('value', [])
            
            self.logger.info(f"Retrieved {len(records)} records from {table_name}")
            return records
            
        except Exception as e:
            self.logger.error(f"Error querying table {table_name}: {e}")
            return []
    
    def get_financial_records(
        self,
        table_name: str = 'cr123_financialrecords',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        department: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get financial records from Dataverse
        
        Args:
            table_name: Name of the financial records table
            start_date: Optional start date (ISO format)
            end_date: Optional end date (ISO format)
            department: Optional department filter
            
        Returns:
            List of financial records
        """
        filter_parts = []
        
        if start_date:
            filter_parts.append(f"cr123_date ge {start_date}")
        
        if end_date:
            filter_parts.append(f"cr123_date le {end_date}")
        
        if department:
            filter_parts.append(f"cr123_department eq '{department}'")
        
        filter_query = " and ".join(filter_parts) if filter_parts else None
        
        return self.query_table(
            table_name=table_name,
            filter_query=filter_query,
            order_by='cr123_date desc'
        )
    
    def get_budget_submissions(
        self,
        table_name: str = 'cr123_budgetsubmissions',
        status: Optional[str] = 'Approved'
    ) -> List[Dict[str, Any]]:
        """
        Get budget submissions from PowerApps
        
        Args:
            table_name: Name of the budget submissions table
            status: Optional status filter
            
        Returns:
            List of budget submissions
        """
        filter_query = None
        if status:
            filter_query = f"cr123_status eq '{status}'"
        
        return self.query_table(
            table_name=table_name,
            filter_query=filter_query
        )
    
    def get_expense_requests(
        self,
        table_name: str = 'cr123_expenserequests',
        pending_only: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get expense requests from PowerApps
        
        Args:
            table_name: Name of the expense requests table
            pending_only: If True, only return pending requests
            
        Returns:
            List of expense requests
        """
        filter_query = "cr123_status eq 'Pending'" if pending_only else None
        
        return self.query_table(
            table_name=table_name,
            filter_query=filter_query,
            order_by='createdon desc'
        )
    
    def create_record(
        self,
        table_name: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create a new record in Dataverse
        
        Args:
            table_name: Name of the table
            data: Record data
            
        Returns:
            Created record
        """
        try:
            response = self._make_request('POST', table_name, data=data)
            self.logger.info(f"Created record in {table_name}")
            return response
            
        except Exception as e:
            self.logger.error(f"Error creating record in {table_name}: {e}")
            raise
    
    def update_record(
        self,
        table_name: str,
        record_id: str,
        data: Dict[str, Any]
    ) -> bool:
        """
        Update a record in Dataverse
        
        Args:
            table_name: Name of the table
            record_id: ID of the record to update
            data: Updated data
            
        Returns:
            True if successful
        """
        try:
            endpoint = f"{table_name}({record_id})"
            self._make_request('PATCH', endpoint, data=data)
            self.logger.info(f"Updated record {record_id} in {table_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error updating record: {e}")
            return False
    
    def submit_insight_to_powerapps(
        self,
        insight_data: Dict[str, Any],
        table_name: str = 'cr123_financialinsights'
    ) -> bool:
        """
        Submit generated financial insights back to PowerApps
        
        Args:
            insight_data: Insight data to submit
            table_name: Name of the insights table in Dataverse
            
        Returns:
            True if successful
        """
        try:
            # Format data for Dataverse
            formatted_data = {
                'cr123_name': insight_data.get('title', 'Financial Insight'),
                'cr123_description': insight_data.get('description', ''),
                'cr123_insights': json.dumps(insight_data.get('insights', [])),
                'cr123_recommendations': json.dumps(insight_data.get('recommendations', [])),
                'cr123_healthscore': insight_data.get('health_score', 0),
                'cr123_generatedon': insight_data.get('generated_at', ''),
            }
            
            self.create_record(table_name, formatted_data)
            self.logger.info("Successfully submitted insight to PowerApps")
            return True
            
        except Exception as e:
            self.logger.error(f"Error submitting insight to PowerApps: {e}")
            return False
    
    def test_connection(self) -> bool:
        """
        Test the Dataverse connection
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            # Try to query a system table
            self.query_table('systemusers', top=1)
            return True
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
