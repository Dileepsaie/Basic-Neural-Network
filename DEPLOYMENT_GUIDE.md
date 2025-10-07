# Azure Deployment Guide

Complete guide for deploying the Financial Data Processing Pipeline in Azure.

## 📋 Prerequisites

- Azure subscription
- Azure CLI installed
- Python 3.8+ installed
- Git installed

## 🚀 Step-by-Step Deployment

### 1. Azure Resource Setup

#### A. Create Resource Group

```bash
# Login to Azure
az login

# Create resource group
az group create \
  --name financial-pipeline-rg \
  --location eastus
```

#### B. Create Azure Blob Storage

```bash
# Create storage account
az storage account create \
  --name financialstorage001 \
  --resource-group financial-pipeline-rg \
  --location eastus \
  --sku Standard_LRS

# Get connection string
az storage account show-connection-string \
  --name financialstorage001 \
  --resource-group financial-pipeline-rg \
  --query connectionString \
  --output tsv

# Create containers
az storage container create \
  --name financial-documents \
  --account-name financialstorage001

az storage container create \
  --name financial-reports \
  --account-name financialstorage001
```

#### C. Create Azure SQL Database (Optional)

```bash
# Create SQL Server
az sql server create \
  --name financial-sql-server \
  --resource-group financial-pipeline-rg \
  --location eastus \
  --admin-user sqladmin \
  --admin-password YourStrongPassword123!

# Create database
az sql db create \
  --resource-group financial-pipeline-rg \
  --server financial-sql-server \
  --name FinancialDB \
  --service-objective S0

# Configure firewall (allow Azure services)
az sql server firewall-rule create \
  --resource-group financial-pipeline-rg \
  --server financial-sql-server \
  --name AllowAzureServices \
  --start-ip-address 0.0.0.0 \
  --end-ip-address 0.0.0.0
```

#### D. Create Azure Synapse Workspace (Optional)

```bash
# Create Synapse workspace
az synapse workspace create \
  --name financial-synapse-workspace \
  --resource-group financial-pipeline-rg \
  --storage-account financialstorage001 \
  --file-system synapsedata \
  --sql-admin-login-user sqladmin \
  --sql-admin-login-password YourStrongPassword123! \
  --location eastus

# Create SQL pool
az synapse sql pool create \
  --name FinancialPool \
  --performance-level DW100c \
  --workspace-name financial-synapse-workspace \
  --resource-group financial-pipeline-rg
```

### 2. Azure AD Application Setup (for Dataverse)

#### A. Register Application

```bash
# Create Azure AD app
az ad app create \
  --display-name "Financial Pipeline App" \
  --available-to-other-tenants false

# Get App ID
az ad app list --display-name "Financial Pipeline App" --query [].appId -o tsv

# Create service principal
az ad sp create --id <APP_ID>

# Create client secret
az ad app credential reset --id <APP_ID> --append
```

#### B. Grant Permissions

1. Go to Azure Portal → Azure Active Directory → App registrations
2. Select "Financial Pipeline App"
3. Go to "API permissions"
4. Add permissions:
   - Dynamics CRM → Delegated → user_impersonation
   - Microsoft Graph → Application → User.Read.All
5. Grant admin consent

### 3. PowerApps Dataverse Setup

#### A. Create PowerApps Environment

1. Go to https://admin.powerplatform.microsoft.com
2. Create new environment
3. Enable Dataverse database
4. Note the environment URL

#### B. Create Custom Tables (Example)

1. Go to PowerApps → Tables → New table
2. Create tables:
   - **Financial Records**
     - Fields: date, department, amount, category, description
   - **Budget Submissions**
     - Fields: department, budget_amount, fiscal_year, status
   - **Financial Insights** (for output)
     - Fields: name, description, insights, recommendations, health_score

### 4. Configure Azure VM or App Service

#### Option A: Azure VM

