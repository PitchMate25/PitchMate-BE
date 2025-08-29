"""
외부 API 라우터.

이 라우터는 TourAPI 및 GoCamping API를 사용하는 엔드포인트를 제공합니다.
세그먼트별로 캠핑, 체험/일반 관광, 스포츠 정보 검색을 지원합니다.
"""

from typing import List, Optional
from fastapi import APIRouter, Query
from ..clients import tour, gocamping
from ..services.normalize import normalize_tour_list, normalize_gocamping_list
from ..schemas.external import Place

router = APIRouter(prefix="/external", tags=["external"])

@router.get("/tour/search", response_model=List[Place])
async def tour_search(
    q: str = Query(..., description="검색 키워드"),
    content_type_id: Optional[int] = Query(None, description="TourAPI contentTypeId"),
    area_code: Optional[int] = None,
    sigungu_code: Optional[int] = None,
    page: int = 1,
    size: int = 20,
) -> List[Place]:
    """TourAPI 키워드 검색 엔드포인트."""
    raw = await tour.search_keyword(q, content_type_id, area_code, sigungu_code, page, size)
    if content_type_id == 28:
        category = "sports"
    elif "체험" in q:
        category = "experience"
    else:
        category = "general"
    return normalize_tour_list(raw, category)

@router.get("/camping/search", response_model=List[Place])
async def camping_search(
    q: str,
    page: int = 1,
    size: int = 20,
) -> List[Place]:
    """GoCamping 키워드 검색 엔드포인트."""
    raw = await gocamping.search_list(q, page, size)
    return normalize_gocamping_list(raw)

@router.get("/camping/nearby", response_model=List[Place])
async def camping_nearby(
    lng: float,
    lat: float,
    radius_km: int = 10,
    page: int = 1,
    size: int = 20,
) -> List[Place]:
    """위치 기반 캠핑장 조회 엔드포인트."""
    raw = await gocamping.location_based_list(map_x=lng, map_y=lat, radius_km=radius_km, page=page, size=size)
    return normalize_gocamping_list(raw)

@router.get("/sports/nearby", response_model=List[Place])
async def sports_nearby(
    area_code: Optional[int] = None,
    sigungu_code: Optional[int] = None,
    page: int = 1,
    size: int = 20,
) -> List[Place]:
    """TourAPI를 이용한 스포츠/레포츠 장소 조회."""
    raw = await tour.area_based_list(content_type_id=28, area_code=area_code, sigungu_code=sigungu_code, page=page, size=size)
    return normalize_tour_list(raw, category="sports")