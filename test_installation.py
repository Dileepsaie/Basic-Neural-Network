"""
Installation Verification Script
Run this to verify all components are properly installed
"""
import sys
import os

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    tests = []
    
    # Core dependencies
    try:
        import pandas
        tests.append(("✅ pandas", True))
    except ImportError as e:
        tests.append(("❌ pandas", False, str(e)))
    
    try:
        import numpy
        tests.append(("✅ numpy", True))
    except ImportError as e:
        tests.append(("❌ numpy", False, str(e)))
    
    try:
        import pydantic
        tests.append(("✅ pydantic", True))
    except ImportError as e:
        tests.append(("❌ pydantic", False, str(e)))
    
    try:
        import yaml
        tests.append(("✅ PyYAML", True))
    except ImportError as e:
        tests.append(("❌ PyYAML", False, str(e)))
    
    # Azure SDKs (optional)
    try:
        import azure.storage.blob
        tests.append(("✅ azure-storage-blob", True))
    except ImportError:
        tests.append(("⚠️  azure-storage-blob (optional)", True))
    
    try:
        import azure.identity
        tests.append(("✅ azure-identity", True))
    except ImportError:
        tests.append(("⚠️  azure-identity (optional)", True))
    
    # OpenAI (optional)
    try:
        import openai
        tests.append(("✅ openai", True))
    except ImportError:
        tests.append(("⚠️  openai (optional)", True))
    
    # Print results
    print("\nDependency Check:")
    for test in tests:
        if len(test) == 2:
            print(f"  {test[0]}")
        else:
            print(f"  {test[0]}: {test[2]}")
    
    return all(test[1] for test in tests)


def test_project_structure():
    """Test if project structure is correct"""
    print("\n\nTesting project structure...")
    
    required_paths = [
        'src/',
        'src/models/',
        'src/workflows/',
        'src/connectors/',
        'data/',
        'data/documents/',
        'data/output/',
        'examples/',
        'config.yaml',
        'requirements.txt',
        'main.py'
    ]
    
    all_exist = True
    for path in required_paths:
        exists = os.path.exists(path)
        status = "✅" if exists else "❌"
        print(f"  {status} {path}")
        if not exists:
            all_exist = False
    
    return all_exist


def test_module_imports():
    """Test if custom modules can be imported"""
    print("\n\nTesting module imports...")
    
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
    
    tests = []
    
    try:
        from src.models import FinancialDocument, FinancialSummary, BudgetInsight
        tests.append(("✅ Data models", True))
    except Exception as e:
        tests.append(("❌ Data models", False, str(e)))
    
    try:
        from src.workflows import (
            FinancialSummarizationWorkflow,
            BudgetInsightsWorkflow
        )
        tests.append(("✅ Workflows", True))
    except Exception as e:
        tests.append(("❌ Workflows", False, str(e)))
    
    try:
        from src.pipeline import FinancialPipeline
        tests.append(("✅ Pipeline", True))
    except Exception as e:
        tests.append(("❌ Pipeline", False, str(e)))
    
    try:
        from src.connectors import (
            AzureBlobConnector,
            AzureSQLConnector,
            AzureSynapseConnector,
            DataverseConnector
        )
        tests.append(("✅ Azure connectors", True))
    except Exception as e:
        tests.append(("❌ Azure connectors", False, str(e)))
    
    for test in tests:
        if len(test) == 2:
            print(f"  {test[0]}")
        else:
            print(f"  {test[0]}: {test[2]}")
    
    return all(test[1] for test in tests)


def test_config():
    """Test if configuration can be loaded"""
    print("\n\nTesting configuration...")
    
    try:
        import yaml
        
        if os.path.exists('config.yaml'):
            with open('config.yaml', 'r') as f:
                config = yaml.safe_load(f)
            print("  ✅ config.yaml loaded successfully")
            
            # Check key sections
            if 'document_storage' in config:
                print("  ✅ document_storage configured")
            if 'llm' in config:
                print("  ✅ llm configured")
            if 'workflows' in config:
                print("  ✅ workflows configured")
            
            return True
        else:
            print("  ❌ config.yaml not found")
            return False
    except Exception as e:
        print(f"  ❌ Error loading config: {e}")
        return False


def test_environment():
    """Test if environment is set up"""
    print("\n\nTesting environment...")
    
    from dotenv import load_dotenv
    load_dotenv()
    
    env_vars = [
        ('OPENAI_API_KEY', False),  # Optional
        ('AZURE_STORAGE_ACCOUNT_NAME', False),  # Optional
        ('AZURE_TENANT_ID', False),  # Optional
    ]
    
    for var_name, required in env_vars:
        value = os.getenv(var_name)
        if value:
            masked = value[:8] + "..." if len(value) > 8 else "***"
            print(f"  ✅ {var_name} = {masked}")
        else:
            status = "❌" if required else "⚠️ "
            suffix = "(required)" if required else "(optional)"
            print(f"  {status} {var_name} not set {suffix}")
    
    return True


def main():
    """Run all tests"""
    print("=" * 80)
    print("Financial Pipeline - Installation Verification")
    print("=" * 80)
    
    results = []
    
    # Run tests
    results.append(("Dependencies", test_imports()))
    results.append(("Project Structure", test_project_structure()))
    results.append(("Module Imports", test_module_imports()))
    results.append(("Configuration", test_config()))
    results.append(("Environment", test_environment()))
    
    # Summary
    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    all_passed = True
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"  {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("✅ All tests passed! Your installation is ready.")
        print("\nNext steps:")
        print("  1. Configure environment variables in .env")
        print("  2. Update config.yaml with your Azure resources")
        print("  3. Run: python main.py --example")
    else:
        print("❌ Some tests failed. Please review errors above.")
        print("\nTroubleshooting:")
        print("  1. Install dependencies: pip install -r requirements.txt")
        print("  2. Check file paths and permissions")
        print("  3. Review error messages above")
    print("=" * 80)
    
    return 0 if all_passed else 1


if __name__ == '__main__':
    sys.exit(main())
