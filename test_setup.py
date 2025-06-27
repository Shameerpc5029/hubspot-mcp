#!/usr/bin/env python3
"""
Test script to validate the HubSpot MCP server setup.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported without errors."""
    try:
        from hubspot.server import HubSpotMCPServer
        from hubspot.connection import get_access_token
        from hubspot.tools.company import HubSpotClient
        from hubspot.tools.contact import (
            HubSpotListManager,
            HubSpotContactDeleter,
            HubSpotContactUpdater,
            HubSpotContactSearcher,
            HubSpotContactGetter,
            HubSpotRecentContactsGetter,
            HubSpotContactCreator
        )
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_server_initialization():
    """Test that the server can be initialized."""
    try:
        from hubspot.server import HubSpotMCPServer
        server = HubSpotMCPServer()
        print("✅ Server initialization successful")
        return True
    except Exception as e:
        print(f"❌ Server initialization error: {e}")
        return False

def test_environment_variables():
    """Test environment variable handling."""
    try:
        from dotenv import load_dotenv
        load_dotenv()
        
        # Check if we have at least one authentication method
        nango_vars = all([
            os.environ.get("NANGO_CONNECTION_ID"),
            os.environ.get("NANGO_INTEGRATION_ID"),
            os.environ.get("NANGO_BASE_URL"),
            os.environ.get("NANGO_SECRET_KEY")
        ])
        
        direct_token = os.environ.get("HUBSPOT_ACCESS_TOKEN")
        
        if nango_vars:
            print("✅ Nango environment variables found")
            return True
        elif direct_token:
            print("✅ Direct HubSpot access token found")
            return True
        else:
            print("⚠️  No authentication credentials found in environment")
            print("   Please set either:")
            print("   - NANGO_* variables for Nango integration")
            print("   - HUBSPOT_ACCESS_TOKEN for direct access")
            return False
            
    except Exception as e:
        print(f"❌ Environment variable test error: {e}")
        return False

def main():
    """Run all tests."""
    print("🔍 Testing HubSpot MCP Server setup...\n")
    
    tests = [
        ("Import Test", test_imports),
        ("Server Initialization Test", test_server_initialization),
        ("Environment Variables Test", test_environment_variables),
    ]
    
    results = []
    for test_name, test_func in tests:
        print(f"Running {test_name}...")
        result = test_func()
        results.append(result)
        print()
    
    if all(results):
        print("🎉 All tests passed! The HubSpot MCP server is ready to use.")
        print("\nTo start the server, run:")
        print("  python run_server.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        failed_tests = [tests[i][0] for i, result in enumerate(results) if not result]
        print(f"Failed tests: {', '.join(failed_tests)}")
        sys.exit(1)

if __name__ == "__main__":
    main()
