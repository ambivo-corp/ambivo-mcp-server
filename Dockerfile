# Multi-stage build for smaller final image
FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN pip install --no-cache-dir build

# Copy source code
COPY . .

# Build the package
RUN python -m build

# Final stage
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Create non-root user
RUN useradd --create-home --shell /bin/bash mcpuser

# Set working directory
WORKDIR /home/mcpuser

# Copy built package from builder stage
COPY --from=builder /app/dist/*.whl /tmp/

# Install the package
RUN pip install --no-cache-dir /tmp/*.whl && \
    rm /tmp/*.whl

# Switch to non-root user
USER mcpuser

# Expose port (if needed for future HTTP interface)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import server; print('MCP server module imports successfully')" || exit 1

# Default command
CMD ["ambivo-mcp-server"]