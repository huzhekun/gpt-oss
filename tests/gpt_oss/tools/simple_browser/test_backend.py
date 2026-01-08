import pytest
from typing import Generator, Any
from unittest import mock
from aiohttp import ClientSession

from gpt_oss.tools.simple_browser.backend import YouComBackend, FirecrawlBackend

class MockAiohttpResponse:
    """Mocks responses for get/post requests from async libraries."""

    def __init__(self, json: dict, status: int):
        self._json = json
        self.status = status

    async def json(self):
        return self._json

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def __aenter__(self):
        return self

def mock_os_environ_get(name: str, default: Any = "test_api_key"):
    assert name in ["YDC_API_KEY", "FIRECRAWL_API_KEY"]
    return default

def test_youcom_backend():
    backend = YouComBackend(source="web")
    assert backend.source == "web"

@pytest.mark.asyncio
@mock.patch("aiohttp.ClientSession.get")
async def test_youcom_backend_search(mock_session_get):
    backend = YouComBackend(source="web")
    api_response = {
        "results": {
            "web": [
                {"title": "Web Result 1", "url": "https://www.example.com/web1", "snippets": "Web Result 1 snippets"},
                {"title": "Web Result 2", "url": "https://www.example.com/web2", "snippets": "Web Result 2 snippets"},
            ],
            "news": [
                {"title": "News Result 1", "url": "https://www.example.com/news1", "description": "News Result 1 description"},
                {"title": "News Result 2", "url": "https://www.example.com/news2", "description": "News Result 2 description"},
            ],
        }
    }
    with mock.patch("os.environ.get", wraps=mock_os_environ_get):
        mock_session_get.return_value = MockAiohttpResponse(api_response, 200)
        async with ClientSession() as session:
            result = await backend.search(query="test", topn=10, session=session)
        assert result.title == "test"
        assert result.urls == {"0": "https://www.example.com/web1", "1": "https://www.example.com/web2", "2": "https://www.example.com/news1", "3": "https://www.example.com/news2"}

@pytest.mark.asyncio
@mock.patch("aiohttp.ClientSession.post")
async def test_youcom_backend_fetch(mock_session_get):
    backend = YouComBackend(source="web")
    api_response = [
        {"title": "Fetch Result 1", "url": "https://www.example.com/fetch1", "html": "<div>Fetch Result 1 text</div>"},
    ]
    with mock.patch("os.environ.get", wraps=mock_os_environ_get):
        mock_session_get.return_value = MockAiohttpResponse(api_response, 200)
        async with ClientSession() as session:
            result = await backend.fetch(url="https://www.example.com/fetch1", session=session)
        assert result.title == "Fetch Result 1"
        assert result.text == "\nURL: https://www.example.com/fetch1\nFetch Result 1 text"


def test_firecrawl_backend():
    backend = FirecrawlBackend(source="web")
    assert backend.source == "web"

def test_firecrawl_backend_custom_base_url():
    # Test with custom base_url
    custom_url = "https://custom.firecrawl.com/v2"
    backend = FirecrawlBackend(source="web", base_url=custom_url)
    assert backend._get_base_url() == custom_url

    # Test with default base_url
    backend_default = FirecrawlBackend(source="web")
    assert backend_default._get_base_url() == "https://api.firecrawl.dev/v2"

    # Test with environment variable
    with mock.patch.dict("os.environ", {"FIRECRAWL_BASE_URL": "https://env.firecrawl.com/v2"}):
        backend_env = FirecrawlBackend(source="web")
        assert backend_env._get_base_url() == "https://env.firecrawl.com/v2"

@pytest.mark.asyncio
@mock.patch("aiohttp.ClientSession.post")
async def test_firecrawl_backend_search(mock_session_post):
    backend = FirecrawlBackend(source="web")
    api_response = {
        "success": True,
        "data": {
            "web": [
                {"title": "Web Result 1", "url": "https://www.example.com/web1", "description": "Web Result 1 description"},
                {"title": "Web Result 2", "url": "https://www.example.com/web2", "description": "Web Result 2 description"},
            ],
            "news": [
                {"title": "News Result 1", "url": "https://www.example.com/news1", "description": "News Result 1 description"},
                {"title": "News Result 2", "url": "https://www.example.com/news2", "description": "News Result 2 description"},
            ],
        }
    }
    with mock.patch("os.environ.get", wraps=mock_os_environ_get):
        mock_session_post.return_value = MockAiohttpResponse(api_response, 200)
        async with ClientSession() as session:
            result = await backend.search(query="test", topn=10, session=session)
        assert result.title == "test"
        assert result.urls == {"0": "https://www.example.com/web1", "1": "https://www.example.com/web2", "2": "https://www.example.com/news1", "3": "https://www.example.com/news2"}

@pytest.mark.asyncio
@mock.patch("aiohttp.ClientSession.post")
async def test_firecrawl_backend_fetch(mock_session_post):
    backend = FirecrawlBackend(source="web")
    api_response = {
        "success": True,
        "data": {
            "html": "<div>Fetch Result 1 text</div>",
            "metadata": {
                "title": "Fetch Result 1"
            }
        }
    }
    with mock.patch("os.environ.get", wraps=mock_os_environ_get):
        mock_session_post.return_value = MockAiohttpResponse(api_response, 200)
        async with ClientSession() as session:
            result = await backend.fetch(url="https://www.example.com/fetch1", session=session)
        assert result.title == "Fetch Result 1"
        assert result.text == "\nURL: https://www.example.com/fetch1\nFetch Result 1 text"


