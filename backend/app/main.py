from datetime import datetime
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List

from .config import settings
from .models import PitchCreate, PitchOut

app = FastAPI(title="PitchMate API", version="0.1.0")

# (개발 편의) CORS 전체 허용 — 실서비스 시 도메인 제한하세요.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    app.state.mongo_client = AsyncIOMotorClient(settings.MONGO_URI)
    app.state.db = app.state.mongo_client[settings.MONGO_DB]

@app.on_event("shutdown")
async def shutdown():
    app.state.mongo_client.close()

async def get_db():
    return app.state.db

@app.get("/health")
async def health():
    return {"status": "ok", "env": settings.ENV}

@app.post("/pitches", response_model=PitchOut)
async def create_pitch(data: PitchCreate, db=Depends(get_db)):
    doc = data.model_dump()
    doc["created_at"] = datetime.utcnow()
    res = await db.pitches.insert_one(doc)
    saved = await db.pitches.find_one({"_id": res.inserted_id})
    return saved

@app.get("/pitches", response_model=List[PitchOut])
async def list_pitches(db=Depends(get_db)):
    cursor = db.pitches.find().sort("_id", -1)
    return [doc async for doc in cursor]