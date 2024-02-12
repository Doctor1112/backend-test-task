from fastapi import HTTPException, Response
from httpx import AsyncClient
import pytest
from src.schemas import ProductCreate, ShiftTaskOut
from src.crud import Crud
from datetime import date, datetime
from src.models import ShiftTask
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.parametrize(
    "update_data",
    (
        {"brigade": "brigade", "task": "task"},
        {"batch_number": 0, "batch_date": "2021-02-01"},
    ),
)
async def test_edit_shift_task(shift_task: ShiftTask, ac: AsyncClient, update_data):
    res = await ac.patch(f"/shift_tasks/{shift_task.id}", json=update_data)
    expected_res = ShiftTaskOut(**{**shift_task.__dict__, **update_data})
    body = ShiftTaskOut(**res.json())
    assert res.status_code == 200
    assert expected_res == body


async def test_update_to_existing_batch_date_and_number(
    ac: AsyncClient, shift_task_factory
):
    shift_tasks = await shift_task_factory(n=2)
    update_data = {
        "batch_number": shift_tasks[0].batch_number,
        "batch_date": shift_tasks[0].batch_date.strftime("%Y-%m-%d"),
    }

    res = await ac.patch(f"/shift_tasks/{shift_tasks[1].id}", json=update_data)
    assert res.status_code == 400


async def test_set_closing_status_true(shift_task: ShiftTask, ac: AsyncClient):
    update_data = {"brigade": "brigade", "task": "task", "closing_status": True}
    assert shift_task.closing_status == False
    res = await ac.patch(f"/shift_tasks/{shift_task.id}", json=update_data)
    body = res.json()
    assert res.status_code == 200
    assert body["closing_status"] == True
    assert body["closed_at"]


async def test_set_closing_status_false(
    shift_task: ShiftTask, ac: AsyncClient, async_session: AsyncSession
):
    shift_task.closing_status = True
    shift_task.closed_at = datetime.now()
    await async_session.commit()
    update_data = {"closing_status": False}
    res = await ac.patch(f"/shift_tasks/{shift_task.id}", json=update_data)
    body = res.json()
    assert res.status_code == 200
    assert body["closing_status"] == False
    assert body["closed_at"] is None


async def test_edit_unexisting_shift_task(ac: AsyncClient):
    update_data = {"closing_status": False}
    res = await ac.patch("/shift_tasks/1", json=update_data)
    assert res.status_code == 404
