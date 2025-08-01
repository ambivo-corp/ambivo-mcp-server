# Ambivo Claude MCP Server

This Claude MCP (Model Context Protocol) server provides access to Ambivo API endpoints for natural language querying of entity data with Claude AI.

## Features

- **Natural Language Queries**: Execute natural language queries against entity data using the `/entity/natural_query` endpoint
- **JWT Authentication**: Secure access using Bearer token authentication
- **Rate Limiting**: Built-in rate limiting to prevent API abuse
- **Token Caching**: Efficient token validation with caching
- **Error Handling**: Comprehensive error handling with detailed error messages
- **Retry Logic**: Automatic retry with exponential backoff for failed requests

## Tools

### 1. `set_auth_token`
Set the JWT Bearer token for authentication with the Ambivo API.

**Parameters:**
- `token` (string, required): JWT Bearer token

**Usage:**
```json
{
  "token": "your-jwt-token-here"
}
```

### 2. `natural_query`
Execute natural language queries against Ambivo entity data.

**Parameters:**
- `query` (string, required): Natural language query describing what data you want
- `response_format` (string, optional): Response format - "table", "natural", or "both" (default: "both")

**Example queries:**
- "Show me leads created this week"
- "Find contacts with gmail addresses"
- "List opportunities worth more than $10,000"
- "Show me leads with attribution_source google_ads from the last 7 days"

**Usage:**
```json
{
  "query": "Show me leads created this week with attribution_source google_ads",
  "response_format": "both"
}
```


## About

This is a pure Claude-based MCP server implementation for the Ambivo API, designed to work seamlessly with Claude Desktop and other Claude-compatible MCP clients. It enables natural language interaction with your Ambivo CRM data through Claude's powerful language understanding capabilities.

## Installation

### Option 1: Install from PyPI (Recommended)
```bash
pip install ambivo-mcp-server
```

### Option 2: Install from Source
```bash
git clone https://github.com/ambivo-corp/ambivo-mcp-server.git
cd ambivo-mcp-server
pip install -e .
```

## Running the Server

```bash
# If installed via pip
ambivo-mcp-server

# Or using Python module
python -m ambivo_mcp_server.server
```

## Configuration

The server uses the following default configuration:
- **Base URL**: `https://goferapi.ambivo.com`
- **Timeout**: 30 seconds
- **Content Type**: `application/json`

You can modify these settings in the `AmbivoAPIClient` class if needed.

## Authentication

1. First, set your authentication token using the `set_auth_token` tool
2. The token will be included in all subsequent API requests as a Bearer token
3. The token should be a valid JWT token from your Ambivo API authentication

## Error Handling

The server provides comprehensive error handling:
- **Authentication errors**: Clear messages when token is missing or invalid
- **HTTP errors**: Detailed HTTP status codes and response messages
- **Validation errors**: Parameter validation with helpful error messages
- **Network errors**: Timeout and connection error handling

## API Endpoints

This MCP server interfaces with these Ambivo API endpoints:

### `/entity/natural_query`
- **Method**: POST
- **Purpose**: Process natural language queries for entity data retrieval
- **Authentication**: Required (JWT Bearer token)
- **Content-Type**: application/json

### `/entity/data`
- **Method**: POST  
- **Purpose**: Direct entity data access with structured parameters
- **Authentication**: Required (JWT Bearer token)
- **Content-Type**: application/json

## Example Workflow

1. **Set Authentication**:
   ```json
   {
     "tool": "set_auth_token",
     "arguments": {
       "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
     }
   }
   ```

2. **Natural Language Query**:
   ```json
   {
     "tool": "natural_query", 
     "arguments": {
       "query": "Show me all leads created in the last 30 days with phone numbers",
       "response_format": "both"
     }
   }
   ```

3. **Direct Entity Query**:
   ```json
   {
     "tool": "entity_data",
     "arguments": {
       "entity_type": "contact",
       "filters": {"email": {"$regex": "@gmail.com$"}},
       "limit": 100,
       "sort": {"created_date": -1}
     }
   }
   ```

## Development

To extend this MCP server:

1. **Add new tools**: Implement additional tools in the `handle_list_tools()` and `handle_call_tool()` functions
2. **Modify API client**: Extend the `AmbivoAPIClient` class to support additional endpoints
3. **Update configuration**: Modify default settings in the configuration section

## Troubleshooting

**Common Issues:**

1. **"Authentication required" error**: Ensure you've called `set_auth_token` first
2. **HTTP 401/403 errors**: Verify your JWT token is valid and not expired
3. **Connection timeout**: Check network connectivity and API endpoint availability
4. **Invalid parameters**: Review the tool schemas for required and optional parameters

**Logging:**

The server logs important events and errors. Check the console output for debugging information.