"""
GoCamping API 호출 클라이언트.

이 모듈은 공공데이터포털에서 제공하는 GoCamping API를 호출하여 캠핑장 정보를
검색, 위치 기반으로 조회하는 함수를 정의합니다.
"""

from typing import Any, Dict
from os import getenv
from urllib.parse import quote
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

BASE = getenv("GOCAMP_API_BASE", "https://apis.data.go.kr/B551011/GoCamping")
API_KEY = getenv("GOCAMPING_API_KEY")
MOBILE_OS = getenv("MOBILE_OS", "ETC")
MOBILE_APP = getenv("MOBILE_APP", "PitchMate")

def _common() -> Dict[str, str]:
    """공통 파라미터를 반환한다."""
    return {
        "serviceKey": quote(API_KEY or "", safe=""),
        "MobileOS": MOBILE_OS,
        "MobileApp": MOBILE_APP,
        "_type": "json",
    }

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=4))
async def based_list(page: int = 1, size: int = 20) -> Dict[str, Any]:
    """기본 캠핑장 목록을 조회한다."""
    params = {**_common(), "pageNo": page, "numOfRows": size}
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{BASE}/basedList", params=params)
        resp.raise_for_status()
        return resp.json()

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=4))
async def search_list(keyword: str, page: int = 1, size: int = 20) -> Dict[str, Any]:
    """키워드로 캠핑장을 검색한다."""
    params = {**_common(), "pageNo": page, "numOfRows": size, "keyword": keyword}
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{BASE}/searchList", params=params)
        resp.raise_for_status()
        return resp.json()

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=4))
async def location_based_list(
    map_x: float,
    map_y: float,
    radius_km: int = 10,
    page: int = 1,
    size: int = 20,
) -> Dict[str, Any]:
    """위치 기반으로 캠핑장을 조회한다."""
    params = {
        **_common(),
        "pageNo": page,
        "numOfRows": size,
        "mapX": map_x,
        "mapY": map_y,
        "radius": radius_km * 1000,
    }
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(f"{BASE}/locationBasedList", params=params)
        resp.raise_for_status()
        return resp.json()