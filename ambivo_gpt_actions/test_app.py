#!/usr/bin/env python3
"""Simple test GPT Actions app with /ping endpoint"""

from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn
import argparse
import sys


class PingResponse(BaseModel):
    message: str
    timestamp: str
    date: str
    time: str


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
async def ping_post():
    """POST version of ping endpoint"""
    return await ping()


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