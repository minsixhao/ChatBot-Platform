from sqlalchemy.orm import Session
from app.models.orm import HaiguiTangModel
from app.models.haiguitang import HaiguiTangCreate, HaiguiTang, HaiguiTangUpdate
from ulid import ULID
from sqlalchemy import select
from sqlalchemy.sql import func

class HaiguiTangRepository:
    def __init__(self, db: Session):
        self.db = db

    async def create(self, haiguitang: HaiguiTangCreate) -> HaiguiTangModel:
        db_haiguitang = HaiguiTangModel(
            id=str(ULID()),
            title=haiguitang.title,
            tang_mian=haiguitang.tang_mian,
            tang_di=haiguitang.tang_di,
            tags=haiguitang.tags,
            difficulty=haiguitang.difficulty
        )
        self.db.add(db_haiguitang)
        await self.db.commit()
        await self.db.refresh(db_haiguitang)
        return db_haiguitang

    async def get_random_haiguitang(self):
        result = await self.db.execute(
            select(HaiguiTangModel).order_by(func.random()).limit(1)
        )
        return result.scalar_one_or_none()

    async def update_haiguitang(self, haiguitang_id: str, haiguitang: HaiguiTangUpdate) -> HaiguiTangModel:
        db_haiguitang = await self.get_haiguitang(haiguitang_id)
        if db_haiguitang:
            update_data = haiguitang.dict(exclude_unset=True)
            for key, value in update_data.items():
                setattr(db_haiguitang, key, value)
            await self.db.commit()
            await self.db.refresh(db_haiguitang)
        return db_haiguitang

    async def get_haiguitang(self, haiguitang_id: str) -> HaiguiTangModel:
        result = await self.db.execute(select(HaiguiTangModel).filter(HaiguiTangModel.id == haiguitang_id))
        return result.scalar_one_or_none()