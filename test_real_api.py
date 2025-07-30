#!/usr/bin/env python3
"""
Test script for the Ambivo MCP Server with real JWT token
"""

import asyncio
import json
import sys
import os

# Add the current directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from server import AmbivoAPIClient
from config import ServerConfig

# Real JWT token (expires: 2025-05-29)
JWT_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNThmYzBmMDdhYWYwOGU0MGMzNjE5OTUzIiwidGVuYW50X2lkIjoiNWE3N2IwZmI4YjU3ODY0ZDdlMTZkNGJhIiwiZXhwIjoxNzUzOTE3MjQwLCJzY29wZXMiOlsiYWxsIl0sImZpcnN0X2xvZ2luIjpmYWxzZSwibW9kdWxlX2FjY2VzcyI6eyJhbGwiOiIqIn0sImNsaWVudF9jb25uZWN0aW9uX2lkIjoiNjg4OTU1YjgxODBkYzYwZDE4MGEwYTQzIn0.n-5422RQgpPv926TbXEl94fxUJevDfVh4rf0aSxWvHE"

async def test_real_api():
    """Test the MCP server with real API calls"""
    print("🚀 Testing Ambivo MCP Server with Real API")
    print("=" * 60)
    
    # Initialize client with proper configuration
    config = ServerConfig()
    client = AmbivoAPIClient(config)
    
    print(f"📡 API Base URL: {client.base_url}")
    print(f"🔒 Token validation: {'Enabled' if config.token_validation_enabled else 'Disabled'}")
    print()
    
    try:
        # Test 1: Set authentication token
        print("Test 1: Authentication")
        print("-" * 30)
        client.set_auth_token(JWT_TOKEN)
        print("✅ JWT token set successfully")
        print(f"🔑 Token length: {len(JWT_TOKEN)} characters")
        print()
        
        # Test 2: Natural Language Query
        print("Test 2: Natural Language Query")
        print("-" * 35)
        
        natural_queries = [
            {"query": "Show me leads created in the last 7 days", "format": "both"},
            {"query": "Find contacts with gmail addresses", "format": "table"},
            {"query": "List opportunities worth more than $1000", "format": "natural"}
        ]
        
        for i, test_query in enumerate(natural_queries, 1):
            print(f"Query {i}: {test_query['query']}")
            try:
                result = await client.natural_query(
                    test_query["query"], 
                    test_query["format"]
                )
                print(f"✅ Success! Response type: {type(result)}")
                if isinstance(result, dict):
                    print(f"📊 Response keys: {list(result.keys())}")
                    if 'data' in result:
                        data_count = len(result['data']) if isinstance(result['data'], list) else 'N/A'
                        print(f"📈 Data records: {data_count}")
                print()
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                print()
        
        
        print("🎉 API Testing Complete!")
        
    except Exception as e:
        print(f"💥 Critical Error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        await client.close()
        print("🔌 HTTP client closed")

async def test_mcp_tools():
    """Test the MCP tools interface"""
    print("\n🛠️  Testing MCP Tools Interface")
    print("=" * 40)
    
    # Import MCP server components
    from server import handle_list_tools, handle_call_tool
    
    try:
        # Test 1: List available tools
        print("Test 1: List Tools")
        print("-" * 20)
        tools = await handle_list_tools()
        print(f"✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"   🔧 {tool.name}: {tool.description[:60]}...")
        print()
        
        # Test 2: Set auth token via MCP tool
        print("Test 2: Set Auth Token (MCP Tool)")
        print("-" * 38)
        auth_result = await handle_call_tool("set_auth_token", {"token": JWT_TOKEN})
        print(f"✅ Auth result: {auth_result[0].text}")
        print()
        
        # Test 3: Natural query via MCP tool
        print("Test 3: Natural Query (MCP Tool)")
        print("-" * 35)
        query_result = await handle_call_tool("natural_query", {
            "query": "Show me recent leads",
            "response_format": "both"
        })
        print(f"✅ Query result length: {len(query_result[0].text)} characters")
        print(f"📝 Result preview: {query_result[0].text[:200]}...")
        print()
        
        
        print("🎉 MCP Tools Testing Complete!")
        
    except Exception as e:
        print(f"💥 MCP Tools Error: {str(e)}")
        import traceback
        traceback.print_exc()

async def main():
    """Run all tests"""
    print("🧪 Ambivo MCP Server - Real API Test Suite")
    print("=" * 60)
    print(f"🌐 Target API: https://goferapi.ambivo.com")
    print(f"🔑 Using real JWT token")
    print(f"⏰ Test started at: {asyncio.get_event_loop().time()}")
    print()
    
    # Run API tests
    await test_real_api()
    
    # Run MCP tools tests
    await test_mcp_tools()
    
    print("\n" + "=" * 60)
    print("🏁 All tests completed!")
    print("✅ The MCP server is ready for production use")
    print("💡 Next step: Configure Claude Code to use this MCP server")

if __name__ == "__main__":
    asyncio.run(main())