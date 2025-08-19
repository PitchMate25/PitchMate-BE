from fastapi import APIRouter, Request, Depends, HTTPException, Response
from starlette.middleware.sessions import SessionMiddleware
from authlib.integrations.starlette_client import OAuth
from os import getenv
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from .database import get_session
from .models import User
from .security import create_jwt

router = APIRouter(prefix="/auth", tags=["auth"])
oauth = OAuth()

# 프로바이더 등록
oauth.register(
    name="google",
    client_id=getenv("GOOGLE_CLIENT_ID"),
    client_secret=getenv("GOOGLE_CLIENT_SECRET"),
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={"scope": "openid email"},
)

oauth.register(
    name="kakao",
    client_id=getenv("KAKAO_CLIENT_ID"),
    client_secret=getenv("KAKAO_CLIENT_SECRET"),
    authorize_url="https://kauth.kakao.com/oauth/authorize",
    access_token_url="https://kauth.kakao.com/oauth/token",
    api_base_url="https://kapi.kakao.com",
    client_kwargs={"scope": "profile_nickname account_email"},
)

oauth.register(
    name="naver",
    client_id=getenv("NAVER_CLIENT_ID"),
    client_secret=getenv("NAVER_CLIENT_SECRET"),
    authorize_url="https://nid.naver.com/oauth2.0/authorize",
    access_token_url="https://nid.naver.com/oauth2.0/token",
    api_base_url="https://openapi.naver.com",
    client_kwargs={"scope": "name email"},
)

REDIRECT_BASE = getenv("OAUTH_REDIRECT_BASE", "http://localhost:8000")

@router.get("/{provider}/login")
async def login(request: Request, provider: str):
    if provider not in ("google", "kakao", "naver"):
        raise HTTPException(404, "unknown provider")
    callback_url = f"{REDIRECT_BASE}/auth/{provider}/callback"
    client = oauth.create_client(provider)
    return await client.authorize_redirect(request, callback_url)

def normalize_userinfo(provider: str, raw: dict) -> dict:
    """
    프로바이더별 응답을 통일된 스키마로 변환
    returns: {external_id, email, name}
    """
    if provider == "google":
        # OpenID UserInfo 표준
        return {
            "external_id": raw.get("sub"),
            "email": raw.get("email"),
            "name": raw.get("name"),
        }
    if provider == "kakao":
        # https://kapi.kakao.com/v2/user/me
        kakao_account = raw.get("kakao_account", {}) or {}
        profile = kakao_account.get("profile", {}) or {}
        return {
            "external_id": str(raw.get("id")),
            "email": kakao_account.get("email"),
            "name": profile.get("nickname"),
        }
    if provider == "naver":
        # https://openapi.naver.com/v1/nid/me
        res = raw.get("response", {}) or {}
        return {
            "external_id": res.get("id"),
            "email": res.get("email"),
            "name": res.get("name"),
        }
    return {}

@router.get("/{provider}/callback")
async def callback(request: Request, response: Response, provider: str, session: AsyncSession = Depends(get_session)):
    client = oauth.create_client(provider)
    token = await client.authorize_access_token(request)
    # userinfo 호출
    if provider == "google":
        userinfo = await client.parse_id_token(request, token)  # or await client.get('userinfo')
    elif provider == "kakao":
        resp = await client.get("/v2/user/me", token=token)
        userinfo = resp.json()
    else:  # naver
        resp = await client.get("https://openapi.naver.com/v1/nid/me", token=token)
        userinfo = resp.json()

    norm = normalize_userinfo(provider, userinfo)
    if not norm.get("external_id"):
        raise HTTPException(400, "cannot read user info")

    # upsert
    q = select(User).where(User.provider == provider, User.external_id == norm["external_id"])
    result = await session.execute(q)
    user = result.scalar_one_or_none()
    if user:
        user.email = norm.get("email")
        user.name = norm.get("name")
    else:
        user = User(
            provider=provider,
            external_id=norm["external_id"],
            email=norm.get("email"),
            name=norm.get("name"),
        )
        session.add(user)
    await session.commit()

    # 우리 서비스용 JWT 생성
    jwt_token = create_jwt({"sub": f"{provider}:{norm['external_id']}", "provider": provider, "email": norm.get("email")})
    # HttpOnly 쿠키 세팅 (개발환경: secure=False, prod는 True + same-site 조정)
    response.set_cookie("access_token", jwt_token, httponly=True, secure=False, samesite="lax", max_age=60*60)
    # 간단한 리다이렉트 (프론트가 있다면 프론트 주소로)
    response.headers["Location"] = "/me"
    return Response(status_code=302)