```bash
# Create Ubuntu VM
az vm create \
  --resource-group financial-pipeline-rg \
  --name financial-pipeline-vm \
  --image UbuntuLTS \
  --size Standard_D2s_v3 \
  --admin-username azureuser \
  --generate-ssh-keys

# Enable managed identity
az vm identity assign \
  --name financial-pipeline-vm \
  --resource-group financial-pipeline-rg

# SSH into VM
ssh azureuser@<VM_PUBLIC_IP>

# Install Python and dependencies
sudo apt update
sudo apt install python3-pip python3-venv git -y

# Clone and setup
git clone <repository-url>
cd financial-data-pipeline
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Option B: Azure Container Instance

```bash
# Build and push Docker image
docker build -t financial-pipeline .
az acr create --name financialregistry --resource-group financial-pipeline-rg --sku Basic
az acr login --name financialregistry
docker tag financial-pipeline financialregistry.azurecr.io/financial-pipeline:v1
docker push financialregistry.azurecr.io/financial-pipeline:v1

# Deploy container
az container create \
  --resource-group financial-pipeline-rg \
  --name financial-pipeline-container \
  --image financialregistry.azurecr.io/financial-pipeline:v1 \
  --cpu 2 \
  --memory 4 \
  --environment-variables \
    AZURE_STORAGE_ACCOUNT_NAME=financialstorage001 \
    OPENAI_API_KEY=<your-key>
```

### 5. Grant Managed Identity Permissions

```bash
# Get managed identity principal ID
PRINCIPAL_ID=$(az vm identity show \
  --name financial-pipeline-vm \
  --resource-group financial-pipeline-rg \
  --query principalId \
  --output tsv)

# Grant Storage Blob Data Contributor role
az role assignment create \
  --assignee $PRINCIPAL_ID \
  --role "Storage Blob Data Contributor" \
  --scope /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/financial-pipeline-rg

# Grant SQL Database Contributor role (if using SQL)
az role assignment create \
  --assignee $PRINCIPAL_ID \
  --role "SQL DB Contributor" \
  --scope /subscriptions/<SUBSCRIPTION_ID>/resourceGroups/financial-pipeline-rg
```

### 6. Configure Environment Variables

Create `.env` file on your deployment target:

```bash
# OpenAI
OPENAI_API_KEY=sk-...

# Azure Authentication
AZURE_TENANT_ID=<tenant-id>
AZURE_CLIENT_ID=<app-id>
AZURE_CLIENT_SECRET=<client-secret>

# Azure Blob Storage
AZURE_STORAGE_ACCOUNT_NAME=financialstorage001
AZURE_STORAGE_CONNECTION_STRING=<connection-string>

# Azure SQL
AZURE_SQL_SERVER=financial-sql-server.database.windows.net
AZURE_SQL_DATABASE=FinancialDB
# For managed identity, no connection string needed

# Azure Synapse
AZURE_SYNAPSE_WORKSPACE=financial-synapse-workspace
AZURE_SYNAPSE_SQL_POOL=FinancialPool

# Dataverse
DATAVERSE_ENVIRONMENT_URL=https://yourenv.crm.dynamics.com
DATAVERSE_CLIENT_ID=<app-id>
DATAVERSE_CLIENT_SECRET=<client-secret>
```

### 7. Upload Sample Data

```bash
# Upload sample documents to Blob Storage
az storage blob upload-batch \
  --account-name financialstorage001 \
  --destination financial-documents \
  --source ./data/documents \
  --pattern "*.txt"
```

### 8. Test Deployment

```bash
# Test with example data
python main.py --example

# Test with real Azure sources
python main.py \
  --keywords budget quarterly \
  --days-back 90 \
  --sources blob sql
```

### 9. Setup Scheduled Execution (Optional)

#### Using Azure Logic Apps

1. Create Logic App
2. Add Recurrence trigger (daily/weekly)
3. Add HTTP action to call your API/VM
4. Configure error handling and notifications

#### Using Azure Automation

```bash
# Create automation account
az automation account create \
  --resource-group financial-pipeline-rg \
  --name financial-automation \
  --location eastus

