# Deployment Guide - Ambivo MCP Server

This guide covers all the ways to deploy and distribute the Ambivo MCP Server for public use.

## Table of Contents

1. [PyPI Package Distribution](#pypi-package-distribution)
2. [GitHub Repository Setup](#github-repository-setup)
3. [Docker Deployment](#docker-deployment)
4. [Environment Configuration](#environment-configuration)
5. [Security Considerations](#security-considerations)
6. [Monitoring and Logging](#monitoring-and-logging)

## PyPI Package Distribution

### 1. Prepare for PyPI Release

```bash
# Install build dependencies
pip install build twine

# Build the package
python -m build

# Check the package
twine check dist/*
```

### 2. Upload to Test PyPI (Recommended First)

```bash
# Upload to Test PyPI
twine upload --repository testpypi dist/*

# Test installation from Test PyPI
pip install --index-url https://test.pypi.org/simple/ ambivo-mcp-server
```

### 3. Upload to Production PyPI

```bash
# Upload to PyPI
twine upload dist/*
```

### 4. Installation for End Users

Once published, users can install via:

```bash
# Install from PyPI
pip install ambivo-mcp-server

# Or with development dependencies
pip install ambivo-mcp-server[dev]

# Or with test dependencies
pip install ambivo-mcp-server[test]
```

## GitHub Repository Setup

### 1. Create Repository Structure

```
ambivo-mcp-server/
├── .github/
│   └── workflows/
│       ├── test.yml
│       └── publish.yml
├── examples/
│   ├── example_config.json
│   └── usage_examples.py
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   └── test_security.py
├── server.py
├── config.py
├── security.py
├── requirements.txt
├── pyproject.toml
├── setup.py
├── LICENSE
├── README.md
├── DEPLOYMENT.md
├── Dockerfile
├── docker-compose.yml
└── .dockerignore
```

### 2. Set Up GitHub Secrets

For automated publishing, add these secrets to your GitHub repository:

- `PYPI_API_TOKEN`: Your PyPI API token
- `TEST_PYPI_API_TOKEN`: Your Test PyPI API token

### 3. Release Process

1. Update version in `setup.py` and `pyproject.toml`
2. Create a git tag: `git tag v1.0.0`
3. Push tag: `git push origin v1.0.0`
4. Create a GitHub release
5. GitHub Actions will automatically publish to PyPI

## Docker Deployment

### 1. Build Docker Image

```bash
# Build the image
docker build -t ambivo/mcp-server:latest .

# Or use docker-compose
docker-compose build
```

### 2. Run with Docker

```bash
# Run container
docker run -d \
  --name ambivo-mcp-server \
  -e AMBIVO_BASE_URL=https://goferapi.ambivo.com \
  -e AMBIVO_LOG_LEVEL=INFO \
  ambivo/mcp-server:latest

# Or use docker-compose
docker-compose up -d
```

### 3. Docker Hub Distribution

```bash
# Tag for Docker Hub
docker tag ambivo/mcp-server:latest ambivo/mcp-server:1.0.0

# Push to Docker Hub
docker push ambivo/mcp-server:latest
docker push ambivo/mcp-server:1.0.0
```

### 4. Kubernetes Deployment

```yaml
# k8s-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ambivo-mcp-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: ambivo-mcp-server
  template:
    metadata:
      labels:
        app: ambivo-mcp-server
    spec:
      containers:
      - name: ambivo-mcp-server
        image: ambivo/mcp-server:latest
        env:
        - name: AMBIVO_BASE_URL
          value: "https://goferapi.ambivo.com"
        - name: AMBIVO_LOG_LEVEL
          value: "INFO"
        - name: AMBIVO_RATE_LIMIT_REQUESTS
          value: "100"
        resources:
          limits:
            cpu: 500m
            memory: 256Mi
          requests:
            cpu: 250m
            memory: 128Mi
---
apiVersion: v1
kind: Service
metadata:
  name: ambivo-mcp-server-service
spec:
  selector:
    app: ambivo-mcp-server
  ports:
  - port: 8000
    targetPort: 8000
```

## Environment Configuration

### 1. Environment Variables

Create a `.env` file or set environment variables:

```bash
# Core Configuration
AMBIVO_BASE_URL=https://goferapi.ambivo.com
AMBIVO_TIMEOUT=30.0
AMBIVO_MAX_RETRIES=3

# Security Configuration
AMBIVO_RATE_LIMIT_REQUESTS=100
AMBIVO_RATE_LIMIT_WINDOW=3600
AMBIVO_MAX_QUERY_LENGTH=1000
AMBIVO_MAX_PAYLOAD_SIZE=1048576

# Logging Configuration
AMBIVO_LOG_LEVEL=INFO
AMBIVO_LOG_FILE=/var/log/ambivo-mcp.log

# Server Configuration
AMBIVO_SERVER_NAME=ambivo-api
AMBIVO_SERVER_VERSION=1.0.0

# Token Configuration
AMBIVO_TOKEN_VALIDATION=true
AMBIVO_TOKEN_CACHE_TTL=300
```

### 2. Configuration File

Alternatively, use a JSON configuration file:

```bash
# Set config file path
export AMBIVO_CONFIG_FILE=/path/to/config.json

# Run server
ambivo-mcp-server
```

### 3. Production Configuration Example

```json
{
  "base_url": "https://api.ambivo.com",
  "timeout": 60.0,
  "max_retries": 5,
  "rate_limit_requests": 1000,
  "rate_limit_window": 3600,
  "max_query_length": 2000,
  "max_payload_size": 2097152,
  "log_level": "WARNING",
  "log_file": "/var/log/ambivo-mcp/server.log",
  "token_validation_enabled": true,
  "token_cache_ttl": 600
}
```

## Security Considerations

### 1. Network Security

- Use HTTPS only for API communications
- Implement proper firewall rules
- Use VPN or private networks when possible

### 2. Authentication Security

- Rotate JWT tokens regularly
- Implement token expiration
- Monitor for suspicious authentication patterns

### 3. Input Validation

- The server includes comprehensive input validation
- All queries are sanitized for dangerous patterns
- MongoDB injection protection is enabled

### 4. Rate Limiting

- Configure appropriate rate limits for your use case
- Monitor rate limit violations
- Implement IP-based blocking if needed

### 5. Logging Security

- Don't log sensitive information (tokens, personal data)
- Secure log files with appropriate permissions
- Implement log rotation and retention policies

## Monitoring and Logging

### 1. Application Logs

```bash
# View logs
tail -f /var/log/ambivo-mcp.log

# With Docker
docker logs -f ambivo-mcp-server

# With docker-compose
docker-compose logs -f
```

### 2. Health Monitoring

```bash
# Docker health check
docker inspect ambivo-mcp-server | grep Health

# Kubernetes health
kubectl get pods -l app=ambivo-mcp-server
```

### 3. Metrics Collection

For production deployments, consider integrating with monitoring systems:

- **Prometheus**: For metrics collection
- **Grafana**: For visualization
- **ELK Stack**: For log analysis
- **Jaeger**: For distributed tracing

### 4. Performance Monitoring

Monitor these key metrics:

- Request rate and response time
- Error rates by type
- Memory and CPU usage
- Rate limit violations
- Token validation failures

## MCP Client Configuration

### 1. Claude Code Integration

Add to your MCP settings file:

```json
{
  "mcpServers": {
    "ambivo-api": {
      "command": "ambivo-mcp-server",
      "env": {
        "AMBIVO_BASE_URL": "https://goferapi.ambivo.com",
        "AMBIVO_LOG_LEVEL": "INFO"
      }
    }
  }
}
```

### 2. Custom Client Integration

```python
import asyncio
from mcp.client import create_client

async def main():
    async with create_client("ambivo-mcp-server") as client:
        # Set authentication
        await client.call_tool("set_auth_token", {
            "token": "your-jwt-token"
        })
        
        # Make queries
        result = await client.call_tool("natural_query", {
            "query": "Show me leads from this week",
            "response_format": "both"
        })
        
        print(result)

asyncio.run(main())
```

## Troubleshooting

### Common Issues

1. **"Module not found" errors**
   - Ensure all dependencies are installed
   - Check Python version compatibility (>=3.8)

2. **"Authentication required" errors**
   - Verify JWT token is valid and not expired
   - Check token format (should be proper JWT)

3. **"Rate limit exceeded" errors**
   - Adjust rate limiting configuration
   - Implement request throttling in client

4. **Connection timeout errors**
   - Check network connectivity to Ambivo API
   - Increase timeout configuration
   - Verify base URL is correct

### Debug Mode

Enable debug logging for troubleshooting:

```bash
# Environment variable
export AMBIVO_LOG_LEVEL=DEBUG

# Or in config file
"log_level": "DEBUG"
```

### Support

For issues and support:

- GitHub Issues: https://github.com/ambivo/ambivo-mcp-server/issues
- Documentation: https://github.com/ambivo/ambivo-mcp-server#readme
- Email: dev@ambivo.com

## Production Checklist

Before deploying to production:

- [ ] Update all configuration for production environment
- [ ] Set up proper logging and monitoring
- [ ] Configure appropriate rate limits
- [ ] Test with production-like data volume
- [ ] Set up backup and recovery procedures
- [ ] Document operational procedures
- [ ] Train operations team
- [ ] Set up alerting for critical errors
- [ ] Perform security review
- [ ] Load test the deployment