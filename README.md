# Financial Data Processing Pipeline - Azure Edition

A comprehensive, production-ready financial data processing pipeline that integrates with Azure services (Azure Blob Storage, Azure SQL, Azure Synapse, and PowerApps Dataverse) to retrieve, analyze, and generate insights from financial data.

## 🎯 Overview

This pipeline implements three interconnected workflows:

1. **Document Retrieval Workflow** 📂
   - Retrieves financial documents from multiple Azure sources
   - Supports Azure Blob Storage, Azure SQL, Azure Synapse, and Dataverse
   - Preprocesses documents (noise removal, table extraction)
   - Extracts key financial figures

2. **Financial Summarization Workflow** 📊
   - Parses and aggregates financial data
   - Uses LLM (GPT-4) or rule-based methods for summarization
   - Generates executive summaries and key insights
   - Calculates financial metrics (revenue, expenses, margins, growth)

3. **Budget Insights Workflow** 💡
   - Compares actual vs. budgeted spending
   - Detects anomalies and budget variances
   - Calculates budget health scores
   - Generates actionable recommendations

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Data Sources (Azure)                      │
├─────────────┬──────────────┬─────────────┬──────────────────┤
│ Azure Blob  │  Azure SQL   │   Synapse   │   Dataverse      │
│  Storage    │   Database   │  Analytics  │   (PowerApps)    │
└──────┬──────┴──────┬───────┴──────┬──────┴────────┬─────────┘
       │             │              │               │
       └─────────────┴──────────────┴───────────────┘
                          │
                          ▼
         ┌────────────────────────────────────┐
         │   Document Retrieval Workflow      │
         │  • Query & retrieve documents      │
         │  • Preprocess & clean data         │
         │  • Extract key figures             │
         └────────────┬───────────────────────┘
                      │
                      ▼
         ┌────────────────────────────────────┐
         │  Financial Summarization Workflow  │
         │  • Parse numeric data              │
         │  • Generate LLM summaries          │
         │  • Calculate metrics               │
         └────────────┬───────────────────────┘
                      │
                      ▼
         ┌────────────────────────────────────┐
         │   Budget Insights Workflow         │
         │  • Compare budget vs actual        │
         │  • Detect anomalies                │
         │  • Generate recommendations        │
         └────────────────────────────────────┘
```

## 📋 Prerequisites

- Python 3.8+
- Azure subscription with:
  - Azure Blob Storage account
  - Azure SQL Database (optional)
  - Azure Synapse workspace (optional)
  - PowerApps Dataverse environment (optional)
- OpenAI API key (for LLM summarization)

## 🚀 Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd financial-data-pipeline
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your Azure credentials
```

4. **Update configuration**
```bash
# Edit config.yaml with your Azure resource names
```

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# OpenAI API
OPENAI_API_KEY=your_openai_key

# Azure Authentication
AZURE_TENANT_ID=your_tenant_id
AZURE_CLIENT_ID=your_client_id
AZURE_CLIENT_SECRET=your_client_secret

# Azure Blob Storage
AZURE_STORAGE_ACCOUNT_NAME=your_storage_account
AZURE_STORAGE_CONNECTION_STRING=your_connection_string

# Azure SQL Database
AZURE_SQL_SERVER=your_server.database.windows.net
AZURE_SQL_DATABASE=your_database
AZURE_SQL_CONNECTION_STRING=your_sql_connection_string

# Azure Synapse Analytics
AZURE_SYNAPSE_WORKSPACE=your_synapse_workspace
AZURE_SYNAPSE_SQL_POOL=your_sql_pool

# PowerApps Dataverse
DATAVERSE_ENVIRONMENT_URL=https://your_env.crm.dynamics.com
DATAVERSE_CLIENT_ID=your_app_id
DATAVERSE_CLIENT_SECRET=your_app_secret
```

### Configuration File (config.yaml)

See `config.yaml` for detailed configuration options including:
- Document storage settings
- LLM parameters
- Workflow configurations
- Azure service settings

## 💻 Usage

### Command Line Interface

**Run full pipeline:**
```bash
python main.py --example
```

**Run with custom parameters:**
```bash
python main.py \
  --keywords budget expense revenue \
  --department Engineering \
  --days-back 90 \
  --sources blob sql synapse dataverse
```

**Run specific workflow:**
```bash
# Document retrieval only
python main.py --workflow retrieval

# Summarization only
python main.py --workflow summarization

# Insights only
python main.py --workflow insights
```

### Python API

**Full pipeline:**
```python
from src.pipeline import FinancialPipeline
from datetime import datetime, timedelta

# Initialize pipeline
pipeline = FinancialPipeline(config_path='config.yaml')

# Define query
query = {
    'keywords': ['quarterly', 'budget'],
    'document_type': 'quarterly_report',
    'department': 'Engineering',
    'date_range': (datetime.now() - timedelta(days=90), datetime.now()),
    'sources': ['blob', 'sql', 'synapse', 'dataverse'],
    'limit': 50
}

# Define budget data
budget_data = {
    'total_budget': 5000000,
    'department_budgets': {
        'Engineering': 2000000,
        'Sales': 1500000,
        'Marketing': 1000000
    },
    'category_budgets': {
        'Salaries': 2500000,
        'Equipment': 1000000,
        'Marketing': 800000
    }
}

# Run pipeline
results = pipeline.run_full_pipeline(query, budget_data)

