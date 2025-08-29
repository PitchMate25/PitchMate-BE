"""
TourAPI 호출 클라이언트.

이 모듈은 한국관광공사에서 제공하는 TourAPI를 호출하는 함수들을 정의합니다.
비동기 httpx 클라이언트를 사용하고, 재시도 로직을 적용하여 안정적으로 데이터를
조회할 수 있도록 구현되어 있습니다.
"""

from typing import Any, Dict, Optional
from os import getenv
from urllib.parse import quote
import httpx
from tenacity import retry, stop_after_attempt, wait_exponential

TOUR_API_BASE = getenv("TOUR_API_BASE", "https://apis.data.go.kr/B551011/KorService1")
TOUR_API_KEY = getenv("TOUR_API_KEY")

def _auth_params() -> Dict[str, str]:
    """인증 파라미터를 반환한다.

    TourAPI는 serviceKey를 쿼리 파라미터로 전달해야 한다. URL 인코딩하여 반환한다.
    """
    return {
        "serviceKey": quote(TOUR_API_KEY or "", safe=""),
        "_type": "json",
    }

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=4))
async def search_keyword(
    keyword: str,
    content_type_id: Optional[int] = None,
    area_code: Optional[int] = None,
    sigungu_code: Optional[int] = None,
    page: int = 1,
    size: int = 20,
) -> Dict[str, Any]:
    """키워드 기반으로 관광 정보를 검색한다."""
    params: Dict[str, Any] = {
        **_auth_params(),
        "MobileOS": "ETC",
        "MobileApp": "PitchMate",
        "keyword": keyword,
        "pageNo": page,
        "numOfRows": size,
        "listYN": "Y",
        "arrange": "P",
    }
    if content_type_id is not None:
        params["contentTypeId"] = content_type_id
    if area_code:
        params["areaCode"] = area_code
    if sigungu_code:
        params["sigunguCode"] = sigungu_code
    url = f"{TOUR_API_BASE}/searchKeyword1"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=4))
async def area_based_list(
    content_type_id: Optional[int] = None,
    area_code: Optional[int] = None,
    sigungu_code: Optional[int] = None,
    page: int = 1,
    size: int = 20,
) -> Dict[str, Any]:
    """지역 기반으로 관광 정보를 검색한다."""
    params: Dict[str, Any] = {
        **_auth_params(),
        "MobileOS": "ETC",
        "MobileApp": "PitchMate",
        "pageNo": page,
        "numOfRows": size,
        "listYN": "Y",
        "arrange": "P",
    }
    if content_type_id is not None:
        params["contentTypeId"] = content_type_id
    if area_code:
        params["areaCode"] = area_code
    if sigungu_code:
        params["sigunguCode"] = sigungu_code
    url = f"{TOUR_API_BASE}/areaBasedList1"
    async with httpx.AsyncClient(timeout=10) as client:
        resp = await client.get(url, params=params)
        resp.raise_for_status()
        return resp.json()