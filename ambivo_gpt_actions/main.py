#!/usr/bin/env python3
"""Simple test GPT Actions app with /ping endpoint"""

from datetime import datetime
from fastapi import FastAPI, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import uvicorn
import os
print(f"🧪 Starting main.py, PORT={os.environ.get('PORT')}")

class PingResponse(BaseModel):
    message: str
    timestamp: str
    date: str
    time: str

class QueryRequest(BaseModel):
    query: str
    response_format: str = "natural"

app = FastAPI(
    title="Ambivo Test GPT Actions",
    description="Simple test API for GPT Actions",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://chat.openai.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Ambivo Test GPT Actions API",
        "endpoints": ["/ping", "/docs", "/openapi.json"]
    }

@app.get("/ping", response_model=PingResponse)
async def ping():
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
    now = datetime.now()
    if authorization:
        print(f"Received auth header: {authorization[:20]}...")
    if request:
        print(f"Received query: {request.query}")
    return PingResponse(
        message="Pong! Server is alive (with auth)" if authorization else "Pong! Server is alive",
        timestamp=now.isoformat(),
        date=now.strftime("%Y-%m-%d"),
        time=now.strftime("%H:%M:%S")
    )

if __name__ == "__main__":


    port = int(os.environ.get("PORT", 8080))
    print(f"🚀 Starting Uvicorn on 0.0.0.0:{port}")
    uvicorn.run("ambivo_gpt_actions.main:app", host="0.0.0.0", port=port)

