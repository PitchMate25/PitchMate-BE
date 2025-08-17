from typing import List, Annotated
from pydantic import BaseModel, Field, ConfigDict
from pydantic.functional_validators import BeforeValidator
from bson import ObjectId

def to_object_id_str(v):
    # 스키마는 str로 노출, 내부 검증은 여기서
    if isinstance(v, ObjectId):
        return str(v)
    if isinstance(v, str) and ObjectId.is_valid(v):
        return v  # 이미 문자열 ObjectId
    raise ValueError("Invalid ObjectId")

# 스키마 타입은 str, 검증은 BeforeValidator로 처리
PyObjectId = Annotated[str, BeforeValidator(to_object_id_str)]

class PitchCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    author: str = Field(..., min_length=1, max_length=50)

class PitchOut(BaseModel):
    id: PyObjectId = Field(alias="_id")
    title: str
    content: str
    author: str

    # Pydantic v2 설정
    model_config = ConfigDict(
        populate_by_name=True,
        arbitrary_types_allowed=True,
    )
