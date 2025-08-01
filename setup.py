#!/usr/bin/env python3
"""
Setup script for Ambivo MCP Server
"""

from setuptools import setup, find_packages
import os

# Read the README file
current_directory = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(current_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name="ambivo-mcp-server",
    version="1.0.6",
    description="MCP Server for Ambivo API endpoints - Natural language queries and direct entity data access",
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="Ambivo Development Team",
    author_email="info@ambivo.com",
    url="https://github.com/ambivo-corp/ambivo-mcp-server",
    project_urls={
        "Bug Tracker": "https://github.com/ambivo-corp/ambivo-mcp-server/issues",
        "Documentation": "https://github.com/ambivo-corp/ambivo-mcp-server#readme",
        "Source Code": "https://github.com/ambivo-corp/ambivo-mcp-server",
    },
    packages=find_packages(),
    install_requires=[
        "mcp>=1.0.0",
        "httpx>=0.25.0",
        "pyyaml>=6.0.0"
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-asyncio>=0.21.0",
            "black>=22.0.0",
            "isort>=5.0.0",
        ],
        "test": [
            "pytest>=7.0.0", 
            "pytest-asyncio>=0.21.0",
            "httpx[test]>=0.25.0",
        ],
    },
    python_requires=">=3.11",
    entry_points={
        "console_scripts": [
            "ambivo-mcp-server=ambivo_mcp_server:main",
            "ambivo_mcp_server=ambivo_mcp_server:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Communications :: Chat",
        "Framework :: AsyncIO",
    ],
    keywords="mcp server ambivo api natural language query entity data crm",
    include_package_data=True,
    zip_safe=False,
)