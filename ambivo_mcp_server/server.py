#!/usr/bin/env python3
"""
MCP Server for Ambivo API Endpoints

This MCP server provides access to Ambivo's entity/natural_query endpoint
through standardized MCP tools. It handles authentication via JWT Bearer tokens with
enhanced security, configuration management, and error handling.
"""

import asyncio
import json
import logging
import os
import time
from typing import Any, Dict, List, Optional

import httpx
from mcp import types
from mcp.server import Server, NotificationOptions
from mcp.server.models import InitializationOptions

# Import from package modules
from .config import load_config, ServerConfig
from .security import RateLimiter, InputValidator, TokenValidator


# Load configuration
try:
    config_path = os.getenv("AMBIVO_CONFIG_FILE")
    config = load_config(config_path)
    logger = config.setup_logging()
except Exception as e:
    # Fallback logging if config fails
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger("ambivo-mcp")
    logger.error(f"Failed to load configuration: {e}")
    # Use default config
    config = ServerConfig()

# Initialize security components
rate_limiter = RateLimiter(
    max_requests=config.rate_limit_requests,
    window_seconds=config.rate_limit_window
)
input_validator = InputValidator(
    max_query_length=config.max_query_length,
    max_payload_size=config.max_payload_size
)
token_validator = TokenValidator(cache_ttl=config.token_cache_ttl)

# Server configuration
server = Server(config.server_name)