# Create runbook (Python)
# Upload pipeline code as runbook
```

## 🔒 Security Best Practices

1. **Use Managed Identity** whenever possible
2. **Store secrets** in Azure Key Vault
3. **Enable encryption** for Blob Storage
4. **Use Private Endpoints** for sensitive data
5. **Enable Azure Monitor** for logging
6. **Configure Network Security Groups**
7. **Regular security updates**

## 📊 Monitoring & Logging

### Enable Application Insights

```bash
# Create Application Insights
az monitor app-insights component create \
  --app financial-pipeline-insights \
  --location eastus \
  --resource-group financial-pipeline-rg

# Get instrumentation key
az monitor app-insights component show \
  --app financial-pipeline-insights \
  --resource-group financial-pipeline-rg \
  --query instrumentationKey
```

### Configure Alerts

```bash
# Create action group for notifications
az monitor action-group create \
  --name financial-alerts \
  --resource-group financial-pipeline-rg \
  --short-name FinAlerts \
  --email-receiver admin admin@example.com

# Create alert rule
az monitor metrics alert create \
  --name high-error-rate \
  --resource-group financial-pipeline-rg \
  --scopes <resource-id> \
  --condition "count > 5" \
  --description "Alert when error rate is high"
```

## 🔧 Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Check managed identity is enabled
   - Verify role assignments
   - Check service principal permissions

2. **Connection Timeouts**
   - Check firewall rules
   - Verify network connectivity
   - Check if private endpoints are configured

3. **Permission Denied**
   - Verify RBAC roles
   - Check storage account access
   - Verify SQL/Synapse permissions

### Debug Commands

```bash
# Check managed identity
az vm identity show --name financial-pipeline-vm --resource-group financial-pipeline-rg

# Test storage connection
az storage blob list --account-name financialstorage001 --container-name financial-documents

# Check SQL connectivity
az sql db show --name FinancialDB --server financial-sql-server --resource-group financial-pipeline-rg
```

## 📈 Scaling

### Horizontal Scaling
- Deploy multiple VM instances
- Use Azure Load Balancer
- Implement queue-based processing

### Vertical Scaling
- Increase VM size
- Upgrade SQL/Synapse tier
- Optimize queries and processing

## 💰 Cost Optimization

1. Use **Azure Reserved Instances** for long-term deployment
2. Enable **auto-shutdown** for dev/test VMs
3. Use **spot instances** for non-critical workloads
4. Monitor and optimize **storage tiers**
5. Set up **cost alerts**

## 🔄 CI/CD Pipeline

### Azure DevOps Pipeline Example

```yaml
trigger:
  branches:
    include:
      - main

pool:
  vmImage: 'ubuntu-latest'

steps:
- task: UsePythonVersion@0
  inputs:
    versionSpec: '3.9'

- script: |
    pip install -r requirements.txt
    pytest tests/
  displayName: 'Install and Test'

- task: AzureCLI@2
  inputs:
    azureSubscription: 'Azure-Subscription'
    scriptType: 'bash'
    scriptLocation: 'inlineScript'
    inlineScript: |
      az vm run-command invoke \
        --name financial-pipeline-vm \
        --resource-group financial-pipeline-rg \
        --command-id RunShellScript \
        --scripts "cd /app && git pull && python main.py"
```

## ✅ Post-Deployment Checklist

- [ ] All Azure resources created
- [ ] Managed identity configured
- [ ] Role assignments granted
- [ ] Environment variables set
- [ ] Sample data uploaded
- [ ] Connections tested
- [ ] Monitoring enabled
- [ ] Alerts configured
- [ ] Documentation updated
- [ ] Backup strategy defined

## 📞 Support

For deployment issues:
1. Check Azure Portal for resource status
2. Review logs in Application Insights
3. Verify all environment variables
4. Test each connector individually
5. Contact Azure support if needed

---

**Deployment Guide Version 1.0**
