# MCP Servers for gpt-oss reference tools

This directory contains MCP servers for the reference tools in the [gpt-oss](https://github.com/openai/gpt-oss) repository.
You can set up these tools behind MCP servers and use them in your applications.
For inference service that integrates with MCP, you can also use these as reference tools.

In particular, this directory contains a `build-system-prompt.py` script that will generate exactly the same system prompt as `reference-system-prompt.py`.
The build system prompt script show case all the care needed to automatically discover the tools and construct the system prompt before feeding it into Harmony.

## Usage

### Local Development

```bash
# Install the dependencies
uv pip install -r requirements.txt
```

```bash
# Assume we have harmony and gpt-oss installed
uv pip install mcp[cli] uvicorn
# start the servers
python -m uvicorn browser_server:app --host 0.0.0.0 --port 8001
python -m uvicorn python_server:app --host 0.0.0.0 --port 8000
```

You can now use MCP inspector to play with the tools.
Once opened, connect to `http://localhost:8001` and `http://localhost:8000` respectively.

To compare the system prompt and see how to construct it via MCP service discovery, see `build-system-prompt.py`.
This script will generate exactly the same system prompt as `reference-system-prompt.py`.

## Docker Deployment

### Browser Server Docker Container

For production deployments, you can use Docker to run the MCP browser server as a standalone container.

#### Quick Start with Docker Compose

```bash
# 1. Copy the environment template
cp .env.example .env

# 2. Edit .env with your API keys
# BROWSER_BACKEND=exa  # or "youcom" or "firecrawl"
# EXA_API_KEY=your_api_key_here
# FIRECRAWL_API_KEY=your_api_key_here
# FIRECRAWL_BASE_URL=https://api.firecrawl.dev/v2  # optional, for custom/self-hosted instances

# 3. Build and start the server
docker-compose up -d

# 4. Check logs
docker-compose logs -f

# 5. Stop the server
docker-compose down
```

#### Manual Docker Build

```bash
# Build from the gpt-oss root directory
cd /path/to/gpt-oss
docker build -f gpt-oss-mcp-server/Dockerfile -t gpt-oss-mcp-browser:latest .

# Run the container
docker run -d \
  --name gpt-oss-mcp-browser \
  -p 8001:8001 \
  -e BROWSER_BACKEND=exa \
  -e EXA_API_KEY=your_api_key_here \
  gpt-oss-mcp-browser:latest
```

### Features

The Docker container provides:

- **Web Search**: Search using Exa, You.com, or Firecrawl backends
- **Page Reading**: Open and read web pages with smart content extraction
- **Pattern Finding**: Search for patterns within loaded pages
- **Session Management**: Per-client browser state with page history
- **Citation Support**: Proper citation formatting for source attribution
- **Streamable HTTP**: Bidirectional HTTP streaming for real-time responses
- **Health Checks**: Built-in health monitoring

### Available Tools

The MCP server exposes three tools:

1. **search**: Search for information with configurable result count
2. **open**: Open links or navigate pages with viewport control
3. **find**: Search for patterns within loaded pages

### Configuration

Set these environment variables in your `.env` file:

```bash
# Backend selection: "exa", "youcom", or "firecrawl"
BROWSER_BACKEND=exa

# Exa API Key (get from https://exa.ai)
EXA_API_KEY=your_exa_api_key_here

# You.com API Key (get from https://api.you.com)
YDC_API_KEY=your_youcom_api_key_here

# Firecrawl API Key (get from https://firecrawl.dev)
FIRECRAWL_API_KEY=your_firecrawl_api_key_here

# Firecrawl Base URL (optional, defaults to https://api.firecrawl.dev/v2)
# FIRECRAWL_BASE_URL=https://api.firecrawl.dev/v2
```

### Server Endpoints

- **MCP HTTP Endpoint**: `http://localhost:8001`
- **Health Check**: `http://localhost:8001/health`

### Connecting Clients

```python
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

async with streamablehttp_client("http://localhost:8001") as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        result = await session.call_tool("search", {"query": "AI news"})
```

For detailed documentation on Docker deployment, configuration options, troubleshooting, and architecture, see the inline comments in the Docker files or run the container and check the logs.
