from fastapi import HTTPException, Response
from httpx import AsyncClient
import pytest
from src.schemas import ProductCreate, ShiftTaskOut, ShiftTaskFilter
from src.crud import Crud
from datetime import date, datetime
from src.models import Product, ShiftTask
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.encoders import jsonable_encoder


@pytest.mark.parametrize(
    ("offset", "limit"),
    [
        (1, 2),
        (0, 100),
        (10, 10),
        (0, 0),
    ],
)
async def test_get_shift_tasks_filter_by_closing_status(
    ac: AsyncClient, shift_task_factory, offset, limit
):
    tasks = await shift_task_factory(12)
    res = await ac.get(
        "/shift_tasks",
        params={"closing_status": False, "offset": offset, "limit": limit},
    )
    expected_tasks = tasks[offset:][:limit]
    body = res.json()
    assert res.status_code == 200, res.json()
    assert len(body) == len(expected_tasks)
    for task in expected_tasks:
        task_dict = jsonable_encoder(ShiftTaskOut(**task.__dict__))
        assert task_dict in body


async def test_get_shift_task_by_all_fields(ac: AsyncClient, shift_task: ShiftTask):
    shift_task_filter = ShiftTaskFilter(**shift_task.__dict__)
    for field_name, value in shift_task_filter:
        if value is None:
            continue
        res = await ac.get("/shift_tasks", params={field_name: value})
        assert res.status_code == 200, res.json()
        task_dict = jsonable_encoder(shift_task_filter)
        assert task_dict == res.json()[0]


async def test_get_shift_task_by_batch_number_and_batch_date(
    ac: AsyncClient, shift_task
):
    res = await ac.get(
        "/shift_tasks",
        params={
            "batch_number": shift_task.batch_number,
            "batch_date": shift_task.batch_date,
        },
    )
    shift_task_dict = jsonable_encoder(ShiftTaskOut(**shift_task.__dict__))
    assert shift_task_dict == res.json()[0]
