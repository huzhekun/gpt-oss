# gpt-oss MCP Browser Server - Docker Deployment Guide

This guide provides comprehensive instructions for deploying the gpt-oss MCP Browser Server as a Docker container.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Available Tools](#available-tools)
- [Deployment Options](#deployment-options)
- [Health Checks](#health-checks)
- [Client Integration](#client-integration)
- [Troubleshooting](#troubleshooting)
- [Architecture](#architecture)
- [Security](#security)
- [Performance](#performance)

## Overview

This Docker container packages the gpt-oss reference implementation of web browsing tools into a standalone, streamable HTTP MCP (Model Context Protocol) server. It provides AI models with the ability to search the web, read pages, and find patterns within content.

## Features

- **Web Search**: Query the web using Exa, You.com, or Firecrawl backends
- **Page Reading**: Open URLs and read content with intelligent extraction
- **Pattern Finding**: Search for text patterns within loaded pages
- **Session Management**: Per-client isolated browser state
- **Citation Tracking**: Precise source attribution with line-level citations
- **Streamable HTTP**: Server-Sent Events (SSE) for real-time streaming
- **Token-Aware**: Automatic truncation to fit context windows
- **Multi-Backend**: Pluggable search providers (Exa, You.com, Firecrawl)
- **Health Monitoring**: Built-in health checks for orchestration
- **Production Ready**: Multi-stage builds, minimal image size

## Prerequisites

### Required

- Docker 20.10+ and Docker Compose 2.0+
- API key from one of:
  - [Exa](https://exa.ai) (recommended for general search)
  - [You.com](https://api.you.com) (good for news and recent content)
  - [Firecrawl](https://firecrawl.dev) (excellent for page scraping and search)

### Optional

- MCP client or SDK for testing
- curl or similar tool for health checks

## Quick Start

### 1. Setup Environment

```bash
cd gpt-oss/gpt-oss-mcp-server

# Copy environment template
cp .env.example .env

# Edit with your preferred editor
nano .env
```

Add your API key to `.env`:

```bash
BROWSER_BACKEND=exa
EXA_API_KEY=your_actual_api_key_here
```

### 2. Deploy with Docker Compose (Recommended)

```bash
# Build and start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f mcp-browser-server

# Check health
curl http://localhost:8001/health

# Stop when done
docker-compose down
```

### 3. Verify Deployment

```bash
# Check container status
docker ps | grep gpt-oss-mcp-browser

# Check health status
docker inspect --format='{{.State.Health.Status}}' gpt-oss-mcp-browser

# Test with MCP inspector or client
# Point your client to: http://localhost:8001
```

## Configuration

### Environment Variables

| Variable | Default | Required | Description |
|----------|---------|----------|-------------|
| `BROWSER_BACKEND` | `exa` | No | Search backend: `exa`, `youcom`, or `firecrawl` |
| `EXA_API_KEY` | - | Yes (for exa) | API key from exa.ai |
| `YDC_API_KEY` | - | Yes (for youcom) | API key from You.com |
| `FIRECRAWL_API_KEY` | - | Yes (for firecrawl) | API key from firecrawl.dev |
| `FIRECRAWL_BASE_URL` | `https://api.firecrawl.dev/v2` | No | Custom Firecrawl API URL (for self-hosted) |

### Backend Selection

**Exa Backend** (Default):
- Strengths: Fast, accurate general search, includes summaries
- Best for: General web searches, research, factual queries
- Setup: Get key from https://exa.ai

**You.com Backend**:
- Strengths: Mixed web/news results, live crawling
- Best for: Recent news, current events, time-sensitive queries
- Setup: Get key from https://api.you.com

**Firecrawl Backend**:
- Strengths: High-quality scraping, structured data extraction, supports self-hosted
- Best for: Detailed page content, custom scraping needs, enterprise deployments
- Setup: Get key from https://firecrawl.dev
- Note: Supports custom base URL for self-hosted instances

To switch backends, update `.env`:

```bash
# Use You.com
BROWSER_BACKEND=youcom
YDC_API_KEY=your_youcom_key_here

# Or use Firecrawl
BROWSER_BACKEND=firecrawl
FIRECRAWL_API_KEY=your_firecrawl_key_here

# Optional: For self-hosted Firecrawl
FIRECRAWL_BASE_URL=https://your-firecrawl-instance.com/v2
```

## Available Tools

The MCP server exposes three tools accessible via the Model Context Protocol.

### 1. search

Search for information on the web.

**Parameters:**

```json
{
  "query": "string (required)",
  "topn": "integer (optional, default: 10)",
  "source": "string (optional)"
}
```

**Example:**

```json
{
  "query": "latest developments in quantum computing 2026",
  "topn": 5
}
```

**Returns:** HTML-formatted search results with clickable links

### 2. open

Open a URL or link from search results.

**Parameters:**

```json
{
  "id": "integer or string (optional, -1 for current page)",
  "cursor": "integer (optional, -1 for latest)",
  "loc": "integer (optional, line number to start from)",
  "num_lines": "integer (optional, lines to display)",
  "view_source": "boolean (optional, default: false)",
  "source": "string (optional)"
}
```

**Examples:**

```json
// Open a direct URL
{
  "id": "https://example.com/article",
  "num_lines": 50
}

// Open link from search results
{
  "id": 3,
  "cursor": 5,
  "loc": 0
}

// Scroll current page
{
  "loc": 100,
  "num_lines": 30
}
```

**Returns:** Processed page content with line numbers and citations

### 3. find

Search for exact text patterns in the current page.

**Parameters:**

```json
{
  "pattern": "string (required)",
  "cursor": "integer (optional, -1 for current)"
}
```

**Example:**

```json
{
  "pattern": "machine learning",
  "cursor": 3
}
```

**Returns:** Matches with context (4 lines per match)

### Citation Format

Results use a special citation format for source attribution:

```
【{cursor}†L{line_start}-L{line_end}】
```

Examples:
- `【6†L9-L11】` - Lines 9-11 from page cursor 6
- `【8†L3】` - Line 3 from page cursor 8

When citing, do not quote more than 10 words directly from the tool output.

## Deployment Options

### Option 1: Docker Compose (Recommended)

Best for: Development, testing, quick deployments

```bash
docker-compose up -d
```

Includes:
- Automatic restart on failure
- Health checks
- Network isolation
- Environment file support

### Option 2: Docker CLI

Best for: Custom orchestration, CI/CD pipelines

```bash
# Build
docker build -f gpt-oss-mcp-server/Dockerfile \
  -t gpt-oss-mcp-browser:latest \
  /path/to/gpt-oss

# Run
docker run -d \
  --name gpt-oss-mcp-browser \
  --restart unless-stopped \
  -p 8001:8001 \
  -e BROWSER_BACKEND=exa \
  -e EXA_API_KEY=your_key \
  gpt-oss-mcp-browser:latest
```

### Option 3: Kubernetes

Best for: Production, high availability, auto-scaling

See `k8s/` directory for example manifests (if available) or create:

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-browser-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-browser
  template:
    metadata:
      labels:
        app: mcp-browser
    spec:
      containers:
      - name: mcp-browser
        image: gpt-oss-mcp-browser:latest
        ports:
        - containerPort: 8001
        env:
        - name: BROWSER_BACKEND
          value: "exa"
        - name: EXA_API_KEY
          valueFrom:
            secretKeyRef:
              name: mcp-secrets
              key: exa-api-key
        livenessProbe:
          httpGet:
            path: /health
            port: 8001
          initialDelaySeconds: 10
          periodSeconds: 30
```

### Option 4: Docker Swarm

Best for: Simpler orchestration than k8s, multi-node

```bash
docker stack deploy -c docker-compose.yml mcp-stack
```

## Health Checks

The container includes automatic health monitoring.

### Check Health Status

```bash
# HTTP endpoint
curl http://localhost:8001/health

# Docker inspect
docker inspect --format='{{.State.Health.Status}}' gpt-oss-mcp-browser

# Docker Compose
docker-compose ps
```

### Health Check Configuration

Defined in Dockerfile and docker-compose.yml:

- **Interval**: 30 seconds
- **Timeout**: 10 seconds
- **Start Period**: 5 seconds
- **Retries**: 3

### Custom Health Checks

For production monitoring, integrate with:
- Prometheus/Grafana
- Datadog
- New Relic
- CloudWatch

## Client Integration

### Python MCP Client

```python
import asyncio
from mcp import ClientSession
from mcp.client.sse import sse_client

async def search_web():
    async with sse_client("http://localhost:8001/sse") as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize
            await session.initialize()

            # Search
            result = await session.call_tool("search", {
                "query": "AI developments 2026",
                "topn": 5
            })
            print(result)

            # Open a URL
            page = await session.call_tool("open", {
                "id": "https://example.com/article"
            })
            print(page)

asyncio.run(search_web())
```

### Claude Desktop Integration

Add to your Claude Desktop MCP settings (`~/Library/Application Support/Claude/claude_desktop_config.json` on macOS):

```json
{
  "mcpServers": {
    "browser": {
      "url": "http://localhost:8001/sse"
    }
  }
}
```

**Note**: The MCP endpoint requires the `/sse` path when connecting over SSE transport.

### Custom Application Integration

```python
import aiohttp
import json

async def call_tool(tool_name, arguments):
    async with aiohttp.ClientSession() as session:
        payload = {
            "jsonrpc": "2.0",
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            },
            "id": 1
        }

        async with session.post(
            "http://localhost:8001/mcp/v1",
            json=payload
        ) as resp:
            return await resp.json()

# Usage
result = await call_tool("search", {"query": "Python tutorials"})
```

## Troubleshooting

### Server Won't Start

**Symptom:** Container exits immediately

**Solutions:**

1. Check logs:
```bash
docker-compose logs mcp-browser-server
docker logs gpt-oss-mcp-browser
```

2. Verify API key:
```bash
docker exec gpt-oss-mcp-browser env | grep API_KEY
```

3. Check port availability:
```bash
netstat -an | grep 8001
lsof -i :8001
```

### Connection Refused

**Symptom:** Cannot connect to `http://localhost:8001`

**Solutions:**

1. Wait for startup (check health):
```bash
docker logs -f gpt-oss-mcp-browser
```

2. Verify container is running:
```bash
docker ps | grep mcp-browser
```

3. Check firewall:
```bash
# Allow port 8001
sudo ufw allow 8001
```

### API Errors

**Symptom:** 401 Unauthorized or 429 Rate Limit

**Solutions:**

1. Verify API key is valid:
   - Log into Exa/You.com dashboard
   - Check key is active and not expired
   - Verify correct key in `.env`

2. Check rate limits:
   - Review your API plan limits
   - Monitor usage in provider dashboard
   - Consider upgrading plan or adding backoff

3. Try alternative backend:
```bash
# In .env - Try You.com
BROWSER_BACKEND=youcom
YDC_API_KEY=your_youcom_key

# Or try Firecrawl
BROWSER_BACKEND=firecrawl
FIRECRAWL_API_KEY=your_firecrawl_key
```

### Search Returns No Results

**Symptom:** Empty or error responses from search

**Solutions:**

1. Verify backend API status:
   - Check Exa/You.com status page
   - Test API directly with curl

2. Check network connectivity:
```bash
# Test Exa
docker exec gpt-oss-mcp-browser curl https://api.exa.ai

# Test Firecrawl
docker exec gpt-oss-mcp-browser curl https://api.firecrawl.dev
```

3. Try different query:
   - Use more specific terms
   - Remove special characters
   - Try broader query

### Memory Issues

**Symptom:** Container OOM killed

**Solutions:**

1. Increase memory limit:
```yaml
# In docker-compose.yml
services:
  mcp-browser-server:
    mem_limit: 2g
```

2. Monitor usage:
```bash
docker stats gpt-oss-mcp-browser
```

### Permission Denied

**Symptom:** Cannot write files or execute

**Solutions:**

1. Check SELinux/AppArmor:
```bash
# Temporarily disable to test
sudo setenforce 0
```

2. Run with specific user:
```bash
docker run --user $(id -u):$(id -g) ...
```

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                     Client Layer                        │
│  (Claude Desktop, MCP Clients, Custom Applications)     │
└─────────────────┬───────────────────────────────────────┘
                  │
                  │ HTTP/SSE (Port 8001)
                  │
┌─────────────────▼───────────────────────────────────────┐
│              FastMCP Server (Container)                  │
│  ┌───────────────────────────────────────────────────┐  │
│  │        Application Context Manager                │  │
│  │  - Session-based browser instances                │  │
│  │  - Isolated state per client                      │  │
│  └───────────────┬───────────────────────────────────┘  │
│                  │                                       │
│  ┌───────────────▼───────────────────────────────────┐  │
│  │         SimpleBrowserTool                         │  │
│  │  - Page history tracking                          │  │
│  │  - Citation normalization                         │  │
│  │  - Token-aware truncation                         │  │
│  │  - URL caching                                    │  │
│  └───────────────┬───────────────────────────────────┘  │
│                  │                                       │
│  ┌───────────────▼───────────────────────────────────┐  │
│  │           Backend Interface                       │  │
│  │  ┌──────────────┐ ┌──────────────┐ ┌──────────┐  │  │
│  │  │ ExaBackend   │ │ YouComBackend│ │Firecrawl │  │  │
│  │  │ - /search    │ │ - /v1/search │ │Backend   │  │  │
│  │  │ - /contents  │ │ - /v1/contents│ │- /search│  │  │
│  │  │              │ │              │ │ - /scrape│  │  │
│  │  └──────┬───────┘ └──────┬───────┘ └────┬─────┘  │  │
│  └─────────┼────────────────┼──────────────┼────────┘  │
└────────────┼────────────────┼──────────────┼────────────┘
             │                │              │
             │                │              │
   ┌─────────▼──────┐ ┌───────▼────────┐ ┌─▼──────────┐
   │   Exa API      │ │  You.com API   │ │Firecrawl   │
   │   (exa.ai)     │ │  (you.com)     │ │API         │
   └────────────────┘ └────────────────┘ └────────────┘
```

### Component Flow

1. **Request Handling**: Client sends MCP tool call via HTTP/SSE
2. **Session Management**: AppContext creates/retrieves browser for client
3. **Tool Execution**: SimpleBrowserTool processes request
4. **Backend Query**: Appropriate backend (Exa/You.com/Firecrawl) fetched
5. **Content Processing**: HTML converted to structured text with citations
6. **Response Streaming**: Results streamed back via SSE

### Container Layers

```
┌─────────────────────────────────────────┐
│  Application Layer (browser_server.py)  │  <-- MCP server
├─────────────────────────────────────────┤
│  gpt-oss Library                        │  <-- Tools & backends
├─────────────────────────────────────────┤
│  Python Dependencies                    │  <-- pip packages
├─────────────────────────────────────────┤
│  Python 3.12 Runtime                    │  <-- Base image
├─────────────────────────────────────────┤
│  Debian Slim                            │  <-- OS
└─────────────────────────────────────────┘
```

### Multi-Stage Build

The Dockerfile uses multi-stage builds for efficiency:

1. **Builder stage**: Installs build dependencies, compiles packages
2. **Runtime stage**: Copies only necessary artifacts, minimal size

## Security

### Best Practices

1. **API Keys**
   - Never commit keys to version control
   - Use `.env` file (gitignored)
   - For production, use secrets management:
     - Docker secrets
     - Kubernetes secrets
     - AWS Secrets Manager
     - HashiCorp Vault

2. **Network Security**
   - Run behind reverse proxy (nginx, Traefik)
   - Enable HTTPS/TLS
   - Use firewall rules to limit access
   - Consider VPN for internal services

3. **Container Security**
   - Run as non-root user (future enhancement)
   - Use read-only filesystem where possible
   - Limit capabilities
   - Scan images for vulnerabilities:
     ```bash
     docker scan gpt-oss-mcp-browser:latest
     ```

4. **Access Control**
   - Implement authentication/authorization
   - Rate limiting per client
   - IP whitelisting for production
   - Audit logging

### Example: Running as Non-Root

```dockerfile
# Add to Dockerfile
RUN useradd -m -u 1000 mcp && \
    chown -R mcp:mcp /app
USER mcp
```

### Example: Read-Only Filesystem

```bash
docker run -d \
  --read-only \
  --tmpfs /tmp \
  --tmpfs /app/cache \
  ...
```

## Performance

### Optimization Tips

1. **Caching**
   - Browser tool includes URL caching
   - Add Redis for distributed caching
   - Configure HTTP cache headers

2. **Connection Pooling**
   - aiohttp uses connection pooling by default
   - Tune pool size for your workload

3. **Resource Limits**
   ```yaml
   # docker-compose.yml
   services:
     mcp-browser-server:
       deploy:
         resources:
           limits:
             cpus: '2'
             memory: 2G
           reservations:
             cpus: '1'
             memory: 1G
   ```

4. **Horizontal Scaling**
   - Run multiple instances behind load balancer
   - Use sticky sessions for client affinity
   - Share state via Redis if needed

5. **Monitoring**
   ```bash
   # Monitor resource usage
   docker stats gpt-oss-mcp-browser

   # Profile with py-spy
   docker exec gpt-oss-mcp-browser \
     py-spy top --pid 1
   ```

### Performance Metrics

Expected performance (single instance):
- **Startup time**: 3-5 seconds
- **Search latency**: 1-3 seconds (network dependent)
- **Page load**: 0.5-2 seconds (size dependent)
- **Memory usage**: 200-500 MB typical
- **Concurrent clients**: 10-50 (CPU dependent)

## License

This project follows the license of the parent gpt-oss repository.

## Support

- **Issues**: Report at [gpt-oss GitHub](https://github.com/openai/gpt-oss/issues)
- **Documentation**: See main [README.md](README.md)
- **Examples**: Check `examples/` directory

## Related Documentation

- [Main README](README.md)
- [MCP Protocol](https://modelcontextprotocol.io)
- [FastMCP](https://github.com/jlowin/fastmcp)
- [gpt-oss Repository](https://github.com/openai/gpt-oss)
