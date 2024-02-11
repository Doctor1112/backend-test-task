import asyncio
from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from src.db.init_db import Base, get_db
from src.main import app
from src.config import settings
from src.crud import Crud
from src.models import ShiftTask
import faker
from datetime import datetime, date


# DATABASE
TEST_DATABASE_URL = f"postgresql+asyncpg://{settings.DB_TEST_USER}:{settings.DB_TEST_PASS}@{settings.DB_TEST_HOST}:{settings.DB_TEST_PORT}/{settings.DB_TEST_NAME}"


engine_test = create_async_engine(TEST_DATABASE_URL, poolclass=NullPool)
async_session_maker = sessionmaker(engine_test, class_=AsyncSession, expire_on_commit=False)
Base.metadata.engine = engine_test

BASE_URL = "http://test"

async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

app.dependency_overrides[get_db] = get_async_session

@pytest.fixture()
async def async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session

@pytest.fixture()
async def crud(async_session: AsyncSession):
    return Crud(async_session)



@pytest.fixture(autouse=True, scope='function')
async def prepare_database():
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with engine_test.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


# SETUP
@pytest.fixture(scope='session')
def event_loop(request):
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

client = TestClient(app)


@pytest.fixture()
async def ac() -> AsyncGenerator[AsyncClient, None]:
    async with AsyncClient(app=app, base_url=BASE_URL) as ac:
        yield ac

@pytest.fixture()
async def product_factory(async_session: AsyncSession):
    fake = faker.Faker()
    async def inner(n=1, with_task_creating=True) -> list[dict]:
        products = []
        for i in range(n):
            product = {
                    "УникальныйКодПродукта": fake.unique.text(),
                    "НомерПартии": fake.unique.random_int(),
                    "ДатаПартии": fake.unique.date(),
                    }
            if with_task_creating:
                shift_task = ShiftTask(
                            closing_status=False,
                            task=fake.text(),
                            work_center=fake.text(),
                            shift=fake.text(),
                            brigade=fake.text(),
                            batch_number=product["НомерПартии"],
                            batch_date=date.fromisoformat(product["ДатаПартии"]),
                            nomenclature=fake.text(),
                            ekn_code=fake.text(),
                            work_center_id=fake.text(),
                            start_time=datetime(2000, 2, 3),
                            end_time=datetime(2001, 2, 3))
                async_session.add(shift_task)
            await async_session.commit()
            products.append(product)
        return products
    
    return inner

