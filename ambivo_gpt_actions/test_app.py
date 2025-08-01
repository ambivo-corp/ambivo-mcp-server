#!/usr/bin/env python3
"""Simple test GPT Actions app with /ping endpoint"""

from datetime import datetime
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import argparse
import sys


class PingResponse(BaseModel):
    message: str
    timestamp: str
    date: str
    time: str


class QueryRequest(BaseModel):
    query: str
    response_format: str = "natural"


class QueryResponse(BaseModel):
    message: str
    query: str
    auth_received: bool
    timestamp: str


app = FastAPI(
    title="Ambivo Test GPT Actions",
    description="Simple test API for GPT Actions",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chat.openai.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Ambivo Test GPT Actions API",
        "endpoints": ["/ping", "/docs", "/openapi.json"]
    }


@app.get("/ping", response_model=PingResponse)
async def ping():
    """Simple ping endpoint that returns current date and time"""
    now = datetime.now()
    return PingResponse(
        message="Pong! Server is alive",
        timestamp=now.isoformat(),
        date=now.strftime("%Y-%m-%d"),
        time=now.strftime("%H:%M:%S")
    )


@app.post("/ping", response_model=PingResponse)
async def ping_post(
    request: Optional[QueryRequest] = None,
    authorization: Optional[str] = Header(None)
):
    """POST version of ping endpoint that can accept auth header and body"""
    now = datetime.now()
    
    # Log if we received auth header
    if authorization:
        print(f"Received auth header: {authorization[:20]}...")
    
    # Log if we received request body
    if request:
        print(f"Received query: {request.query}")
        
    return PingResponse(
        message="Pong! Server is alive (with auth)" if authorization else "Pong! Server is alive",
        timestamp=now.isoformat(),
        date=now.strftime("%Y-%m-%d"),
        time=now.strftime("%H:%M:%S")
    )


def main():
    parser = argparse.ArgumentParser(description="Simple test GPT Actions server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    
    args = parser.parse_args()
    
    print(f"Starting test server on {args.host}:{args.port}")
    print(f"Access the API at http://{args.host}:{args.port}")
    print(f"Access the docs at http://{args.host}:{args.port}/docs")
    
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()