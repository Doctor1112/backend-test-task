from fastapi import FastAPI, Depends, HTTPException, status
from src.db.init_db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from src.deps import get_crud
from src.crud import Crud
from src.schemas import (ShiftTaskOut, ShiftTaskCreate, ProductCreate,
                         ShiftTaskEdit, ShiftTaskOutWithProducts)
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



@app.get("/shift_tasks/{id}", response_model=ShiftTaskOutWithProducts)
async def get_shift_task_with_products_ids(id: int, crud: Crud = Depends(get_crud)):
    shift = await crud.get_shift_task_with_products(id)
    if shift is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="shift task with this id does not exist"
        )
    return shift

@app.patch("/shift_tasks/{id}", response_model=ShiftTaskOut)
async def shift_task_edit(id: int, update_data: ShiftTaskEdit,
                          crud: Crud = Depends(get_crud)):
    shift_task = await crud.shift_task_edit_by_id(id=id, data=update_data)
    if shift_task is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="shift task with this id does not exist")
    return shift_task