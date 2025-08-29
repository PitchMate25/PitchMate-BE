"""
API 응답을 공통 스키마로 변환하는 유틸리티 함수들.

TourAPI와 GoCamping API의 응답 형식이 조금씩 다르므로, 이 모듈에서
Pydantic 모델(Place) 리스트로 변환하여 일관된 구조를 제공합니다.
"""

from typing import Any, Dict, List
from ..schemas.external import Place

def normalize_tour_list(data: Dict[str, Any], category: str) -> List[Place]:
    """TourAPI 목록 응답을 Place 리스트로 변환한다."""
    items = (
        data.get("response", {}).get("body", {}).get("items", {}) or {}
    ).get("item", []) or []
    if isinstance(items, dict):
        items = [items]
    out: List[Place] = []
    for it in items:
        out.append(
            Place(
                id=str(it.get("contentid")),
                name=it.get("title") or "",
                category=category,
                lat=float(it["mapy"]) if it.get("mapy") else None,
                lng=float(it["mapx"]) if it.get("mapx") else None,
                address=it.get("addr1"),
                tel=it.get("tel"),
                image=it.get("firstimage"),
                source="tourapi",
                link=None,
            )
        )
    return out

def normalize_gocamping_list(data: Dict[str, Any]) -> List[Place]:
    """GoCamping API 목록 응답을 Place 리스트로 변환한다."""
    items = (
        data.get("response", {}).get("body", {}).get("items", {}) or {}
    ).get("item", []) or []
    if isinstance(items, dict):
        items = [items]
    out: List[Place] = []
    for it in items:
        out.append(
            Place(
                id=str(it.get("contentId") or it.get("facltNm")),
                name=it.get("facltNm") or "",
                category="camping",
                lat=float(it["mapY"]) if it.get("mapY") else None,
                lng=float(it["mapX"]) if it.get("mapX") else None,
                address=it.get("addr1"),
                tel=it.get("tel"),
                image=it.get("firstImageUrl"),
                source="gocamping",
                link=it.get("homepage"),
            )
        )
    return out