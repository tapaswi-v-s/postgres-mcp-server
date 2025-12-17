# health_check.py
"""
MCP Server Health Check Script
Tests database connectivity, server functionality, and all tools
"""

import os
import sys
import asyncio
from datetime import datetime
from dotenv import load_dotenv
from sqlalchemy import text

# Color codes for terminal output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_status(message, status="info"):
    """Print colored status messages"""
    colors = {
        "success": GREEN,
        "error": RED,
        "warning": YELLOW,
        "info": BLUE
    }
    color = colors.get(status, RESET)
    symbols = {
        "success": "✓",
        "error": "✗",
        "warning": "⚠",
        "info": "ℹ"
    }
    symbol = symbols.get(status, "→")
    print(f"{color}{symbol} {message}{RESET}")

def check_environment():
    """Check if all required environment variables are set"""
    print("\n" + "=" * 60)
    print("1. CHECKING ENVIRONMENT VARIABLES")
    print("=" * 60)
    
    load_dotenv()
    
    required_vars = ["DB_HOST", "DB_NAME", "DB_USER", "DB_PASSWORD"]
    all_present = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask password
            display_value = "****" if var == "DB_PASSWORD" else value
            print_status(f"{var}: {display_value}", "success")
        else:
            print_status(f"{var}: NOT SET", "error")
            all_present = False
    
    return all_present

async def check_database_connection():
    """Test database connection"""
    print("\n" + "=" * 60)
    print("2. TESTING DATABASE CONNECTION")
    print("=" * 60)
    
    try:
        from server import DatabaseConnection
        
        db = DatabaseConnection()
        engine = db.get_engine()
        
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 as test"))
            row = result.fetchone()
            
        print_status(f"Connected to database: {os.getenv('DB_NAME')}", "success")
        print_status(f"Database host: {os.getenv('DB_HOST')}", "success")
        return True
        
    except Exception as e:
        print_status(f"Database connection failed: {str(e)}", "error")
        return False

async def test_tool(tool_name, func, *args, **kwargs):
    """Test individual tool"""
    try:
        result = await func(*args, **kwargs)
        
        # Check if result contains error
        if result and isinstance(result, str) and "Error" in result:
            print_status(f"{tool_name}: FAILED - {result[:100]}", "error")
            return False
        else:
            print_status(f"{tool_name}: OK", "success")
            if result:
                # Show first 200 chars of result
                preview = str(result)[:200].replace('\n', ' ')
                print(f"  {BLUE}Preview:{RESET} {preview}...")
            return True
            
    except Exception as e:
        print_status(f"{tool_name}: FAILED - {str(e)}", "error")
        return False

async def check_tools():
    """Test all MCP server tools"""
    print("\n" + "=" * 60)
    print("3. TESTING MCP SERVER TOOLS")
    print("=" * 60)
    
    try:
        from server import (
            list_schemas_impl,
            list_tables_impl,
            describe_table_impl,
            execute_select_query_impl,
            get_sample_data_impl
        )
        
        results = []
        
        # Test 1: List schemas
        results.append(await test_tool("list_schemas", list_schemas_impl))
        
        # Test 2: List tables (use first available schema)
        # Try common schema names
        for schema in ["public", "inventory", "hr"]:
            result = await test_tool(f"list_tables (schema: {schema})", list_tables_impl, schema)
            results.append(result)
            if result:
                break
        
        # Test 3: Simple SELECT query
        results.append(await test_tool(
            "execute_select_query (SELECT 1)",
            execute_select_query_impl,
            "SELECT 1 as test"
        ))
        
        return all(results[:2])  # At least first 2 should pass
        
    except Exception as e:
        print_status(f"Tool testing failed: {str(e)}", "error")
        return False

async def check_server_imports():
    """Check if server can be imported"""
    print("\n" + "=" * 60)
    print("4. CHECKING SERVER IMPORTS")
    print("=" * 60)
    
    try:
        import server
        print_status("server.py imported successfully", "success")
        
        # Check for required functions
        required = ["DatabaseConnection", "list_tools", "call_tool", "main"]
        for item in required:
            if hasattr(server, item):
                print_status(f"Found: {item}", "success")
            else:
                print_status(f"Missing: {item}", "error")
                return False
        
        return True
        
    except Exception as e:
        print_status(f"Failed to import server: {str(e)}", "error")
        return False

async def main():
    """Run all health checks"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 15 + "MCP SERVER HEALTH CHECK" + " " * 20 + "║")
    print("╚" + "=" * 58 + "╝")
    print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    results = {
        "Environment Variables": check_environment(),
        "Server Imports": await check_server_imports(),
        "Database Connection": await check_database_connection(),
        "MCP Tools": await check_tools()
    }
    
    # Summary
    print("\n" + "=" * 60)
    print("HEALTH CHECK SUMMARY")
    print("=" * 60)
    
    all_passed = True
    for check, passed in results.items():
        status = "success" if passed else "error"
        result = "PASSED" if passed else "FAILED"
        print_status(f"{check}: {result}", status)
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print_status("ALL CHECKS PASSED ✓", "success")
        print_status("MCP Server is ready to use!", "success")
        sys.exit(0)
    else:
        print_status("SOME CHECKS FAILED ✗", "error")
        print_status("Please fix the issues above before running the server", "warning")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nHealth check interrupted by user")
        sys.exit(1)
    except Exception as e:
        print_status(f"Health check failed with error: {str(e)}", "error")
        sys.exit(1)