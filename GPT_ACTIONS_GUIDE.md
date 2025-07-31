# Ambivo GPT Actions Guide

This guide shows how to integrate Ambivo CRM with ChatGPT using GPT Actions.

## Overview

GPT Actions allow you to connect ChatGPT directly to external APIs. This integration provides:

- **Natural language CRM queries** in ChatGPT
- **Direct API access** without requiring a separate server
- **OpenAPI-based integration** for reliable communication
- **JWT authentication** for secure access

## Architecture

```
ChatGPT → GPT Actions → Ambivo GPT Actions Server → Ambivo MCP Server → Ambivo API
```

**Benefits over Tornado server approach:**
- ✅ No need to keep Tornado server running
- ✅ Self-contained HTTP server with minimal dependencies  
- ✅ Direct integration with ChatGPT's GPT Actions
- ✅ Automatic OpenAPI schema generation
- ✅ Built-in authentication and CORS handling

## Quick Start

### 1. Install with GPT Actions Support

```bash
# Install with GPT Actions dependencies
pip install -e ".[gpt-actions]"

# Or install specific dependencies
pip install pyyaml>=6.0.0
```

### 2. Start GPT Actions Server

**Note:** The server now supports multi-tenant authentication. Each user provides their own JWT token through ChatGPT's authentication settings, so you don't need to set `AMBIVO_AUTH_TOKEN` environment variable anymore.

### 3. Run the Server

```bash
# Start server on default port 8080
ambivo-gpt-actions serve

# Or specify custom host/port
ambivo-gpt-actions serve --host 0.0.0.0 --port 9000
```

### 4. Verify Server is Running

```bash
# Check health
curl http://localhost:8080/health

# View API documentation
curl http://localhost:8080/

# Get OpenAPI schema
curl http://localhost:8080/openapi.yaml
```

## ChatGPT Integration

### Step 1: Create Custom GPT

1. Go to ChatGPT → **Explore GPTs** → **Create a GPT**
2. Configure basic details:
   - **Name**: "Ambivo CRM Assistant"
   - **Description**: "Access and query Ambivo CRM data using natural language"

### Step 2: Add GPT Action

1. In GPT configuration, go to **Actions** section
2. Click **Create new action**
3. In the schema field, paste your OpenAPI URL:
   ```
   http://localhost:8080/openapi.yaml
   ```
4. ChatGPT will automatically import the schema

### Step 3: Configure Authentication

1. In **Authentication** section, select **API Key**
2. Set **Auth Type** to **Bearer**
3. Enter your personal Ambivo JWT token

**Multi-tenant Support:** Each user enters their own Ambivo JWT token here. The server will use this token to authenticate API requests, ensuring users only see their own CRM data.

### Step 4: Test Integration

Try these example queries in ChatGPT:

```
Show me leads created this week
Find contacts with gmail addresses  
What deals are closing this month?
Get contact information for John Smith
List recent activities for lead ID 12345
```

## Available Endpoints

### Core Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API documentation |
| `/health` | GET | Health check and available tools |
| `/openapi.yaml` | GET | OpenAPI specification |
| `/.well-known/ai-plugin.json` | GET | AI plugin manifest |

### Tool Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/tools` | GET | List available CRM tools |
| `/tools` | POST | Execute a specific tool |
| `/query` | POST | Natural language query |

### Individual Tool Endpoints

Each MCP tool gets its own endpoint:
- `/tools/natural-query` - Natural language queries
- `/tools/get-leads` - Get leads data
- `/tools/get-contacts` - Get contacts data
- `/tools/search-entities` - Search across entities
- And more based on your MCP tools...

## API Examples

### Natural Language Query

```bash
curl -X POST http://localhost:8080/query \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "Show me leads created this week",
    "response_format": "both"
  }'
```

### Direct Tool Call

```bash
curl -X POST http://localhost:8080/tools \
  -H "Authorization: Bearer your-jwt-token" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "get_leads",
    "arguments": {
      "limit": 10,
      "created_after": "2024-01-01"
    }
  }'
```

### List Available Tools

```bash
curl -X GET http://localhost:8080/tools \
  -H "Authorization: Bearer your-jwt-token"
```

## CLI Commands

### Server Commands

