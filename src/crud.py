from typing import Sequence
from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import ShiftTask, Product
from sqlalchemy.orm import selectinload
from datetime import datetime
from sqlalchemy.dialects.sqlite import insert as sqlite_upsert


class Crud:

    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_shift_task_with_products(self, shift_id: int) -> ShiftTask | None:
        query = select(ShiftTask).where(ShiftTask.id == shift_id).options(
            selectinload(ShiftTask.products).load_only(Product.id))
        res = await self._db.execute(query)
        return res.scalar_one_or_none()
    
    
    async def create_shift_tasks(self, shift_tasks: list[dict]):
            
        stmt = sqlite_upsert(ShiftTask).values(shift_tasks)
        stmt = stmt.on_conflict_do_update(
            index_elements=[ShiftTask.batch_date, ShiftTask.batch_number],
            set_=dict(**stmt.excluded))
        await self._db.execute(stmt)
        await self._db.commit()


    async def get_all_shift_tasks(self) -> Sequence[ShiftTask]:
        query = select(ShiftTask)
        res = await self._db.execute(query)
        return res.scalars().all()