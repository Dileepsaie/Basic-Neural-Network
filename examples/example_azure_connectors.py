"""
Example: Using Azure Connectors Directly
"""
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.connectors import (
    AzureBlobConnector,
    AzureSQLConnector,
    AzureSynapseConnector,
    DataverseConnector
)

# Load environment variables
load_dotenv()


def example_blob_connector():
    """Example: Azure Blob Storage"""
    print("\n1. Azure Blob Storage Connector")
    print("-" * 80)
    
    try:
        config = {
            'storage_account_name': os.getenv('AZURE_STORAGE_ACCOUNT_NAME'),
            'container_name': 'financial-documents',
            'connection_string': os.getenv('AZURE_STORAGE_CONNECTION_STRING')
        }
        
        blob_connector = AzureBlobConnector(config)
        
        # List blobs
        blobs = blob_connector.list_blobs()
        print(f"✓ Found {len(blobs)} blobs in container")
        
        for i, blob in enumerate(blobs[:3], 1):
            print(f"   {i}. {blob['name']} ({blob['size']} bytes)")
        
        # Search for specific documents
        matching = blob_connector.search_blobs(keywords=['budget', 'quarterly'])
        print(f"✓ Found {len(matching)} matching blobs")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_sql_connector():
    """Example: Azure SQL Database"""
    print("\n2. Azure SQL Database Connector")
    print("-" * 80)
    
    try:
        config = {
            'server': os.getenv('AZURE_SQL_SERVER'),
            'database': os.getenv('AZURE_SQL_DATABASE'),
            'connection_string': os.getenv('AZURE_SQL_CONNECTION_STRING')
        }
        
        sql_connector = AzureSQLConnector(config)
        
        # Test connection
        if sql_connector.test_connection():
            print("✓ Successfully connected to Azure SQL")
        
        # Query financial data (example - table may not exist)
        # df = sql_connector.get_financial_data(
        #     table_name='FinancialTransactions',
        #     start_date='2024-01-01',
        #     end_date='2024-03-31'
        # )
        # print(f"✓ Retrieved {len(df)} financial records")
        
        print("✓ SQL connector initialized (queries commented out)")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_synapse_connector():
    """Example: Azure Synapse Analytics"""
    print("\n3. Azure Synapse Analytics Connector")
    print("-" * 80)
    
    try:
        config = {
            'workspace_name': os.getenv('AZURE_SYNAPSE_WORKSPACE'),
            'sql_pool': os.getenv('AZURE_SYNAPSE_SQL_POOL'),
            'connection_string': os.getenv('AZURE_SYNAPSE_CONNECTION_STRING')
        }
        
        synapse_connector = AzureSynapseConnector(config)
        
        # Test connection
        if synapse_connector.test_connection():
            print("✓ Successfully connected to Azure Synapse")
        
        # Query aggregated data (example - table may not exist)
        # df = synapse_connector.get_aggregated_financial_data(
        #     start_date='2024-01-01',
        #     end_date='2024-03-31'
        # )
        # print(f"✓ Retrieved aggregated data")
        
        print("✓ Synapse connector initialized (queries commented out)")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def example_dataverse_connector():
    """Example: PowerApps Dataverse"""
    print("\n4. PowerApps Dataverse Connector")
    print("-" * 80)
    
    try:
        config = {
            'environment_url': os.getenv('DATAVERSE_ENVIRONMENT_URL'),
            'client_id': os.getenv('DATAVERSE_CLIENT_ID'),
            'client_secret': os.getenv('DATAVERSE_CLIENT_SECRET'),
            'tenant_id': os.getenv('AZURE_TENANT_ID')
        }
        
        dataverse_connector = DataverseConnector(config)
        
        # Test connection
        if dataverse_connector.test_connection():
            print("✓ Successfully connected to Dataverse")
        
        # Query financial records (example - table may not exist)
        # records = dataverse_connector.get_financial_records(
        #     start_date='2024-01-01',
        #     end_date='2024-03-31'
        # )
        # print(f"✓ Retrieved {len(records)} financial records from PowerApps")
        
        print("✓ Dataverse connector initialized (queries commented out)")
        
    except Exception as e:
        print(f"✗ Error: {e}")


def main():
    """Run all connector examples"""
    print("=" * 80)
    print("Example: Azure Connectors")
    print("=" * 80)
    
    example_blob_connector()
    example_sql_connector()
    example_synapse_connector()
    example_dataverse_connector()
    
    print()
    print("=" * 80)
    print("Connector examples completed!")
    print("=" * 80)
    print()
    print("Note: Some queries are commented out as they require actual Azure resources")
    print("and database tables to exist. Uncomment them when your Azure environment")
    print("is fully configured.")


if __name__ == '__main__':
    main()
