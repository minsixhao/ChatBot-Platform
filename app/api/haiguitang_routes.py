from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.haiguitang import HaiguiTangCreate, HaiguiTang, HaiguiTangUpdate
from app.repositories.haiguitang_repository import HaiguiTangRepository
from app.services.haiguitang_service import HaiguiTangService

router = APIRouter()

@router.post("/haiguitang", response_model=HaiguiTang)
async def create_haiguitang(haiguitang: HaiguiTangCreate, db: Session = Depends(get_db)):
    haiguitang_repo = HaiguiTangRepository(db)
    return await haiguitang_repo.create(haiguitang)

@router.put("/haiguitang/{haiguitang_id}", response_model=HaiguiTang)
async def update_haiguitang(haiguitang_id: str, haiguitang: HaiguiTangUpdate, db: Session = Depends(get_db)):
    haiguitang_repo = HaiguiTangRepository(db)
    return await haiguitang_repo.update_haiguitang(haiguitang_id, haiguitang)