class AmbivoAPIClient:
    """Client for interacting with Ambivo API endpoints with enhanced error handling"""
    
    def __init__(self, config: ServerConfig, auth_token: Optional[str] = None):
        self.config = config
        self.base_url = config.base_url.rstrip("/")
        self.auth_token = auth_token
        self.client = httpx.AsyncClient(timeout=config.timeout)
        self.logger = logging.getLogger("ambivo-mcp.client")
    
    def set_auth_token(self, token: str):
        """Set the authentication token with validation"""
        try:
            if self.config.token_validation_enabled:
                token_validator.validate_token_format(token)
            self.auth_token = token
            self.logger.info("Authentication token set successfully")
        except ValueError as e:
            self.logger.error(f"Invalid token format: {e}")
            raise
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for API requests"""
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    async def _make_request_with_retry(self, method: str, url: str, **kwargs) -> httpx.Response:
        """Make HTTP request with retry logic"""
        last_exception = None
        
        for attempt in range(self.config.max_retries + 1):
            try:
                response = await self.client.request(method, url, **kwargs)
                return response
            except (httpx.TimeoutException, httpx.ConnectError, httpx.ReadError) as e:
                last_exception = e
                if attempt < self.config.max_retries:
                    wait_time = 2 ** attempt  # Exponential backoff
                    self.logger.warning(f"Request attempt {attempt + 1} failed, retrying in {wait_time}s: {e}")
                    await asyncio.sleep(wait_time)
                else:
                    self.logger.error(f"All {self.config.max_retries + 1} request attempts failed")
                    raise
        
        # This should never be reached, but just in case
        raise last_exception
    
    async def natural_query(self, query: str, response_format: str = "both") -> Dict[str, Any]:
        """
        Execute a natural language query against entity data with validation and error handling
        
        Args:
            query: Natural language query string
            response_format: Response format - "table", "natural", or "both"
        
        Returns:
            API response dictionary
        """
        # Validate inputs
        input_validator.validate_query(query)
        
        if response_format not in ["table", "natural", "both"]:
            raise ValueError("Invalid response_format. Must be 'table', 'natural', or 'both'")
        
        payload = {
            "query": query,
            "response_format": response_format
        }
        
        url = f"{self.base_url}/entity/natural_query"
        
        try:
            self.logger.info(f"Executing natural query: {query[:100]}...")
            start_time = time.time()
            
            response = await self._make_request_with_retry(
                "POST",
                url,
                json=payload,
                headers=self._get_headers()
            )
            
            elapsed_time = time.time() - start_time
            self.logger.info(f"Natural query completed in {elapsed_time:.2f}s")
            
            response.raise_for_status()
            result = response.json()
            
            self.logger.debug(f"API response: {json.dumps(result, indent=2)[:500]}...")
            return result
            
        except httpx.TimeoutException as e:
            self.logger.error(f"Natural query timeout: {e}")
            raise Exception(f"Request timeout after {self.config.timeout}s")
        except httpx.HTTPStatusError as e:
            self.logger.error(f"Natural query HTTP error: {e.response.status_code} - {e.response.text}")
            raise
        except Exception as e:
            self.logger.error(f"Natural query unexpected error: {e}")
            raise
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()


# Global client instance
api_client = AmbivoAPIClient(config, auth_token=config.auth_token)


@server.list_tools()
async def handle_list_tools() -> List[types.Tool]:
    """
    List available tools.
    """
    return [
        types.Tool(
            name="natural_query",
            description="Execute natural language queries against Ambivo entity data. "
                       "This tool processes natural language queries and returns structured data "
                       "about leads, contacts, opportunities, and other entities.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Natural language query describing what data you want to retrieve. "
                                     "Examples: 'Show me leads created this week', 'Find contacts with gmail addresses', "
                                     "'List opportunities worth more than $10,000'"
                    },
                    "response_format": {
                        "type": "string",
                        "enum": ["table", "natural", "both"],
                        "default": "both",
                        "description": "Format of the response: 'table' for structured data, "
                                     "'natural' for natural language description, 'both' for both formats"
                    }
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="set_auth_token",
            description="Set the authentication token for API requests. "
                       "This must be called before using other tools to authenticate with the Ambivo API.",
            inputSchema={
                "type": "object",
                "properties": {
                    "token": {
                        "type": "string",
                        "description": "JWT Bearer token for authentication with Ambivo API"
                    }
                },
                "required": ["token"]
            }
        )
    ]


@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any] | None) -> List[types.TextContent]:
    """
    Handle tool calls with security and rate limiting.
    """
    if arguments is None:
        arguments = {}
    
    start_time = time.time()
    logger.info(f"Tool call started: {name}")
    
    try:
        # Rate limiting (except for auth token setting)
        if name != "set_auth_token" and api_client.auth_token:
            client_id = token_validator.get_client_id_from_token(api_client.auth_token)
            if not rate_limiter.is_allowed(client_id):
                stats = rate_limiter.get_client_stats(client_id)
                return [types.TextContent(
                    type="text",
                    text=f"Rate limit exceeded. Requests: {stats['requests']}/{config.rate_limit_requests}. "
                         f"Reset in {stats['reset_time'] - time.time():.0f}s"
                )]
        
        if name == "set_auth_token":
            token = arguments.get("token")
            if not token:
                return [types.TextContent(
                    type="text",
                    text="Error: Authentication token is required"
                )]
            
            # Validate and set token
            api_client.set_auth_token(token)
            
            # Cache the token if validation is enabled
            if config.token_validation_enabled:
                token_validator.cache_token(token)
            
            return [types.TextContent(
                type="text",
                text="Authentication token set successfully. You can now use other tools to query the Ambivo API."
            )]
        
        elif name == "natural_query":
            if not api_client.auth_token:
                return [types.TextContent(
                    type="text",
                    text="Error: Authentication required. Please use the 'set_auth_token' tool first."
                )]
            
            query = arguments.get("query")
            if not query:
                return [types.TextContent(
                    type="text",
                    text="Error: Query parameter is required"
                )]
            
            response_format = arguments.get("response_format", "both")
            
            try:
                result = await api_client.natural_query(query, response_format)
                return [types.TextContent(
                    type="text",
                    text=f"Natural Query Results:\n\n{json.dumps(result, indent=2)}"
                )]
            except httpx.HTTPStatusError as e:
                error_msg = f"HTTP {e.response.status_code}: {e.response.text}"
                return [types.TextContent(
                    type="text",
                    text=f"API Error: {error_msg}"
                )]
            except Exception as e:
                return [types.TextContent(
                    type="text",
                    text=f"Error executing natural query: {str(e)}"
                )]
        
        else:
            return [types.TextContent(
                type="text",
                text=f"Unknown tool: {name}"
            )]
    
    except ValueError as e:
        # Input validation errors
        logger.warning(f"Validation error in tool {name}: {e}")
        return [types.TextContent(
            type="text",
            text=f"Validation Error: {str(e)}"
        )]
    
    except httpx.HTTPStatusError as e:
        # HTTP errors from API
        logger.error(f"HTTP error in tool {name}: {e.response.status_code}")
        error_msg = f"API Error (HTTP {e.response.status_code})"
        try:
            error_detail = e.response.json()
            if "error_code" in error_detail:
                error_msg += f": {error_detail['error_code']}"
        except:
            error_msg += f": {e.response.text[:200]}"
        
        return [types.TextContent(
            type="text",
            text=error_msg
        )]
    
    except Exception as e:
        # Unexpected errors
        logger.exception(f"Unexpected error in tool {name}")
        return [types.TextContent(
            type="text",
            text=f"Unexpected error: {str(e)}"
        )]
    
    finally:
        elapsed_time = time.time() - start_time
        logger.info(f"Tool call completed: {name} in {elapsed_time:.2f}s")


async def main():
    """Main entry point for the MCP server with enhanced initialization"""
    logger.info(f"Starting {config.server_name} v{config.server_version}")
    logger.info(f"Configuration: Base URL: {config.base_url}")
    logger.info(f"Security: Rate limit: {config.rate_limit_requests}/{config.rate_limit_window}s")
    
    # Import here to avoid issues with event loops
    import mcp.server.stdio
    
    try:
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                InitializationOptions(
                    server_name=config.server_name,
                    server_version=config.server_version,
                    capabilities=server.get_capabilities(
                        notification_options=NotificationOptions(),
                        experimental_capabilities={},
                    ),
                ),
            )
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
    finally:
        # Cleanup
        await api_client.close()
        logger.info("Server shutdown complete")


def run_server():
    """Synchronous wrapper for the async main function"""
    import asyncio
    asyncio.run(main())


if __name__ == "__main__":
    run_server()