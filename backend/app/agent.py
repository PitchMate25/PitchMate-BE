"""
LangChain 에이전트 정의 모듈.

이 모듈은 OpenAI LLM과 MCP 서버를 통합하여 LangChain 기반 에이전트를 생성합니다.
에이전트는 MCP 서버가 제공하는 툴을 통해 웹 검색 및 도메인 정보 조회를 수행할 수 있습니다.
"""

from __future__ import annotations
from os import getenv
from typing import List, Any
from langchain import OpenAI
from langchain.agents import initialize_agent
from langchain_mcp.adapters import MCPToolSet

def create_agent() -> Any:
    """OpenAI 기반 LangChain 에이전트를 생성합니다."""
    openai_api_key = getenv("OPENAI_API_KEY")
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY가 설정되어 있지 않습니다. .env 파일에 키를 추가하세요.")
    mcp_server_url = getenv("MCP_SERVER_URL", "http://localhost:8000/mcp")
    llm = OpenAI(temperature=0, openai_api_key=openai_api_key)
    toolset = MCPToolSet(server_url=mcp_server_url)
    tools: List[Any] = toolset.get_tools()
    agent = initialize_agent(tools=tools, llm=llm, agent_type="zero-shot-react-description", verbose=True)
    return agent

__all__ = ["create_agent"]