# Access results
print(f"Documents: {results['documents_count']}")
print(f"Health Score: {results['insights']['budget_health_score']}")
```

**Individual workflows:**
```python
# Run workflows separately
documents = pipeline.run_document_retrieval(query)
summary = pipeline.run_financial_summarization(documents)
insights = pipeline.run_budget_insights(summary, budget_data)
```

## 📁 Project Structure

```
financial-data-pipeline/
├── src/
│   ├── connectors/           # Azure service connectors
│   │   ├── azure_blob_connector.py
│   │   ├── azure_sql_connector.py
│   │   ├── azure_synapse_connector.py
│   │   └── dataverse_connector.py
│   ├── models/               # Data models
│   │   ├── financial_document.py
│   │   ├── summary.py
│   │   └── budget_insight.py
│   ├── workflows/            # Workflow implementations
│   │   ├── base.py
│   │   ├── document_retrieval.py
│   │   ├── document_retrieval_azure.py
│   │   ├── financial_summarization.py
│   │   └── budget_insights.py
│   ├── utils/                # Utility functions
│   └── pipeline.py           # Main pipeline orchestrator
├── data/
│   ├── documents/            # Sample documents
│   └── output/               # Pipeline output
├── examples/                 # Usage examples
│   ├── example_basic_usage.py
│   ├── example_individual_workflows.py
│   └── example_azure_connectors.py
├── config.yaml               # Configuration file
├── .env.example              # Environment template
├── requirements.txt          # Python dependencies
├── main.py                   # CLI entry point
└── README.md                 # This file
```

## 🔌 Azure Connectors

### Azure Blob Storage Connector

```python
from src.connectors import AzureBlobConnector

blob_connector = AzureBlobConnector(config)
blobs = blob_connector.list_blobs()
content = blob_connector.download_blob('financial_report.pdf')
```

### Azure SQL Connector

```python
from src.connectors import AzureSQLConnector

sql_connector = AzureSQLConnector(config)
df = sql_connector.get_financial_data(
    table_name='FinancialTransactions',
    start_date='2024-01-01',
    end_date='2024-03-31'
)
```

### Azure Synapse Connector

```python
from src.connectors import AzureSynapseConnector

synapse_connector = AzureSynapseConnector(config)
df = synapse_connector.get_aggregated_financial_data(
    start_date='2024-01-01',
    end_date='2024-03-31'
)
```

### Dataverse (PowerApps) Connector

```python
from src.connectors import DataverseConnector

dataverse_connector = DataverseConnector(config)
records = dataverse_connector.get_financial_records(
    start_date='2024-01-01',
    end_date='2024-03-31'
)
```

## 📊 Data Models

### FinancialDocument
- Document metadata and content
- Extracted tables and key figures
- Preprocessing status

### FinancialSummary
- Executive summary and insights
- Financial metrics (revenue, expenses, margins)
- Trends, risks, and opportunities

### BudgetInsight
- Budget health score
- Variances and anomalies
- Recommendations

## 🔍 Features

### Document Retrieval
- ✅ Multi-source data retrieval (Blob, SQL, Synapse, Dataverse)
- ✅ Smart keyword search
- ✅ Date range filtering
- ✅ Document preprocessing
- ✅ Table and figure extraction

### Financial Summarization
- ✅ LLM-powered summarization (GPT-4)
- ✅ Rule-based fallback
- ✅ Automated metric calculation
- ✅ Trend identification
- ✅ Risk and opportunity analysis

### Budget Insights
- ✅ Budget variance analysis
- ✅ Anomaly detection
- ✅ Health score calculation
- ✅ Department-level insights
- ✅ Actionable recommendations

## 🛡️ Security

- Uses Azure Managed Identity for authentication (recommended)
- Supports Service Principal authentication
- Environment variables for sensitive data
- Azure Key Vault integration ready

## 📝 Examples

See the `examples/` directory for:
- Basic usage example
- Individual workflow execution
- Direct connector usage
- Custom queries and filters

Run examples:
```bash
python examples/example_basic_usage.py
python examples/example_individual_workflows.py
python examples/example_azure_connectors.py
```

## 🧪 Testing

```bash
# Test Azure connections
python -c "from src.connectors import AzureBlobConnector; print('Import successful')"

# Run example with sample data
python main.py --example
```

## 📈 Output

Pipeline generates:
- JSON results file with complete analysis
- Executive summaries
- Financial metrics
- Budget insights and recommendations
- Anomaly reports

Output location: `data/output/`

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

This project is provided as-is for educational and commercial use.

## 🆘 Support

For issues and questions:
- Check the examples in `examples/`
- Review configuration in `config.yaml`
- Ensure Azure credentials are correct
- Check logs in `pipeline.log`

## 🔮 Future Enhancements

- [ ] PDF parsing with PyPDF2/pdfplumber
- [ ] Excel file analysis
- [ ] Power BI integration
- [ ] Email/Slack notifications
- [ ] Scheduled pipeline execution
- [ ] ML-based anomaly detection
- [ ] Multi-language support
- [ ] Advanced visualization

## 📚 Documentation

Additional documentation:
- Azure Blob Storage: https://docs.microsoft.com/azure/storage/blobs/
- Azure SQL Database: https://docs.microsoft.com/azure/azure-sql/
- Azure Synapse: https://docs.microsoft.com/azure/synapse-analytics/
- Dataverse: https://docs.microsoft.com/powerapps/developer/data-platform/

---

**Built with ❤️ for financial data analysis in Azure environments**
