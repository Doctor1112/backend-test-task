from fastapi import HTTPException, Response
from httpx import AsyncClient
import pytest
from src.schemas import ProductCreate, ShiftTaskOut, ShiftTaskOutWithProducts
from src.crud import Crud
from datetime import date
from src.models import ShiftTask

async def test_get_shift_task(ac: AsyncClient,
                              shift_task: ShiftTask):
    
    res = await ac.get(f"/shift_tasks/{shift_task.id}")
    body = res.json()
    assert res.status_code == 200
    assert ShiftTaskOutWithProducts(**body) == ShiftTaskOutWithProducts(**shift_task.__dict__)

async def test_get_shift_task_with_products(ac: AsyncClient,
                              shift_task: ShiftTask, crud: Crud):
    products_id = [str(i) for i in range(5)]
    products = [ProductCreate(id=str(i), batch_number=shift_task.batch_number, batch_date=shift_task.batch_date) for i in products_id]
    await crud.create_products(products)
    res = await ac.get(f"/shift_tasks/{shift_task.id}")
    assert res.status_code == 200
    body = res.json()
    assert sorted(body["products"]) == sorted(products_id)

async def test_get_unexisting_task(ac: AsyncClient):
    res = await ac.get(f"/shift_tasks/1")
    assert res.status_code == 404