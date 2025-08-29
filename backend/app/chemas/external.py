"""
외부 API 응답을 위한 Pydantic 스키마.

Place 모델은 TourAPI 및 GoCamping API에서 받아온 데이터를 표준화하여 반환하기 위해 사용됩니다.
"""

from typing import Optional
from pydantic import BaseModel, Field

class Place(BaseModel):
    """외부 API에서 수신한 장소 정보를 표현하는 모델."""

    id: str
    name: str
    category: str = Field(..., description="camping|experience|sports|general")
    lat: Optional[float] = None
    lng: Optional[float] = None
    address: Optional[str] = None
    tel: Optional[str] = None
    image: Optional[str] = None
    source: str  # "tourapi" 또는 "gocamping"
    link: Optional[str] = None