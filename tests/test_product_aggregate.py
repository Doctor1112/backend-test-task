from fastapi import HTTPException, Response
from httpx import AsyncClient
import pytest
from src.schemas import ProductCreate, ShiftTaskOut
from src.crud import Crud
from datetime import date, datetime
from src.models import Product, ShiftTask
from sqlalchemy.ext.asyncio import AsyncSession

async def test_product_aggregate(ac: AsyncClient,
                           product: Product, crud: Crud):
    shift_task = await crud.get_shift_task_by_batch_number_and_date(
        product.batch_number,
        product.batch_date
    )
    assert shift_task
    res = await ac.post(f"/products/aggregate/{shift_task.id}/{product.id}")
    assert res.status_code == 200, res.json()
    assert res.json() == product.id

async def test_unexisting_product_aggregate(ac: AsyncClient):
    res = await ac.post(f"/products/aggregate/1/2")
    assert res.status_code == 404

async def test_aggregate_agrregated_product(ac: AsyncClient,
                                            crud: Crud, product: Product):
    shift_task = await crud.get_shift_task_by_batch_number_and_date(
        product.batch_number,
        product.batch_date
    )
    await crud.aggregate_product(product)
    assert shift_task
    res = await ac.post(f"/products/aggregate/{shift_task.id}/{product.id}")
    assert res.status_code == 400


