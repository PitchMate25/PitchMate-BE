from .mcp_router import router as mcp_router
from .agent_router import router as agent_router
from .routers.external import router as external_router
from .auth import router as auth_router
from .database import engine, Base
from .security import get_current_user_claims

def create_app() -> FastAPI:
    app = FastAPI(title="AI MCP API", version="0.1.0")
    app.add_middleware(SessionMiddleware, secret_key=getenv("SECRET_KEY", "dev"))
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # MCP tools router
    app.include_router(mcp_router)
    # AI agent router
    app.include_router(agent_router)
    # External API router (TourAPI/GoCamping)
    app.include_router(external_router)
    # Social login router
    app.include_router(auth_router)
    @app.on_event("startup")
    async def on_startup() -> None:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}
    @app.get("/me")
    def me(claims: dict = Depends(get_current_user_claims)) -> dict:
        return {"ok": True, "claims": claims}
    @app.post("/logout")
    def logout() -> Response:
        resp = Response(status_code=204)
        resp.delete_cookie("access_token")
        return resp
    return app