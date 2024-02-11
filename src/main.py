from fastapi import FastAPI, Depends, HTTPException, status
from src.db.init_db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.deps import get_crud
from src.crud import Crud
from src.schemas import ShiftTaskOut, ShiftTaskCreate, ProductCreate
app = FastAPI()


@app.post("/shift_tasks", status_code=status.HTTP_201_CREATED)
async def create_shift_tasks(shift_tasks: list[ShiftTaskCreate],
                             crud: Crud = Depends(get_crud)):
    unique_pairs: set[tuple] = set()
    shift_tasks_dicts = []
    for shift_task in shift_tasks:
        unique_pair = (shift_task.batch_number, shift_task.batch_date)
        if unique_pair in unique_pairs:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
                                detail=f"batch_number and batch_date are not unique: {unique_pair}")
        unique_pairs.add(unique_pair)
        shift_tasks_dicts.append(shift_task.model_dump())
    await crud.create_shift_tasks(shift_tasks_dicts)

@app.post("/products", status_code=status.HTTP_201_CREATED)
async def create_products(products: list[ProductCreate],
                          crud: Crud = Depends(get_crud)):
    await crud.create_products(products)



