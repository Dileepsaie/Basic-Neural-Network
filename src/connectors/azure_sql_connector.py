"""Azure SQL Database Connector"""
import os
import logging
from typing import List, Dict, Any, Optional
import pandas as pd

try:
    import pyodbc
    from sqlalchemy import create_engine, text
    from azure.identity import DefaultAzureCredential
    AZURE_SQL_AVAILABLE = True
except ImportError:
    AZURE_SQL_AVAILABLE = False


class AzureSQLConnector:
    """
    Connector for Azure SQL Database to retrieve financial data
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Azure SQL connector
        
        Args:
            config: Configuration dictionary with Azure SQL settings
        """
        if not AZURE_SQL_AVAILABLE:
            raise ImportError(
                "Required packages not installed. Install with: pip install pyodbc sqlalchemy"
            )
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config
        
        self.server = config.get('server')
        self.database = config.get('database')
        self.use_managed_identity = config.get('use_managed_identity', True)
        self.connection_string = config.get('connection_string')
        
        # Create connection
        self.engine = self._create_engine()
        self.logger.info(f"Azure SQL connector initialized for database: {self.database}")
    
    def _create_engine(self):
        """Create SQLAlchemy engine with appropriate authentication"""
        
        # Option 1: Use connection string
        if self.connection_string:
            self.logger.info("Using connection string for SQL authentication")
            # Convert ODBC connection string to SQLAlchemy format
            conn_str = self.connection_string.replace('Driver=', 'DRIVER=')
            return create_engine(f"mssql+pyodbc:///?odbc_connect={conn_str}")
        
        # Option 2: Use Managed Identity (Azure AD authentication)
        elif self.use_managed_identity:
            self.logger.info("Using Managed Identity for SQL authentication")
            connection_string = (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"Authentication=ActiveDirectoryMsi;"
                f"Encrypt=yes;"
                f"TrustServerCertificate=no;"
            )
            return create_engine(f"mssql+pyodbc:///?odbc_connect={connection_string}")
        
        # Option 3: SQL Server authentication with username/password
        elif os.getenv('AZURE_SQL_USERNAME') and os.getenv('AZURE_SQL_PASSWORD'):
            self.logger.info("Using SQL Server authentication")
            username = os.getenv('AZURE_SQL_USERNAME')
            password = os.getenv('AZURE_SQL_PASSWORD')
            connection_string = (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"UID={username};"
                f"PWD={password};"
                f"Encrypt=yes;"
                f"TrustServerCertificate=no;"
            )
            return create_engine(f"mssql+pyodbc:///?odbc_connect={connection_string}")
        
        else:
            raise ValueError(
                "No valid authentication method configured. Provide connection_string, "
                "enable managed_identity, or set AZURE_SQL_USERNAME/AZURE_SQL_PASSWORD"
            )
    
    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """
        Execute a SQL query and return results as DataFrame
        
        Args:
            query: SQL query string
            params: Optional query parameters
            
        Returns:
            Pandas DataFrame with query results
        """
        try:
            with self.engine.connect() as connection:
                result = pd.read_sql(text(query), connection, params=params)
            
            self.logger.info(f"Query executed successfully, returned {len(result)} rows")
            return result
            
        except Exception as e:
            self.logger.error(f"Error executing query: {e}")
            return pd.DataFrame()
    
    def get_financial_data(
        self,
        table_name: str,
        date_column: str = 'date',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> pd.DataFrame:
        """
        Retrieve financial data from a table
        
        Args:
            table_name: Name of the table to query
            date_column: Name of the date column for filtering
            start_date: Optional start date (YYYY-MM-DD)
            end_date: Optional end date (YYYY-MM-DD)
            filters: Optional additional filters {column: value}
            
        Returns:
            DataFrame with financial data
        """
        query = f"SELECT * FROM {table_name} WHERE 1=1"
        params = {}
        
        if start_date:
            query += f" AND {date_column} >= :start_date"
            params['start_date'] = start_date
        
        if end_date:
            query += f" AND {date_column} <= :end_date"
            params['end_date'] = end_date
        
        if filters:
            for column, value in filters.items():
                param_name = f"filter_{column}"
                query += f" AND {column} = :{param_name}"
                params[param_name] = value
        
        return self.execute_query(query, params)
    
    def get_budget_data(
        self,
        budget_table: str = 'budgets',
        fiscal_year: Optional[int] = None,
        department: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Retrieve budget data
        
        Args:
            budget_table: Name of the budget table
            fiscal_year: Optional fiscal year filter
            department: Optional department filter
            
        Returns:
            DataFrame with budget data
        """
        filters = {}
        if fiscal_year:
            filters['fiscal_year'] = fiscal_year
        if department:
            filters['department'] = department
        
        query = f"SELECT * FROM {budget_table}"
        
        if filters:
            where_clauses = [f"{k} = :{k}" for k in filters.keys()]
            query += " WHERE " + " AND ".join(where_clauses)
        
        return self.execute_query(query, filters if filters else None)
    
    def get_expense_summary(
        self,
        expense_table: str = 'expenses',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        group_by: Optional[List[str]] = None
    ) -> pd.DataFrame:
        """
        Get expense summary with grouping
        
        Args:
            expense_table: Name of the expense table
            start_date: Optional start date
            end_date: Optional end date
            group_by: Optional list of columns to group by (e.g., ['department', 'category'])
            
        Returns:
            DataFrame with expense summary
        """
        group_by = group_by or ['department']
        group_columns = ', '.join(group_by)
        
        query = f"""
        SELECT 
            {group_columns},
            SUM(amount) as total_amount,
            COUNT(*) as transaction_count,
            AVG(amount) as avg_amount,
            MIN(amount) as min_amount,
            MAX(amount) as max_amount
        FROM {expense_table}
        WHERE 1=1
        """
        
        params = {}
        if start_date:
            query += " AND date >= :start_date"
            params['start_date'] = start_date
        
        if end_date:
            query += " AND date <= :end_date"
            params['end_date'] = end_date
        
        query += f" GROUP BY {group_columns}"
        query += " ORDER BY total_amount DESC"
        
        return self.execute_query(query, params if params else None)
    
    def get_revenue_data(
        self,
        revenue_table: str = 'revenue',
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Retrieve revenue data
        
        Args:
            revenue_table: Name of the revenue table
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            DataFrame with revenue data
        """
        return self.get_financial_data(
            table_name=revenue_table,
            start_date=start_date,
            end_date=end_date
        )
    
    def test_connection(self) -> bool:
        """
        Test the database connection
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            result = self.execute_query("SELECT 1 as test")
            return len(result) > 0
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
