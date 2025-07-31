#!/usr/bin/env python3
"""
Test script for multi-tenant GPT Actions server
"""

import requests
import json

# Test configuration
BASE_URL = "http://localhost:8080"

def test_with_token(token):
    """Test API calls with a specific token"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    print(f"\nTesting with token: {token[:20]}...")
    
    # Test health check (no auth required)
    response = requests.get(f"{BASE_URL}/health")
    print(f"Health check: {response.status_code}")
    
    # Test list tools
    response = requests.get(f"{BASE_URL}/tools", headers=headers)
    print(f"List tools: {response.status_code}")
    if response.status_code == 200:
        tools = response.json()["tools"]
        print(f"Available tools: {len(tools)}")
    
    # Test natural query
    query_data = {
        "query": "Show me leads created this week",
        "response_format": "both"
    }
    response = requests.post(f"{BASE_URL}/query", json=query_data, headers=headers)
    print(f"Natural query: {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Query result: {result.get('result', '')[:100]}...")
    
    # Test direct tool call
    tool_data = {
        "name": "get_leads",
        "arguments": {
            "limit": 5
        }
    }
    response = requests.post(f"{BASE_URL}/tools", json=tool_data, headers=headers)
    print(f"Tool call (get_leads): {response.status_code}")
    if response.status_code == 200:
        result = response.json()
        print(f"Tool result: {result.get('result', '')[:100]}...")

def main():
    print("Multi-tenant GPT Actions Server Test")
    print("="*40)
    
    # Test with different tokens (replace with actual tokens)
    test_tokens = [
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.user1_token",  # User 1's token
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.user2_token",  # User 2's token
    ]
    
    print("\nNote: Replace test_tokens with actual JWT tokens from different users")
    print("Each user should only see their own CRM data")
    
    # Test without token (should fail)
    print("\nTesting without token:")
    response = requests.get(f"{BASE_URL}/tools")
    print(f"List tools without auth: {response.status_code} (should be 401)")
    
    # Test with each token
    for token in test_tokens:
        test_with_token(token)

if __name__ == "__main__":
    main()