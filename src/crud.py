from typing import Sequence
from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import ShiftTask, Product
from sqlalchemy.orm import selectinload
from datetime import date, datetime
from sqlalchemy.dialects.sqlite import insert as sqlite_upsert
from src.schemas import ProductCreate, ShiftTaskEdit


class Crud:

    def __init__(self, db: AsyncSession):
        self._db = db

    async def get_shift_task_with_products(self, shift_id: int) -> ShiftTask | None:
        query = select(ShiftTask).where(ShiftTask.id == shift_id).options(
            selectinload(ShiftTask.products).load_only(Product.id))
        res = await self._db.execute(query)
        return res.scalar_one_or_none()
    
    async def shift_task_edit_by_id(self, id: int, data: ShiftTaskEdit):
        shift_task = await self.get_shift_task_by_id(id)
        if shift_task is None:
            return None
        
        dict_data = data.model_dump(exclude_none=True)
        batch_number = data.batch_number or shift_task.batch_number
        batch_date = data.batch_date or shift_task.batch_date
        if batch_number != shift_task.batch_number or batch_date != shift_task.batch_date:
            shift_task_ = await self.get_shift_task_by_batch_number_and_date(batch_number,
                                                                         batch_date)
            if shift_task_:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                    detail="shift task with that batch number and batch date already exists")
            
        for (key, value) in dict_data.items():
            setattr(shift_task, key, value)
            if key == "closing_status":
                if value == True:
                    shift_task.closed_at = datetime.now()
                else:
                    shift_task.closed_at = None
        await self._db.commit()
        return shift_task
                
    
    
    async def create_shift_tasks(self, shift_tasks: list[dict]):
            
        stmt = sqlite_upsert(ShiftTask).values(shift_tasks)
        stmt = stmt.on_conflict_do_update(
            index_elements=[ShiftTask.batch_date, ShiftTask.batch_number],
            set_=dict(**stmt.excluded))
        await self._db.execute(stmt)
        await self._db.commit()

    async def get_shift_task_by_id(self, id: int) -> ShiftTask | None:
        return await self._db.get(ShiftTask, id)


    async def get_all_shift_tasks(self) -> Sequence[ShiftTask]:
        query = select(ShiftTask)
        res = await self._db.execute(query)
        return res.scalars().all()
    
    async def get_product_by_id(self, id: str) -> Product | None:
        return await self._db.get(Product, id)
    
    async def get_shift_task_by_batch_number_and_date(self, batch_number: int, batch_date: date) -> ShiftTask | None:
        query = select(ShiftTask).where(
            ShiftTask.batch_date == batch_date,
            ShiftTask.batch_number == batch_number
        )
        res = await self._db.execute(query)
        return res.scalar_one_or_none()
    
    async def create_products(self, products: list[ProductCreate]):
        for product in products:
            shift_task = await self.get_shift_task_by_batch_number_and_date(product.batch_number,
                                                         product.batch_date)
            product_exists = await self.get_product_by_id(product.id)
            if shift_task is None or not product_exists is None:
                continue
            self._db.add(Product(**product.model_dump()))
        await self._db.commit()

    async def get_products_count(self) -> int | None:
        query = await self._db.execute(func.count(Product.id))
        return query.scalar()
    
    async def aggregate_product(self, product: Product):
        product.is_aggregated = True
        product.aggregated_at = datetime.now()
        await self._db.commit()
