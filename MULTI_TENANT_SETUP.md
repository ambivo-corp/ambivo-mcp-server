# Multi-Tenant GPT Actions Setup

This guide explains how the multi-tenant authentication works for the Ambivo GPT Actions server.

## How It Works

1. **No Environment Token Required**: The server no longer requires `AMBIVO_AUTH_TOKEN` to be set as an environment variable.

2. **User-Provided Tokens**: Each ChatGPT user provides their own Ambivo JWT token through the GPT's authentication settings.

3. **Per-Request Authentication**: The server extracts the token from the `Authorization: Bearer <token>` header on each request and uses it to authenticate with the Ambivo API.

4. **Data Isolation**: Each user only sees their own CRM data based on their JWT token.

## Setup Instructions

### For Server Administrators

1. **Deploy the server** without setting `AMBIVO_AUTH_TOKEN`:
   ```bash
   # Local development
   ambivo-gpt-actions serve
   
   # Production deployment
   ambivo-gpt-actions serve --host 0.0.0.0 --port $PORT
   ```

2. **Share the OpenAPI URL** with your users:
   ```
   https://your-deployment.railway.app/openapi.yaml
   ```

### For ChatGPT Users

1. **Create a Custom GPT** in ChatGPT
2. **Add the Action** using the provided OpenAPI URL
3. **Configure Authentication**:
   - Type: API Key
   - Auth Type: Bearer
   - API Key: Your personal Ambivo JWT token

## Security Considerations

- **Token Validation**: The server validates token format but doesn't verify signatures (relies on Ambivo API for final validation)
- **HTTPS Required**: Always use HTTPS in production to protect tokens in transit
- **Token Scope**: Users should use tokens with appropriate scopes for CRM access
- **No Token Storage**: The server doesn't store any tokens - they're only used for the duration of each request

## Testing Multi-Tenant Setup

Use the provided test script to verify multi-tenant functionality:

```bash
python test_multi_tenant.py
```

Replace the test tokens in the script with actual JWT tokens from different users to verify data isolation.

## Benefits

1. **Simplified Deployment**: One server instance can serve multiple users
2. **Better Security**: Users manage their own tokens
3. **Easy Scaling**: No need for per-user deployments
4. **Cost Effective**: Single deployment serves all users

## Troubleshooting

### "Authentication failed" errors
- Verify the JWT token is valid and not expired
- Check token format (should start with 'eyJ')
- Ensure token has required CRM access scopes

### Users seeing wrong data
- This should not happen with proper token isolation
- Verify each user is using their own token
- Check server logs for token confusion

### Performance issues
- The server sets/unsets tokens per request
- Consider connection pooling for high traffic
- Monitor server resources