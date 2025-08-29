"""MCP tool implementations for web search and domain info.

This module defines async functions to call external APIs for web search and
domain registration information (WHOIS). It also exposes metadata about
available tools so that they can be registered with an MCP server or
LangChain agent.

Note: These implementations use external services (Google Custom Search
JSON API and a WHOIS API). You must set the corresponding API keys
(`CUSTOM_SEARCH_API_KEY`, `CUSTOM_SEARCH_ENGINE_ID`, `WHOIS_API_KEY`) in
your environment or `.env` file.
"""

from typing import Any, Dict, List
from os import getenv
import httpx

CUSTOM_SEARCH_API_KEY = getenv("CUSTOM_SEARCH_API_KEY")
CUSTOM_SEARCH_ENGINE_ID = getenv("CUSTOM_SEARCH_ENGINE_ID")
WHOIS_API_KEY = getenv("WHOIS_API_KEY")

async def web_search(query: str) -> Dict[str, Any]:
    """Perform a web search using Google Custom Search JSON API."""
    if not CUSTOM_SEARCH_API_KEY or not CUSTOM_SEARCH_ENGINE_ID:
        raise ValueError("CUSTOM_SEARCH_API_KEY and CUSTOM_SEARCH_ENGINE_ID must be set to use web_search")
    url = "https://customsearch.googleapis.com/customsearch/v1"
    params = {"key": CUSTOM_SEARCH_API_KEY, "cx": CUSTOM_SEARCH_ENGINE_ID, "q": query, "num": 5}
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

async def domain_info(domain: str) -> Dict[str, Any]:
    """Retrieve WHOIS information for a domain."""
    if not WHOIS_API_KEY:
        raise ValueError("WHOIS_API_KEY must be set to use domain_info")
    url = f"https://api.api-ninjas.com/v1/whois?domain={domain}"
    headers = {"X-Api-Key": WHOIS_API_KEY}
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, headers=headers)
        resp.raise_for_status()
        return resp.json()

def list_tools() -> List[Dict[str, Any]]:
    """Return metadata for available tools."""
    return [
        {
            "name": "web_search",
            "description": "Perform web search using the Google Custom Search JSON API",
            "params": {
                "query": {"type": "string", "description": "Search query text"}
            },
        },
        {
            "name": "domain_info",
            "description": "Retrieve WHOIS registration information for a domain",
            "params": {
                "domain": {"type": "string", "description": "Domain name to look up"}
            },
        },
    ]