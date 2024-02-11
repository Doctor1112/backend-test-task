from fastapi import HTTPException, Response
from httpx import AsyncClient
import pytest
from src.schemas import ShiftTaskCreate, BaseShiftTask
from src.crud import Crud
from tests.data import base_shift_task



@pytest.mark.parametrize(
    "shift_tasks",
    (
        [base_shift_task],
        [
            base_shift_task,
            {
                **base_shift_task,
                **{"НомерПартии": 222},
            },
        ],
    ),
)
async def test_shift_tasks_create(ac: AsyncClient, shift_tasks: list[dict]):
    res = await ac.post("/shift_tasks", json=shift_tasks)
    assert res.status_code == 201


@pytest.mark.parametrize(
    "shift_tasks",
    (
        [
            base_shift_task,
            {
                **base_shift_task,
                **{
                    "НомерПартии": 222,
                    "ДатаПартии": "2024-01-30",
                    "ДатаВремяНачалаСмены": "2024-01-31T20:00:00+05:00",
                    "ДатаВремяОкончанияСмены": "2024-01-30T08:00:00+05:00",
                },
            },
        ],
    ),
)
async def test_shift_tasks_create_with_wrong_start_end_datetime(
    ac: AsyncClient, shift_tasks: list[dict]
):
    res = await ac.post("/shift_tasks", json=shift_tasks)
    assert res.status_code == 422


async def test_shift_tasks_create_if_shift_task_exists(ac: AsyncClient, crud: Crud):
    shift_task_2 = base_shift_task.copy()
    shift_task_2.update(**{"Смена": "9", "Бригада": "Бригада №6"})
    res = await ac.post("/shift_tasks", json=[base_shift_task])
    assert res.status_code == 201
    res = await ac.post("/shift_tasks", json=[shift_task_2])
    assert res.status_code == 201
    shift_tasks = await crud.get_all_shift_tasks()
    assert len(shift_tasks) == 1
    shift_task_created = shift_tasks[0]
    assert shift_task_created.brigade == shift_task_2["Бригада"]
    assert shift_task_created.shift == shift_task_2["Смена"]


async def test_shift_tasks_create_if_shift_tasks_not_unique(
    ac: AsyncClient, crud: Crud
):

    res = await ac.post("/shift_tasks", json=[base_shift_task, base_shift_task])
    assert res.status_code == 400
