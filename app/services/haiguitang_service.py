from app.repositories.haiguitang_repository import HaiguiTangRepository
from app.models.haiguitang import HaiguiTangCreate, HaiguiTang

class HaiguiTangService:
    def __init__(self, repository: HaiguiTangRepository):
        self.repository = repository

    async def create_haiguitang(self, haiguitang: HaiguiTangCreate) -> HaiguiTang:
        db_haiguitang = await self.repository.create(haiguitang)
        return HaiguiTang.model_validate(db_haiguitang)