#!/usr/bin/env python3
"""
FastAPI-based GPT Actions Server - Proper async implementation
"""

import json
import logging
import os
import sys
from datetime import datetime, UTC
from typing import Dict, Any, Optional

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel

# Version timestamp - automatically updated on git push
VERSION_TIMESTAMP = "2025-07-31T02:50:00Z"

# Add parent directory to path to import MCP server
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from ambivo_mcp_server.server import handle_list_tools, handle_call_tool, api_client


# Pydantic models
class QueryRequest(BaseModel):
    query: str
    response_format: str = "both"


class ToolRequest(BaseModel):
    name: str
    arguments: Dict[str, Any] = {}


# Create FastAPI app
app = FastAPI(
    title="Ambivo CRM API",
    description="API for accessing and querying Ambivo CRM data using natural language and direct tool calls",
    version="1.0.0",
    servers=[
        {"url": "https://gpt.ambivo.com", "description": "Production server"},
        {"url": "http://localhost:8080", "description": "Local development"}
    ]
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Auth dependency
async def get_auth_token(authorization: Optional[str] = Header(None)) -> str:
    """Extract and validate auth token from Authorization header"""
    if not authorization:
        raise HTTPException(status_code=401, detail="Authorization header required")
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Bearer token required")
    
    token = authorization[7:]  # Remove "Bearer " prefix
    if not token:
        raise HTTPException(status_code=401, detail="Token cannot be empty")
    
    return token


# Routes
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        tools = await handle_list_tools()
        tool_names = [tool.name for tool in tools]
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(UTC).isoformat(),
            "available_tools": tool_names,
            "server_type": "gpt_actions_fastapi",
            "version": VERSION_TIMESTAMP,
            "deployment_info": {
                "version_timestamp": VERSION_TIMESTAMP,
                "build_time": datetime.now(UTC).isoformat()
            }
        }
    except Exception as e:
        logging.error(f"Health check error: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")


@app.get("/openapi.json")
async def get_openapi_schema():
    """Get OpenAPI schema - FastAPI generates this automatically"""
    return app.openapi()


@app.post("/query")
async def natural_language_query(
    request: QueryRequest,
    token: str = Depends(get_auth_token)
):
    """Execute natural language query"""
    try:
        # Set auth token for this request
        original_token = api_client.auth_token
        api_client.set_auth_token(token)
        
        try:
            # Call the MCP tool directly (no event loop issues!)
            result = await handle_call_tool('natural_query', {
                'query': request.query,
                'response_format': request.response_format
            })
            
            # Format response
            response_text = ""
            for content in result:
                response_text += content.text + "\n"
            
            return {
                "query": request.query,
                "result": response_text.strip(),
                "response_format": request.response_format,
                "timestamp": datetime.now(UTC).isoformat(),
                "success": True
            }
            
        finally:
            # Restore original token
            if original_token:
                api_client.auth_token = original_token
            else:
                api_client.auth_token = None
                
    except Exception as e:
        logging.error(f"Natural query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tools")
async def list_tools(token: str = Depends(get_auth_token)):
    """List available tools"""
    try:
        # Set auth token for this request
        original_token = api_client.auth_token
        api_client.set_auth_token(token)
        
        try:
            mcp_tools = await handle_list_tools()
            
            # Convert to OpenAI function calling format
            tools = []
            for tool in mcp_tools:
                tool_def = {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                }
                tools.append(tool_def)
            
            return {
                "tools": tools,
                "server_info": {
                    "name": "ambivo-gpt-actions-fastapi",
                    "version": VERSION_TIMESTAMP,
                    "capabilities": ["natural_language_queries", "crm_data_access"]
                }
            }
            
        finally:
            # Restore original token
            if original_token:
                api_client.auth_token = original_token
            else:
                api_client.auth_token = None
                
    except Exception as e:
        logging.error(f"List tools error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/tools")
async def execute_tool(
    request: ToolRequest,
    token: str = Depends(get_auth_token)
):
    """Execute a specific tool"""
    try:
        # Set auth token for this request
        original_token = api_client.auth_token
        api_client.set_auth_token(token)
        
        try:
            # Call the MCP tool directly
            result = await handle_call_tool(request.name, request.arguments)
            
            # Format response
            response_text = ""
            for content in result:
                response_text += content.text + "\n"
            
            return {
                "result": response_text.strip(),
                "tool_name": request.name,
                "success": True
            }
            
        finally:
            # Restore original token
            if original_token:
                api_client.auth_token = original_token
            else:
                api_client.auth_token = None
                
    except Exception as e:
        logging.error(f"Tool execution error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/debug")
async def debug_info():
    """Debug endpoint"""
    return {
        "message": "FastAPI server working",
        "version": VERSION_TIMESTAMP,
        "timestamp": datetime.now(UTC).isoformat(),
        "endpoints": {
            "health": "/health",
            "openapi": "/openapi.json", 
            "query": "/query",
            "tools": "/tools"
        }
    }


# For running with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)