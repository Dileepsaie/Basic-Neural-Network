"""Azure Synapse Analytics Connector"""
import os
import logging
from typing import List, Dict, Any, Optional
import pandas as pd

try:
    import pyodbc
    from sqlalchemy import create_engine, text
    from azure.identity import DefaultAzureCredential
    SYNAPSE_AVAILABLE = True
except ImportError:
    SYNAPSE_AVAILABLE = False


class AzureSynapseConnector:
    """
    Connector for Azure Synapse Analytics to retrieve large-scale financial data
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Azure Synapse connector
        
        Args:
            config: Configuration dictionary with Synapse settings
        """
        if not SYNAPSE_AVAILABLE:
            raise ImportError(
                "Required packages not installed. Install with: pip install pyodbc sqlalchemy azure-identity"
            )
        
        self.logger = logging.getLogger(self.__class__.__name__)
        self.config = config
        
        self.workspace_name = config.get('workspace_name')
        self.sql_pool = config.get('sql_pool')
        self.use_managed_identity = config.get('use_managed_identity', True)
        self.connection_string = config.get('connection_string')
        
        # Construct server name for dedicated SQL pool
        self.server = f"{self.workspace_name}.sql.azuresynapse.net"
        self.database = self.sql_pool
        
        # Create connection
        self.engine = self._create_engine()
        self.logger.info(f"Azure Synapse connector initialized for workspace: {self.workspace_name}")
    
    def _create_engine(self):
        """Create SQLAlchemy engine for Synapse"""
        
        # Option 1: Use connection string
        if self.connection_string:
            self.logger.info("Using connection string for Synapse authentication")
            conn_str = self.connection_string.replace('Driver=', 'DRIVER=')
            return create_engine(f"mssql+pyodbc:///?odbc_connect={conn_str}")
        
        # Option 2: Use Managed Identity
        elif self.use_managed_identity:
            self.logger.info("Using Managed Identity for Synapse authentication")
            connection_string = (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"Authentication=ActiveDirectoryMsi;"
                f"Encrypt=yes;"
                f"TrustServerCertificate=no;"
            )
            return create_engine(f"mssql+pyodbc:///?odbc_connect={connection_string}")
        
        # Option 3: Service Principal authentication
        elif os.getenv('AZURE_CLIENT_ID') and os.getenv('AZURE_CLIENT_SECRET'):
            self.logger.info("Using Service Principal for Synapse authentication")
            connection_string = (
                f"DRIVER={{ODBC Driver 18 for SQL Server}};"
                f"SERVER={self.server};"
                f"DATABASE={self.database};"
                f"Authentication=ActiveDirectoryServicePrincipal;"
                f"UID={os.getenv('AZURE_CLIENT_ID')};"
                f"PWD={os.getenv('AZURE_CLIENT_SECRET')};"
                f"Encrypt=yes;"
                f"TrustServerCertificate=no;"
            )
            return create_engine(f"mssql+pyodbc:///?odbc_connect={connection_string}")
        
        else:
            raise ValueError(
                "No valid authentication method configured for Synapse"
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
            self.logger.error(f"Error executing Synapse query: {e}")
            return pd.DataFrame()
    
    def get_aggregated_financial_data(
        self,
        fact_table: str = 'FactFinancials',
        dimensions: Optional[List[str]] = None,
        metrics: Optional[List[str]] = None,
        filters: Optional[Dict[str, Any]] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Retrieve aggregated financial data from data warehouse
        
        Args:
            fact_table: Name of the fact table
            dimensions: List of dimension columns to group by
            metrics: List of metrics to aggregate
            filters: Optional filters {column: value}
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            DataFrame with aggregated data
        """
        dimensions = dimensions or ['Department', 'FiscalYear', 'FiscalQuarter']
        metrics = metrics or ['Revenue', 'Expenses', 'NetIncome']
        
        # Build SELECT clause
        dim_columns = ', '.join(dimensions)
        metric_aggregations = ', '.join([f"SUM({m}) as Total_{m}" for m in metrics])
        
        query = f"""
        SELECT 
            {dim_columns},
            {metric_aggregations},
            COUNT(*) as RecordCount
        FROM {fact_table}
        WHERE 1=1
        """
        
        params = {}
        
        # Add date filters
        if start_date:
            query += " AND Date >= :start_date"
            params['start_date'] = start_date
        
        if end_date:
            query += " AND Date <= :end_date"
            params['end_date'] = end_date
        
        # Add additional filters
        if filters:
            for column, value in filters.items():
                param_name = f"filter_{column}"
                query += f" AND {column} = :{param_name}"
                params[param_name] = value
        
        query += f" GROUP BY {dim_columns}"
        query += f" ORDER BY {dimensions[0]}"
        
        return self.execute_query(query, params if params else None)
    
    def get_budget_vs_actual(
        self,
        budget_table: str = 'DimBudget',
        actual_table: str = 'FactFinancials',
        fiscal_year: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Compare budget vs actual spending
        
        Args:
            budget_table: Name of the budget dimension table
            actual_table: Name of the actuals fact table
            fiscal_year: Optional fiscal year filter
            
        Returns:
            DataFrame with budget vs actual comparison
        """
        query = f"""
        SELECT 
            b.Department,
            b.Category,
            b.FiscalYear,
            b.BudgetedAmount,
            ISNULL(SUM(a.Amount), 0) as ActualAmount,
            ISNULL(SUM(a.Amount), 0) - b.BudgetedAmount as Variance,
            CASE 
                WHEN b.BudgetedAmount > 0 
                THEN ((ISNULL(SUM(a.Amount), 0) - b.BudgetedAmount) / b.BudgetedAmount * 100)
                ELSE 0 
            END as VariancePercentage
        FROM {budget_table} b
        LEFT JOIN {actual_table} a 
            ON b.Department = a.Department 
            AND b.Category = a.Category
            AND b.FiscalYear = a.FiscalYear
        """
        
        params = {}
        if fiscal_year:
            query += " WHERE b.FiscalYear = :fiscal_year"
            params['fiscal_year'] = fiscal_year
        
        query += """
        GROUP BY b.Department, b.Category, b.FiscalYear, b.BudgetedAmount
        ORDER BY ABS(ISNULL(SUM(a.Amount), 0) - b.BudgetedAmount) DESC
        """
        
        return self.execute_query(query, params if params else None)
    
    def get_time_series_data(
        self,
        table_name: str,
        metric_column: str,
        date_column: str = 'Date',
        group_by: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> pd.DataFrame:
        """
        Get time series financial data
        
        Args:
            table_name: Name of the table
            metric_column: Column to aggregate
            date_column: Date column for time series
            group_by: Optional grouping column (e.g., 'Department')
            start_date: Optional start date
            end_date: Optional end date
            
        Returns:
            DataFrame with time series data
        """
        if group_by:
            select_clause = f"{group_by}, {date_column}, SUM({metric_column}) as Total"
            group_clause = f"GROUP BY {group_by}, {date_column}"
            order_clause = f"ORDER BY {group_by}, {date_column}"
        else:
            select_clause = f"{date_column}, SUM({metric_column}) as Total"
            group_clause = f"GROUP BY {date_column}"
            order_clause = f"ORDER BY {date_column}"
        
        query = f"""
        SELECT {select_clause}
        FROM {table_name}
        WHERE 1=1
        """
        
        params = {}
        if start_date:
            query += f" AND {date_column} >= :start_date"
            params['start_date'] = start_date
        
        if end_date:
            query += f" AND {date_column} <= :end_date"
            params['end_date'] = end_date
        
        query += f" {group_clause} {order_clause}"
        
        return self.execute_query(query, params if params else None)
    
    def get_department_performance(
        self,
        fact_table: str = 'FactFinancials',
        fiscal_year: Optional[int] = None
    ) -> pd.DataFrame:
        """
        Get department-level performance metrics
        
        Args:
            fact_table: Name of the fact table
            fiscal_year: Optional fiscal year filter
            
        Returns:
            DataFrame with department performance
        """
        query = f"""
        SELECT 
            Department,
            SUM(Revenue) as TotalRevenue,
            SUM(Expenses) as TotalExpenses,
            SUM(Revenue) - SUM(Expenses) as NetIncome,
            CASE 
                WHEN SUM(Revenue) > 0 
                THEN ((SUM(Revenue) - SUM(Expenses)) / SUM(Revenue) * 100)
                ELSE 0 
            END as ProfitMargin,
            COUNT(DISTINCT TransactionID) as TransactionCount
        FROM {fact_table}
        """
        
        params = {}
        if fiscal_year:
            query += " WHERE FiscalYear = :fiscal_year"
            params['fiscal_year'] = fiscal_year
        
        query += """
        GROUP BY Department
        ORDER BY TotalRevenue DESC
        """
        
        return self.execute_query(query, params if params else None)
    
    def test_connection(self) -> bool:
        """
        Test the Synapse connection
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            result = self.execute_query("SELECT 1 as test")
            return len(result) > 0
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
