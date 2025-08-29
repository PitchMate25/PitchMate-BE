"""FastAPI router to expose MCP tools via REST endpoints.

This router defines endpoints under the `/mcp` prefix that allow
clients to list available tools and invoke specific tools with the
required parameters. These endpoints are intended to be used with
LangChain's MCP adapters or other Model Context Protocol clients.
"""

from typing import Any, Dict
from fastapi import APIRouter, HTTPException
from .mcp_tools import list_tools, web_search, domain_info

router = APIRouter(prefix="/mcp", tags=["mcp"])

@router.get("/tools")
async def get_tools() -> Dict[str, Any]:
    """Return metadata about all available tools."""
    return {"tools": list_tools()}

@router.post("/tools/{tool_name}")
async def call_tool(tool_name: str, payload: Dict[str, Any]) -> Dict[str, Any]:
    """Invoke a specific tool by name with the provided payload."""
    if tool_name == "web_search":
        query = payload.get("query")
        if not query:
            raise HTTPException(status_code=400, detail="Missing 'query' parameter")
        return await web_search(query)
    elif tool_name == "domain_info":
        domain = payload.get("domain")
        if not domain:
            raise HTTPException(status_code=400, detail="Missing 'domain' parameter")
        return await domain_info(domain)
    else:
        raise HTTPException(status_code=404, detail=f"Unknown tool '{tool_name}'")