```bash
# Start server (default: localhost:8080)
ambivo-gpt-actions serve

# Custom host and port
ambivo-gpt-actions serve --host 0.0.0.0 --port 9000

# Verbose logging
ambivo-gpt-actions serve --verbose
```

### Schema Generation

```bash
# Generate OpenAPI schema
ambivo-gpt-actions generate-schema

# Custom output file
ambivo-gpt-actions generate-schema --output my-schema.yaml

# JSON format
ambivo-gpt-actions generate-schema --format json --output schema.json
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `AMBIVO_AUTH_TOKEN` | JWT authentication token | Not required (users provide via ChatGPT) |
| `AMBIVO_API_BASE_URL` | Base URL for Ambivo API | `https://goferapi.ambivo.com` |
| `AMBIVO_GPT_HOST` | Server host | `localhost` |
| `AMBIVO_GPT_PORT` | Server port | `8080` |

### Configuration File

See `gpt_actions_config.json` for GPT setup configuration:

```json
{
  "name": "Ambivo CRM Assistant",
  "description": "Access and query Ambivo CRM data using natural language",
  "schema_url": "http://localhost:8080/openapi.yaml",
  "authentication": {
    "type": "bearer_token",
    "instructions": "Get your JWT token from Ambivo and paste it here"
  }
}
```

## Deployment Options

### Local Development
```bash
ambivo-gpt-actions serve --host localhost --port 8080
```

### Network Access
```bash
ambivo-gpt-actions serve --host 0.0.0.0 --port 8080
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -e ".[gpt-actions]"

EXPOSE 8080
CMD ["ambivo-gpt-actions", "serve", "--host", "0.0.0.0", "--port", "8080"]
```

### Cloud Deployment

For production use, deploy to cloud platforms:

**Railway/Render/Heroku:**
- Deploy without setting `AMBIVO_AUTH_TOKEN` (users provide their own)
- Set port from `$PORT` environment variable
- Use `ambivo-gpt-actions serve --host 0.0.0.0 --port $PORT`

**AWS/GCP/Azure:**
- Deploy as container or serverless function
- Configure SSL/TLS certificate
- Update ChatGPT Action URL to your domain

## Troubleshooting

### Common Issues

**1. "Server disconnected" in ChatGPT**
- Ensure server is running: `curl http://localhost:8080/health`
- Check firewall/network settings
- Verify OpenAPI URL is accessible from ChatGPT

**2. "Authentication failed"**
- Verify JWT token is valid and not expired
- Check token format (should start with 'eyJ')
- Ensure token has required scopes

**3. "Tool not found"**
- Run `ambivo-gpt-actions generate-schema` to refresh
- Check MCP server is working: test with Claude Desktop first
- Verify tool names match exactly

**4. Import errors**
- Install dependencies: `pip install -e ".[gpt-actions]"`
- Check Python version: requires >= 3.11

### Debug Mode

```bash
# Enable verbose logging
ambivo-gpt-actions serve --verbose

# Test individual components
python -m ambivo_gpt_actions.schema_generator
python -c "from ambivo_mcp_server.server import handle_list_tools; import asyncio; print(asyncio.run(handle_list_tools()))"
```

### Logs

Check server logs for detailed error information:
- Connection attempts from ChatGPT
- Authentication failures  
- Tool execution errors
- API communication issues

## Comparison: GPT Actions vs MCP

| Feature | MCP (Claude Desktop) | GPT Actions (ChatGPT) |
|---------|---------------------|----------------------|
| **Installation** | Local package | HTTP server + ChatGPT config |
| **Authentication** | Environment variable | Bearer token in ChatGPT |
| **Communication** | stdio/JSON-RPC | HTTP/REST API |
| **Schema** | MCP protocol | OpenAPI 3.0 |
| **Deployment** | Local only | Local or cloud |
| **Usage** | Direct in Claude Desktop | Custom GPT in ChatGPT |

Both approaches use the same underlying MCP tools and business logic, just different integration methods.

## Next Steps

1. **Test Integration**: Verify all tools work correctly with ChatGPT
2. **Deploy to Cloud**: For team access, deploy server to cloud platform  
3. **Monitor Usage**: Add logging and monitoring for production use
4. **Extend Tools**: Add more MCP tools as needed for your CRM workflows

For support, see the main [README.md](README.md) or open an issue on GitHub.