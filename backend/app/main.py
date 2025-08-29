from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from os import getenv
from typing import List

from .config import settings
from .database import engine, Base
from .auth import router as auth_router
from .security import get_current_user_claims
from .mcp_router import router as mcp_router
from .agent_router import router as agent_router
from .routers.external import router as external_router

app = FastAPI(title="PitchMate API", version="0.1.0")

app.add_middleware(SessionMiddleware, secret_key=getenv("SECRET_KEY", "dev"))

# (개발 편의) CORS 전체 허용 — 실서비스 시 도메인 제한하세요.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
# 외부 툴(MCP), AI 에이전트, 여행/레저 외부 API 라우터 등록
app.include_router(mcp_router)
app.include_router(agent_router)
app.include_router(external_router)

@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.ENV}

@app.get("/me")
def me(claims: dict = Depends(get_current_user_claims)):
    return {"ok": True, "claims": claims}

@app.post("/logout")
def logout():
    from fastapi import Response
    resp = Response(status_code=204)
    resp.delete_cookie("access_token")
    return resp