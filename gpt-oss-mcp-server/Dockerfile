# Multi-stage build for gpt-oss MCP Browser Server
# NOTE: Build this from the gpt-oss root directory, not from gpt-oss-mcp-server/
# Example: docker build -f gpt-oss-mcp-server/Dockerfile -t gpt-oss-mcp-browser:latest .

FROM python:3.12-slim as builder

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /build

# Copy the main gpt-oss package from root
COPY pyproject.toml README.md /build/gpt-oss/
COPY gpt_oss /build/gpt-oss/gpt_oss/
COPY _build /build/gpt-oss/_build/
COPY MANIFEST.in /build/gpt-oss/

# Install gpt-oss package
RUN cd /build/gpt-oss && pip install --no-cache-dir .

# Copy MCP server files
COPY gpt-oss-mcp-server/pyproject.toml /build/mcp-server/
COPY gpt-oss-mcp-server/browser_server.py /build/mcp-server/

# Install MCP server dependencies
RUN cd /build/mcp-server && pip install --no-cache-dir .

# Final stage
FROM python:3.12-slim

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY gpt-oss-mcp-server/browser_server.py /app/

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV BROWSER_BACKEND=exa

# Expose MCP server port
EXPOSE 8001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8001/health').read()" || exit 1

# Run the MCP server
CMD ["python", "-m", "mcp.server.fastmcp", "browser_server:mcp"]
