"""
FastAPI 라우터: AI 에이전트

이 라우터는 MCP 기반 LangChain 에이전트를 FastAPI 엔드포인트로 노출합니다.
사용자는 `POST /agent/ask` 경로로 JSON {"query": "..."}를 보내면
에이전트가 OpenAI LLM과 MCP 툴을 이용해 답변을 생성합니다.
"""

from fastapi import APIRouter, HTTPException
from typing import Any, Dict
from .agent import create_agent

router = APIRouter(prefix="/agent", tags=["agent"])
_agent: Any | None = None

@router.on_event("startup")
async def on_startup() -> None:
    """앱 시작 시 에이전트 생성."""
    global _agent
    _agent = create_agent()

@router.post("/ask")
async def ask_agent(payload: Dict[str, Any]) -> Dict[str, Any]:
    """사용자의 질문을 받아 에이전트의 응답을 반환한다."""
    global _agent
    if _agent is None:
        raise HTTPException(status_code=500, detail="에이전트가 아직 초기화되지 않았습니다.")
    query = payload.get("query")
    if not query:
        raise HTTPException(status_code=400, detail="query 파라미터는 필수입니다.")
    response = await _agent.arun(query)
    return {"response": response}