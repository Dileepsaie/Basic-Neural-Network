# Financial Data Processing Pipeline - Azure Edition
## Comprehensive Documentation

> A production-ready, enterprise-grade financial data processing pipeline that integrates with Microsoft Azure services to retrieve, analyze, and generate actionable insights from financial data across multiple sources.

---

## 📑 Table of Contents

1. [Overview](#-overview)
2. [Architecture](#-architecture)
3. [Key Features](#-key-features)
4. [Prerequisites](#-prerequisites)
5. [Installation](#-installation)
6. [Configuration](#-configuration)
7. [Usage Guide](#-usage-guide)
8. [Workflows Deep Dive](#-workflows-deep-dive)
9. [Azure Connectors](#-azure-connectors)
10. [Data Models](#-data-models)
11. [API Reference](#-api-reference)
12. [Examples](#-examples)
13. [Deployment](#-deployment)
14. [Troubleshooting](#-troubleshooting)
15. [Best Practices](#-best-practices)
16. [FAQ](#-faq)

---

## 🎯 Overview

### What is This Pipeline?

The Financial Data Processing Pipeline is a comprehensive solution that automates the collection, analysis, and reporting of financial data from multiple Azure sources. It uses AI-powered analysis (OpenAI GPT-4) to generate insights and detect anomalies in financial data.

### Why Use This Pipeline?

**Problems It Solves:**
- ❌ Manual financial report generation
- ❌ Scattered data across multiple systems
- ❌ Delayed budget variance detection
- ❌ Inconsistent financial analysis
- ❌ Time-consuming anomaly detection

**Solutions It Provides:**
- ✅ Automated data retrieval from 4 Azure sources
- ✅ AI-powered financial summarization
- ✅ Real-time budget variance analysis
- ✅ Intelligent anomaly detection
- ✅ Actionable recommendations

### Core Workflows

The pipeline consists of **three interconnected workflows** that can run independently or as a complete pipeline:

#### 1. 📂 Document Retrieval Workflow

**Purpose**: Retrieve and preprocess financial documents from multiple Azure sources

**What It Does**:
- Connects to Azure Blob Storage, Azure SQL, Azure Synapse, and PowerApps Dataverse
- Searches for documents based on keywords, dates, departments, and document types
- Downloads and preprocesses documents (removes noise, extracts tables)
- Identifies and extracts key financial figures (revenue, expenses, etc.)
- Converts various formats (PDF, Excel, CSV, TXT, JSON) into standardized format

**Use Cases**:
- Collecting quarterly financial reports
- Retrieving budget documents
- Gathering expense reports from multiple departments
- Extracting data from PowerApps financial submissions

**Input**: Query parameters (keywords, dates, filters)
**Output**: List of `FinancialDocument` objects with extracted data

#### 2. 📊 Financial Summarization Workflow

**Purpose**: Generate comprehensive financial summaries using AI and statistical analysis

**What It Does**:
- Parses and aggregates data from multiple documents
- Uses GPT-4 to generate executive summaries (with rule-based fallback)
- Calculates key financial metrics:
  - Revenue, Expenses, Net Income
  - Gross Margin, Operating Income
  - Revenue Growth, Expense Growth
- Identifies trends, risks, and opportunities
- Generates key insights and findings

**Use Cases**:
- Creating executive summaries for board meetings
- Generating monthly financial reports
- Identifying financial trends
- Comparing performance across periods

**Input**: List of `FinancialDocument` objects
**Output**: `FinancialSummary` object with metrics and insights

#### 3. 💡 Budget Insights Workflow

**Purpose**: Analyze budget performance and detect financial anomalies

**What It Does**:
- Compares actual spending vs budgeted amounts
- Calculates variances by department and category
- Detects anomalies:
  - Budget overruns
  - Unusual spending patterns
  - Unexpected losses
  - Budget underutilization
- Assigns severity levels (Critical, High, Medium, Low)
- Calculates budget health score (0-100)
- Generates actionable recommendations

**Use Cases**:
- Monthly budget reviews
- Quarterly variance analysis
- Early warning system for budget overruns
- Department performance evaluation

**Input**: `FinancialSummary` + Budget data
**Output**: `BudgetInsight` object with variances, anomalies, recommendations

---

## 🏗️ Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                         Azure Cloud Services                         │
├─────────────────┬──────────────────┬──────────────┬─────────────────┤
│                 │                  │              │                 │
│  Azure Blob     │   Azure SQL      │   Azure      │   PowerApps     │
│  Storage        │   Database       │   Synapse    │   Dataverse     │
│                 │                  │              │                 │
│  • Documents    │  • Transactions  │  • Data      │  • Forms        │
│  • Reports      │  • Revenue       │    Warehouse │  • Submissions  │
│  • Budgets      │  • Expenses      │  • Analytics │  • Records      │
└────────┬────────┴────────┬─────────┴──────┬───────┴────────┬────────┘
         │                 │                │                │
         └─────────────────┴────────────────┴────────────────┘
                                    │
                                    ▼
                    ┌──────────────────────────────┐
                    │   Azure Connectors Layer     │
                    │  • Authentication            │
                    │  • Data Retrieval            │
                    │  • Format Conversion         │
                    └──────────────┬───────────────┘
                                   │
                                   ▼
         ┌─────────────────────────────────────────────────┐
         │      Workflow 1: Document Retrieval             │
         │  ┌─────────────────────────────────────────┐   │
         │  │ 1. Query multiple Azure sources         │   │
         │  │ 2. Download documents                   │   │
         │  │ 3. Preprocess and clean                 │   │
         │  │ 4. Extract key figures                  │   │
         │  └─────────────────────────────────────────┘   │
         └──────────────────────┬──────────────────────────┘
                                │
                                ▼
         ┌─────────────────────────────────────────────────┐
         │   Workflow 2: Financial Summarization           │
         │  ┌─────────────────────────────────────────┐   │
         │  │ 1. Parse and aggregate data             │   │
         │  │ 2. Calculate financial metrics          │   │
         │  │ 3. Generate AI-powered summary          │   │
         │  │ 4. Identify trends and risks            │   │
         │  └─────────────────────────────────────────┘   │
         └──────────────────────┬──────────────────────────┘
                                │
                                ▼
         ┌─────────────────────────────────────────────────┐
         │      Workflow 3: Budget Insights                │
         │  ┌─────────────────────────────────────────┐   │
         │  │ 1. Compare budget vs actual             │   │
         │  │ 2. Calculate variances                  │   │
         │  │ 3. Detect anomalies                     │   │
         │  │ 4. Generate recommendations             │   │
         │  └─────────────────────────────────────────┘   │
         └──────────────────────┬──────────────────────────┘
                                │
                                ▼
                    ┌──────────────────────────┐
                    │      Output Layer        │
                    │  • JSON Results          │
                    │  • Executive Summaries   │
                    │  • Recommendations       │
                    │  • Visualizations        │
                    └──────────────────────────┘
```

### Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Cloud Platform** | Microsoft Azure | Infrastructure and services |
| **Storage** | Azure Blob Storage | Document storage |
| **Database** | Azure SQL Database | Structured financial data |
| **Data Warehouse** | Azure Synapse Analytics | Aggregated analytics |
| **App Platform** | PowerApps Dataverse | Business applications |
| **AI/ML** | OpenAI GPT-4 | Natural language generation |
| **Language** | Python 3.8+ | Application logic |
| **Data Processing** | Pandas, NumPy | Data manipulation |
| **Validation** | Pydantic | Data validation |
| **Authentication** | Azure Identity | Managed Identity/OAuth |

---

## 🔑 Key Features

### Data Integration Features

✅ **Multi-Source Retrieval**
   - Simultaneously query 4 Azure services
   - Unified data format
   - Automatic source detection

✅ **Smart Search**
   - Keyword-based document search
   - Date range filtering
   - Department-specific queries
   - Document type filtering

✅ **Format Support**
   - PDF documents
   - Excel spreadsheets (XLSX, XLS)
   - CSV files
   - Text files (TXT)
   - JSON data

### Analysis Features

✅ **AI-Powered Summarization**
   - GPT-4 integration for intelligent summaries
   - Context-aware analysis
   - Natural language generation
   - Rule-based fallback (no API key required)

✅ **Financial Metrics**
   - Revenue, expenses, profit analysis
   - Margin calculations (gross, operating, net)
   - Growth rate analysis (YoY, QoQ)
   - Custom metric support

✅ **Budget Analysis**
   - Variance analysis (budget vs actual)
   - Department-level tracking
   - Category-level breakdown
   - Trend analysis

✅ **Anomaly Detection**
   - Unusual spending patterns
   - Budget overruns
   - Unexpected losses
   - Budget underutilization
   - Severity classification (Critical → Low)

### Operational Features

✅ **Flexible Execution**
   - Run complete pipeline or individual workflows
   - Command-line interface (CLI)
   - Python API
   - Batch processing support

✅ **Security**
   - Azure Managed Identity support
   - Service Principal authentication
   - Connection string fallback
   - Environment variable encryption ready

✅ **Monitoring & Logging**
   - Detailed execution logs
   - Error tracking
   - Performance metrics
   - Status reporting

✅ **Output Options**
   - JSON format (default)
   - CSV export
   - Automated report generation
   - Azure Blob output storage

---

## 📋 Prerequisites

### Required

1. **Python Environment**
   - Python 3.8 or higher
   - pip package manager
   - Virtual environment (recommended)

2. **Azure Subscription**
   - Active Azure subscription
   - Resource group created
   - Appropriate permissions to create resources

3. **Azure Services** (at least one required)
   - Azure Blob Storage account (recommended)
   - Azure SQL Database (optional)
   - Azure Synapse workspace (optional)
   - PowerApps environment with Dataverse (optional)

### Optional

1. **OpenAI API**
   - OpenAI API key (for AI-powered summarization)
   - Alternative: Pipeline works with rule-based summarization

2. **Development Tools**
   - Git (for version control)
   - Azure CLI (for deployment)
   - Code editor (VS Code recommended)

### Azure Resource Requirements

| Resource | SKU/Size | Purpose | Monthly Cost (Est.) |
|----------|----------|---------|---------------------|
| **Storage Account** | Standard LRS | Document storage | ~$20-50 |
| **SQL Database** | S0 (Standard) | Transactional data | ~$15-30 |
| **Synapse Workspace** | DW100c | Data warehouse | ~$1-5/hr paused |
| **VM (Optional)** | Standard D2s v3 | Pipeline execution | ~$70-100 |

---

## 🚀 Installation

### Step 1: Clone Repository

```bash
# Clone the repository
git clone https://github.com/your-org/financial-data-pipeline.git
cd financial-data-pipeline

# Verify structure
ls -la
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### Step 3: Install Dependencies

```bash
# Install all requirements
pip install -r requirements.txt

# Verify installation
python test_installation.py
```

### Step 4: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your credentials
nano .env  # or use your preferred editor
```

### Step 5: Update Configuration

```bash
# Edit configuration file
nano config.yaml

# Update Azure resource names and settings
```

### Step 6: Verify Installation

```bash
# Run installation test
python test_installation.py

# Run with example data
python main.py --example
```

---

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root:

```bash
# ============================================
# OpenAI API Configuration (Optional)
# ============================================
OPENAI_API_KEY=sk-your-openai-api-key-here

# ============================================
# Azure Authentication
# ============================================
AZURE_TENANT_ID=your-tenant-id-from-azure-ad
AZURE_CLIENT_ID=your-application-client-id
AZURE_CLIENT_SECRET=your-client-secret-value

# ============================================
# Azure Blob Storage
# ============================================
AZURE_STORAGE_ACCOUNT_NAME=yourstorageaccountname
AZURE_STORAGE_CONNECTION_STRING=DefaultEndpointsProtocol=https;AccountName=...;AccountKey=...

# ============================================
# Azure SQL Database (Optional)
# ============================================
AZURE_SQL_SERVER=your-server-name.database.windows.net
AZURE_SQL_DATABASE=your-database-name
AZURE_SQL_USERNAME=sqladmin
AZURE_SQL_PASSWORD=YourStrongPassword123!
AZURE_SQL_CONNECTION_STRING=Driver={ODBC Driver 18 for SQL Server};Server=tcp:your-server.database.windows.net...

# ============================================
# Azure Synapse Analytics (Optional)
# ============================================
AZURE_SYNAPSE_WORKSPACE=your-synapse-workspace-name
AZURE_SYNAPSE_SQL_POOL=your-dedicated-sql-pool-name
AZURE_SYNAPSE_CONNECTION_STRING=Driver={ODBC Driver 18 for SQL Server};Server=tcp:your-synapse...

# ============================================
# PowerApps Dataverse (Optional)
# ============================================
DATAVERSE_ENVIRONMENT_URL=https://yourenv.crm.dynamics.com
DATAVERSE_CLIENT_ID=your-dataverse-app-registration-id
DATAVERSE_CLIENT_SECRET=your-dataverse-app-secret

# ============================================
# Azure Key Vault (Optional - For Secrets)
# ============================================
AZURE_KEY_VAULT_URL=https://your-keyvault-name.vault.azure.net/
```

### Configuration File (config.yaml)

```yaml
# Document Storage Configuration
document_storage:
  type: "azure_blob"
  path: "./data/documents"  # Fallback for local
  supported_formats: ["pdf", "xlsx", "csv", "txt", "json"]
  
  azure_blob:
    storage_account_name: "${AZURE_STORAGE_ACCOUNT_NAME}"
    container_name: "financial-documents"
    use_managed_identity: true
    connection_string: "${AZURE_STORAGE_CONNECTION_STRING}"

# LLM Configuration
llm:
  provider: "openai"
  model: "gpt-4"              # Options: gpt-4, gpt-3.5-turbo
  temperature: 0.3            # 0.0 = deterministic, 1.0 = creative
  max_tokens: 2000

# Workflow Configuration
workflows:
  document_retrieval:
    enabled: true
    max_documents: 100
    preprocessing:
      remove_noise: true
      extract_tables: true
  
  financial_summarization:
    enabled: true
    summary_length: "concise"  # Options: concise, detailed, comprehensive
    include_metrics: true
  
  budget_insights:
    enabled: true
    variance_threshold: 0.10   # 10% variance triggers alert
    anomaly_detection: true

# Azure SQL Configuration
azure_sql:
  enabled: true
  server: "${AZURE_SQL_SERVER}"
  database: "${AZURE_SQL_DATABASE}"
  use_managed_identity: true

# Azure Synapse Configuration
azure_synapse:
  enabled: true
  workspace_name: "${AZURE_SYNAPSE_WORKSPACE}"
  sql_pool: "${AZURE_SYNAPSE_SQL_POOL}"
  use_managed_identity: true

# PowerApps Dataverse Configuration
dataverse:
  enabled: true
  environment_url: "${DATAVERSE_ENVIRONMENT_URL}"
  client_id: "${DATAVERSE_CLIENT_ID}"
  client_secret: "${DATAVERSE_CLIENT_SECRET}"
  tenant_id: "${AZURE_TENANT_ID}"

# Output Configuration
output:
  format: "json"
  save_path: "./data/output"
  save_to_blob: true
  output_container: "financial-reports"
  include_visualizations: true
```

---

## 💻 Usage Guide

### Command Line Interface (CLI)

#### Basic Commands

```bash
# Run with example data (quickest way to test)
python main.py --example

# Run with default settings (queries last 90 days)
python main.py

# Get help and see all options
python main.py --help
```

#### Custom Query Examples

```bash
# Search for specific keywords
python main.py --keywords budget quarterly revenue

# Filter by department
python main.py --department Engineering

# Specify date range
python main.py --days-back 30

# Query specific data sources
python main.py --sources blob sql

# Combine multiple filters
python main.py \
  --keywords budget expense \
  --department Engineering \
  --days-back 90 \
  --sources blob sql synapse dataverse \
  --output ./my_results.json
```

#### Workflow-Specific Commands

```bash
# Run only document retrieval
python main.py --workflow retrieval --keywords financial

# Run only summarization (includes retrieval)
python main.py --workflow summarization

# Run only budget insights (includes retrieval and summarization)
python main.py --workflow insights
```

### Python API

#### Example 1: Basic Usage

```python
from src.pipeline import FinancialPipeline
from datetime import datetime, timedelta

# Initialize pipeline
pipeline = FinancialPipeline(config_path='config.yaml')

# Define query
query = {
    'keywords': ['budget', 'quarterly'],
    'department': 'Engineering',
    'date_range': (
        datetime(2024, 1, 1),
        datetime(2024, 3, 31)
    ),
    'sources': ['blob', 'sql'],
    'limit': 50
}

# Define budget data
budget_data = {
    'total_budget': 5000000,
    'department_budgets': {
        'Engineering': 2000000,
        'Sales': 1500000
    },
    'category_budgets': {
        'Salaries': 2500000,
        'Equipment': 1000000
    }
}

# Run pipeline
results = pipeline.run_full_pipeline(query, budget_data)

# Print results
print(f"Documents: {results['documents_count']}")
print(f"Health Score: {results['insights']['budget_health_score']}")
```

#### Example 2: Individual Workflows

```python
from src.pipeline import FinancialPipeline

pipeline = FinancialPipeline()

# Step 1: Retrieve documents
documents = pipeline.run_document_retrieval(query)
print(f"Retrieved {len(documents)} documents")

# Step 2: Generate summary
summary = pipeline.run_financial_summarization(documents)
print(f"Revenue: ${summary.metrics.revenue:,.2f}")

# Step 3: Analyze budget
insights = pipeline.run_budget_insights(summary, budget_data)
print(f"Health Score: {insights.budget_health_score}/100")
```

#### Example 3: Direct Connector Usage

```python
from src.connectors import AzureBlobConnector, DataverseConnector

# Azure Blob Storage
blob_config = {
    'storage_account_name': 'mystorageaccount',
    'container_name': 'financial-documents',
    'connection_string': 'your-connection-string'
}
blob_connector = AzureBlobConnector(blob_config)
blobs = blob_connector.search_blobs(keywords=['budget'])

# PowerApps Dataverse
dataverse_config = {
    'environment_url': 'https://yourenv.crm.dynamics.com',
    'client_id': 'your-client-id',
    'client_secret': 'your-secret',
    'tenant_id': 'your-tenant-id'
}
dataverse_connector = DataverseConnector(dataverse_config)
records = dataverse_connector.get_financial_records()
```

---

## 🔄 Workflows Deep Dive

### Workflow 1: Document Retrieval

**File**: `src/workflows/document_retrieval_azure.py`

**Process Flow**:
```
Query Parameters
    ↓
┌──────────────────┐
│ Parse Query      │
│ • Keywords       │
│ • Date Range     │
│ • Department     │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Query Sources    │ ←─ Azure Blob Storage
│                  │ ←─ Azure SQL Database
│                  │ ←─ Azure Synapse
│                  │ ←─ PowerApps Dataverse
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Download Data    │
│ • Parallel fetch │
│ • Format detect  │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Preprocess       │
│ • Remove noise   │
│ • Extract tables │
│ • Parse figures  │
└────────┬─────────┘
         ↓
    Documents
```

**Configuration Options**:
```yaml
workflows:
  document_retrieval:
    max_documents: 100           # Max documents to retrieve
    preprocessing:
      remove_noise: true         # Remove headers, footers
      extract_tables: true       # Extract tabular data
```

**Query Parameters**:
```python
query = {
    'keywords': ['budget', 'quarterly'],        # Search keywords
    'document_type': 'quarterly_report',        # Filter by type
    'department': 'Engineering',                 # Department filter
    'date_range': (start_date, end_date),       # Date range tuple
    'sources': ['blob', 'sql'],                  # Data sources
    'limit': 50                                  # Max results
}
```

### Workflow 2: Financial Summarization

**File**: `src/workflows/financial_summarization.py`

**Process Flow**:
```
Documents List
    ↓
┌──────────────────┐
│ Parse Documents  │
│ • Extract text   │
│ • Extract tables │
│ • Aggregate data │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Calculate        │
│ Metrics          │
│ • Revenue        │
│ • Expenses       │
│ • Margins        │
│ • Growth rates   │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Generate         │
│ Summary          │
│ • LLM (GPT-4)    │
│ • Rule-based     │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Identify         │
│ • Trends         │
│ • Risks          │
│ • Opportunities  │
└────────┬─────────┘
         ↓
 Financial Summary
```

**Metrics Calculated**:
- **Revenue**: Total income
- **Expenses**: Total spending
- **Net Income**: Revenue - Expenses
- **Gross Margin**: (Revenue - COGS) / Revenue * 100
- **Operating Income**: Operating revenues - Operating expenses
- **Revenue Growth**: Period-over-period revenue change %
- **Expense Growth**: Period-over-period expense change %

**LLM Configuration**:
```yaml
llm:
  provider: "openai"
  model: "gpt-4"              # More accurate, higher cost
  # model: "gpt-3.5-turbo"    # Faster, lower cost
  temperature: 0.3            # Lower = more focused
  max_tokens: 2000            # Max summary length
```

### Workflow 3: Budget Insights

**File**: `src/workflows/budget_insights.py`

**Process Flow**:
```
Summary + Budget Data
    ↓
┌──────────────────┐
│ Calculate        │
│ Variances        │
│ • By Department  │
│ • By Category    │
│ • Overall        │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Detect Anomalies │
│ • Overspend      │
│ • Underspend     │
│ • Unusual        │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Calculate        │
│ Health Score     │
│ (0-100 scale)    │
└────────┬─────────┘
         ↓
┌──────────────────┐
│ Generate         │
│ Recommendations  │
│ • Actions        │
│ • Priorities     │
└────────┬─────────┘
         ↓
  Budget Insights
```

**Variance Types**:
- **Overspend**: Actual > Budget (positive variance)
- **Underspend**: Actual < Budget (negative variance)
- **On Target**: Within threshold (±10% default)

**Severity Levels**:
- **Critical**: Variance ≥ 20%
- **High**: Variance ≥ 15%
- **Medium**: Variance ≥ 10%
- **Low**: Variance < 10%

**Health Score Calculation**:
```
Start Score: 100
- Critical Variance: -15 points each
- High Variance: -10 points each
- Medium Variance: -5 points each
- Low Variance: -2 points each
- Critical Anomaly: -10 points each
- High Anomaly: -7 points each
Final Score: 0-100 (capped)
```

---

## 🔌 Azure Connectors

### Azure Blob Storage Connector

**File**: `src/connectors/azure_blob_connector.py`

**Authentication Methods**:
1. **Managed Identity** (Recommended for production)
2. **Connection String** (Easiest for development)
3. **Service Principal** (For automation)

**Key Methods**:

```python
from src.connectors import AzureBlobConnector

connector = AzureBlobConnector(config)

# List all blobs
blobs = connector.list_blobs()

# Search for specific blobs
results = connector.search_blobs(
    keywords=['budget', 'quarterly'],
    document_type='quarterly_report',
    date_range=(start_date, end_date)
)

# Download blob
content = connector.download_blob('path/to/file.pdf')
text = connector.download_blob_to_text('path/to/file.txt')

# Upload blob
success = connector.upload_blob(
    blob_name='reports/q1_2024.json',
    data=json_data.encode(),
    metadata={'department': 'Engineering'}
)

# Get metadata
metadata = connector.get_blob_metadata('reports/q1_2024.json')
```

### Azure SQL Connector

**File**: `src/connectors/azure_sql_connector.py`

**Key Methods**:

```python
from src.connectors import AzureSQLConnector

connector = AzureSQLConnector(config)

# Execute custom query
df = connector.execute_query(
    query="SELECT * FROM FinancialTransactions WHERE Department = :dept",
    params={'dept': 'Engineering'}
)

# Get financial data with filters
df = connector.get_financial_data(
    table_name='FinancialTransactions',
    date_column='transaction_date',
    start_date='2024-01-01',
    end_date='2024-03-31',
    filters={'Department': 'Engineering'}
)

# Get budget data
budget_df = connector.get_budget_data(
    budget_table='Budgets',
    fiscal_year=2024,
    department='Engineering'
)

# Get expense summary with grouping
summary_df = connector.get_expense_summary(
    expense_table='Expenses',
    start_date='2024-01-01',
    end_date='2024-03-31',
    group_by=['department', 'category']
)
```

### Azure Synapse Connector

**File**: `src/connectors/azure_synapse_connector.py`

**Key Methods**:

```python
from src.connectors import AzureSynapseConnector

connector = AzureSynapseConnector(config)

# Get aggregated financial data
df = connector.get_aggregated_financial_data(
    fact_table='FactFinancials',
    dimensions=['Department', 'FiscalYear', 'FiscalQuarter'],
    metrics=['Revenue', 'Expenses', 'NetIncome'],
    start_date='2024-01-01',
    end_date='2024-12-31'
)

# Budget vs Actual comparison
comparison_df = connector.get_budget_vs_actual(
    budget_table='DimBudget',
    actual_table='FactFinancials',
    fiscal_year=2024
)

# Time series analysis
timeseries_df = connector.get_time_series_data(
    table_name='FactFinancials',
    metric_column='Revenue',
    date_column='Date',
    group_by='Department',
    start_date='2024-01-01',
    end_date='2024-12-31'
)

# Department performance
perf_df = connector.get_department_performance(
    fact_table='FactFinancials',
    fiscal_year=2024
)
```

### PowerApps Dataverse Connector

**File**: `src/connectors/dataverse_connector.py`

**Key Methods**:

```python
from src.connectors import DataverseConnector

connector = DataverseConnector(config)

# Query any table
records = connector.query_table(
    table_name='cr123_financialrecords',
    select=['cr123_amount', 'cr123_date', 'cr123_department'],
    filter_query="cr123_status eq 'Approved'",
    order_by='cr123_date desc',
    top=100
)

# Get financial records
records = connector.get_financial_records(
    table_name='cr123_financialrecords',
    start_date='2024-01-01',
    end_date='2024-03-31',
    department='Engineering'
)

# Get budget submissions
budgets = connector.get_budget_submissions(
    table_name='cr123_budgetsubmissions',
    status='Approved'
)

# Get expense requests
expenses = connector.get_expense_requests(
    table_name='cr123_expenserequests',
    pending_only=True
)

# Submit insights back to PowerApps
success = connector.submit_insight_to_powerapps(
    insight_data={
        'title': 'Q1 2024 Budget Analysis',
        'description': 'Quarterly budget review insights',
        'insights': ['Revenue up 15%', 'Expenses under control'],
        'recommendations': ['Continue current strategy'],
        'health_score': 85.5,
        'generated_at': datetime.now().isoformat()
    },
    table_name='cr123_financialinsights'
)
```

---

## 📊 Data Models

### FinancialDocument

**File**: `src/models/financial_document.py`

```python
from src.models import FinancialDocument, DocumentType

document = FinancialDocument(
    document_id="doc_12345",
    document_type=DocumentType.QUARTERLY_REPORT,
    title="Q1 2024 Engineering Report",
    content="Full text content...",
    metadata={
        'source': 'azure_blob',
        'filename': 'q1_2024_engineering.pdf'
    },
    period_start=datetime(2024, 1, 1),
    period_end=datetime(2024, 3, 31),
    department="Engineering",
    tables=[{
        'rows': ['Revenue,2500000', 'Expenses,1800000'],
        'num_rows': 2
    }],
    key_figures={
        'revenue': 2500000.0,
        'expenses': 1800000.0,
        'net_income': 700000.0
    },
    retrieved_at=datetime.now(),
    preprocessed=True
)
```

**Fields**:
- `document_id`: Unique identifier
- `document_type`: Enum (QUARTERLY_REPORT, ANNUAL_REPORT, BUDGET, etc.)
- `title`: Document title
- `content`: Full text content
- `metadata`: Additional metadata dictionary
- `period_start/end`: Financial period dates
- `department`: Department name
- `tables`: Extracted tables list
- `key_figures`: Dictionary of extracted financial figures
- `retrieved_at`: Retrieval timestamp
- `preprocessed`: Whether document has been preprocessed

### FinancialSummary

**File**: `src/models/summary.py`

```python
from src.models import FinancialSummary, FinancialMetrics

summary = FinancialSummary(
    summary_id="summary_12345",
    source_document_ids=["doc_001", "doc_002"],
    executive_summary="The organization shows strong performance...",
    key_insights=[
        "Revenue increased by 15% year-over-year",
        "Expenses remain under control at 72% of revenue"
    ],
    metrics=FinancialMetrics(
        revenue=2500000.0,
        expenses=1800000.0,
        net_income=700000.0,
        gross_margin=28.0,
        revenue_growth=15.0,
        expense_growth=5.0
    ),
    period_start=datetime(2024, 1, 1),
    period_end=datetime(2024, 3, 31),
    trends=["Upward revenue trend"],
    risks=["Potential supply chain issues"],
    opportunities=["Market expansion opportunity"],
    generated_at=datetime.now(),
    confidence_score=0.85
)
```

**Metrics Sub-Model**:
```python
class FinancialMetrics:
    revenue: float                    # Total revenue
    expenses: float                   # Total expenses
    net_income: float                 # Net income/profit
    gross_margin: float               # Gross margin %
    operating_income: float           # Operating income
    revenue_growth: float             # Revenue growth %
    expense_growth: float             # Expense growth %
    custom_metrics: Dict[str, float]  # Additional metrics
```

### BudgetInsight

**File**: `src/models/budget_insight.py`

```python
from src.models import BudgetInsight, BudgetVariance, Anomaly, VarianceType, SeverityLevel

insight = BudgetInsight(
    insight_id="insight_12345",
    summary_id="summary_12345",
    budget_health_score=75.0,
    health_status="Good - Budget generally on track",
    variances=[
        BudgetVariance(
            category="Engineering",
            budgeted_amount=2000000.0,
            actual_amount=2300000.0,
            variance_amount=300000.0,
            variance_percentage=15.0,
            variance_type=VarianceType.OVERSPEND,
            severity=SeverityLevel.HIGH
        )
    ],
    total_budget=5000000.0,
    total_actual=4800000.0,
    total_variance=-200000.0,
    total_variance_percentage=-4.0,
    anomalies=[
        Anomaly(
            anomaly_type="Budget Overrun",
            description="Engineering exceeded budget by 15%",
            affected_category="Engineering",
            severity=SeverityLevel.HIGH,
            detected_value=2300000.0,
            expected_range="Budgeted: $2,000,000",
            recommendation="Review spending controls"
        )
    ],
    key_findings=[
        "Overall spending is 4% under budget",
        "Engineering department exceeded budget by 15%"
    ],
    recommendations=[
        "Implement stricter controls for Engineering",
        "Reallocate unused budget from other departments"
    ],
    department_insights={
        'Engineering': {
            'budgeted': 2000000,
            'actual': 2300000,
            'variance': 300000,
            'status': 'overspend'
        }
    },
    generated_at=datetime.now()
)

# Get critical issues
critical = insight.get_critical_issues()
```

**Variance Types**:
- `OVERSPEND`: Actual > Budgeted
- `UNDERSPEND`: Actual < Budgeted
- `ON_TARGET`: Within threshold

**Severity Levels**:
- `CRITICAL`: Requires immediate action
- `HIGH`: Requires attention soon
- `MEDIUM`: Monitor closely
- `LOW`: Minor concern
- `INFO`: Informational only

---

## 📚 API Reference

### Pipeline Class

**File**: `src/pipeline.py`

```python
class FinancialPipeline:
    """Main pipeline orchestrator"""
    
    def __init__(self, config_path: Optional[str] = None):
        """Initialize pipeline with configuration"""
        
    def run_full_pipeline(
        self, 
        query: Dict[str, Any], 
        budget_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Run complete pipeline: Retrieval → Summarization → Insights"""
        
    def run_document_retrieval(
        self, 
        query: Dict[str, Any]
    ) -> List[FinancialDocument]:
        """Run only document retrieval workflow"""
        
    def run_financial_summarization(
        self, 
        documents: List[FinancialDocument]
    ) -> FinancialSummary:
        """Run only financial summarization workflow"""
        
    def run_budget_insights(
        self, 
        summary: FinancialSummary, 
        budget_data: Dict[str, Any]
    ) -> BudgetInsight:
        """Run only budget insights workflow"""
        
    def save_results(
        self, 
        results: Dict[str, Any], 
        output_path: Optional[str] = None
    ) -> str:
        """Save pipeline results to file"""
        
    def get_status(self) -> Dict[str, Any]:
        """Get pipeline status"""
```

---

## 📝 Examples

### Example 1: Basic Usage

**File**: `examples/example_basic_usage.py`

Run a complete pipeline with sample data:

```bash
python examples/example_basic_usage.py
```

### Example 2: Individual Workflows

**File**: `examples/example_individual_workflows.py`

Run each workflow separately:

```bash
python examples/example_individual_workflows.py
```

### Example 3: Direct Connector Usage

**File**: `examples/example_azure_connectors.py`

Use Azure connectors directly:

```bash
python examples/example_azure_connectors.py
```

---

## 🚀 Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for comprehensive deployment instructions including:
- Azure resource setup
- VM/Container deployment
- Managed Identity configuration
- Security hardening
- Monitoring and alerts

---

## 🐛 Troubleshooting

### Common Issues

#### 1. Authentication Errors

**Problem**: "No valid authentication method configured"

**Solution**:
```bash
# Check environment variables
cat .env | grep AZURE

# Test managed identity (if on Azure VM)
curl 'http://169.254.169.254/metadata/identity/oauth2/token?api-version=2018-02-01&resource=https://storage.azure.com/' -H Metadata:true

# Use connection string as fallback
export AZURE_STORAGE_CONNECTION_STRING="your-connection-string"
```

#### 2. Module Import Errors

**Problem**: "No module named 'pydantic'"

**Solution**:
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Verify installation
python test_installation.py
```

#### 3. OpenAI API Errors

**Problem**: "OpenAI API key not found"

**Solution**:
- Pipeline automatically falls back to rule-based summarization
- To use LLM: Set `OPENAI_API_KEY` in `.env`

#### 4. Azure Connection Timeouts

**Problem**: Connection timeouts to Azure services

**Solution**:
```bash
# Check firewall rules
az sql server firewall-rule list --server myserver --resource-group mygroup

# Add your IP
az sql server firewall-rule create --server myserver --resource-group mygroup --name AllowMyIP --start-ip-address YOUR_IP --end-ip-address YOUR_IP

# Check network connectivity
ping your-server.database.windows.net
```

---

## 💡 Best Practices

### 1. Security

✅ **Use Managed Identity in production**
✅ Store secrets in Azure Key Vault
✅ Enable encryption at rest
✅ Use private endpoints for sensitive data
✅ Implement least privilege access

### 2. Performance

✅ Limit document retrieval (`limit` parameter)
✅ Use date range filters
✅ Cache frequently accessed data
✅ Use Synapse for large-scale queries
✅ Optimize SQL queries

### 3. Cost Optimization

✅ Pause Synapse SQL pools when not in use
✅ Use appropriate storage tiers
✅ Monitor OpenAI API usage
✅ Set up budget alerts
✅ Use spot VMs for non-critical workloads

### 4. Monitoring

✅ Enable Application Insights
✅ Set up log aggregation
✅ Configure alerts for failures
✅ Monitor budget health scores
✅ Track pipeline execution times

---

## ❓ FAQ

**Q: Do I need all Azure services?**
A: No, you can start with just Azure Blob Storage and add others as needed.

**Q: Can it work without OpenAI API?**
A: Yes, it falls back to rule-based summarization automatically.

**Q: How much does it cost to run?**
A: Depends on usage. Minimal setup (Blob + VM): ~$100-150/month.

**Q: Can I deploy to other clouds?**
A: The architecture is Azure-specific, but connectors can be adapted.

**Q: Is it production-ready?**
A: Yes, includes error handling, logging, and security best practices.

**Q: How do I contribute?**
A: Fork the repository, make changes, and submit a pull request.

---

## 📞 Support & Community

- **Documentation**: This README and guides
- **Examples**: See `examples/` directory
- **Issues**: GitHub Issues
- **Logs**: Check `pipeline.log`

---

## 📄 License

This project is provided as-is for educational and commercial use.

---

## 🙏 Acknowledgments

Built with:
- Microsoft Azure
- OpenAI GPT-4
- Python ecosystem
- Open source libraries

---

**Built with ❤️ for financial data analysis in Azure environments**

---

*Last Updated: 2024*
*Version: 1.0*
