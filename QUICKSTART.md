# Quick Start Guide

Get started with the Financial Data Processing Pipeline in 5 minutes!

## 🚀 Quick Setup (Local Development)

### 1. Install Dependencies

```bash
# Install Python packages
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your credentials (minimum required for local testing)
nano .env
```

**Minimum configuration for local testing:**
```bash
# Only needed if using LLM summarization
OPENAI_API_KEY=sk-your-key-here

# For Azure Blob Storage (if testing with Azure)
AZURE_STORAGE_ACCOUNT_NAME=your_storage_account
AZURE_STORAGE_CONNECTION_STRING=your_connection_string
```

### 3. Run with Sample Data

```bash
# Run with built-in example
python main.py --example
```

This will:
- ✅ Load sample financial documents
- ✅ Generate financial summary
- ✅ Analyze budget variances
- ✅ Save results to `data/output/`

## 📊 Sample Output

```
================================================================================
Financial Data Processing Pipeline - Azure Edition
================================================================================

Loading configuration from: config.yaml
  ✓ Pipeline initialized

Pipeline Status:
  - document_retrieval: initialized
  - financial_summarization: initialized
  - budget_insights: initialized

Running FULL pipeline (Retrieval → Summarization → Insights)
--------------------------------------------------------------------------------
[Step 1/3] Document Retrieval
✓ Retrieved 2 documents

[Step 2/3] Financial Summarization
✓ Generated summary (confidence: 0.85)

[Step 3/3] Budget Insights Analysis
✓ Generated insights (health score: 75.0/100)

================================================================================
RESULTS SUMMARY
================================================================================

📄 Documents Retrieved: 2

📊 Financial Summary:
   Executive Summary: The organization demonstrates positive financial...
   Revenue: $2,500,000.00
   Expenses: $1,800,000.00
   Net Income: $700,000.00

💡 Budget Insights:
   Health Score: 75.0/100
   Status: Good - Budget is generally on track
   Total Budget: $5,000,000.00
   Total Actual: $1,800,000.00
   Variance: -$3,200,000.00 (-64.0%)

💾 Full results saved to: data/output/pipeline_20241007_results.json

================================================================================
Pipeline execution completed!
================================================================================
```

## 🔧 Testing Individual Components

### Test Document Retrieval Only

```bash
python main.py --workflow retrieval --keywords budget
```

### Test with Custom Parameters

```bash
python main.py \
  --keywords quarterly budget revenue \
  --department Engineering \
  --days-back 30
```

## 📝 Python API Usage

### Minimal Example

```python
from src.pipeline import FinancialPipeline
from datetime import datetime, timedelta

# Initialize
pipeline = FinancialPipeline()

# Simple query
query = {
    'keywords': ['budget'],
    'date_range': (datetime.now() - timedelta(days=30), datetime.now()),
    'sources': ['blob'],
    'limit': 10
}

# Budget data
budget_data = {
    'total_budget': 1000000,
    'department_budgets': {'Engineering': 500000},
    'category_budgets': {'Salaries': 600000}
}

# Run
results = pipeline.run_full_pipeline(query, budget_data)
print(f"Health Score: {results['insights']['budget_health_score']}")
```

## 🎯 Next Steps

### 1. Configure Azure Services (Optional)

If you want to use Azure services:

1. **Set up Azure Blob Storage**
   ```bash
   az storage account create --name mystorageaccount --resource-group mygroup
   ```

2. **Upload documents**
   ```bash
   az storage blob upload-batch \
     --account-name mystorageaccount \
     --destination financial-documents \
     --source ./data/documents
   ```

3. **Update .env with Azure credentials**

### 2. Customize Configuration

Edit `config.yaml` to:
- Change LLM model (GPT-3.5, GPT-4)
- Adjust variance thresholds
- Configure data sources
- Modify output format

### 3. Run Examples

```bash
# Basic usage
python examples/example_basic_usage.py

# Individual workflows
python examples/example_individual_workflows.py

# Azure connectors
python examples/example_azure_connectors.py
```

## 🔍 Verify Installation

Run verification script:

```bash
python -c "
from src.pipeline import FinancialPipeline
from src.connectors import AzureBlobConnector
print('✅ All imports successful!')
print('✅ Pipeline ready to use!')
"
```

## 📂 Sample Data Included

The repository includes sample data in `data/documents/`:
- `sample_q1_2024_report.txt` - Quarterly financial report
- `sample_budget_2024.txt` - Annual budget document

## 🐛 Troubleshooting

### Issue: Import Errors

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

### Issue: Azure Connection Errors

For local testing without Azure:
1. Use `--sources blob` but ensure local files exist in `data/documents/`
2. Or comment out Azure connector initialization
3. Use `--example` flag for testing

### Issue: OpenAI API Errors

If you don't have an OpenAI API key:
- Pipeline will fall back to rule-based summarization
- No API key needed for document retrieval or budget insights

## 💡 Tips

1. **Start Simple**: Use `--example` flag first
2. **Add Azure Gradually**: Start with Blob Storage, then add SQL/Synapse
3. **Check Logs**: Review `pipeline.log` for detailed information
4. **Use Small Datasets**: Test with limited documents first (`--limit 5`)

## 📚 Learn More

- **Full Documentation**: See [README.md](README.md)
- **Deployment Guide**: See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Examples**: Check the `examples/` directory

## 🎉 You're Ready!

Try running your first pipeline:

```bash
python main.py --example
```

For help:
```bash
python main.py --help
```

---

**Happy analyzing! 📊**
