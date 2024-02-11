from fastapi import HTTPException, Response
from httpx import AsyncClient
import pytest
from src.schemas import ProductCreate
from src.crud import Crud
from datetime import date


async def test_products_create(ac: AsyncClient,
                              crud: Crud,
                              product_factory):
    products = await product_factory(3)
    res = await ac.post("/products", json=products)
    assert res.status_code == 201
    assert await crud.get_products_count() == 3




async def test_products_create_with_unexisting_shift_task(ac: AsyncClient,
                              crud: Crud,
                              product_factory):
    products = [*await product_factory(2), *await product_factory(with_task_creating=False)]
    res = await ac.post("/products", json=products)
    assert res.status_code == 201
    assert await crud.get_products_count() == 2


async def test_products_create_with_existing_id(ac: AsyncClient,
                              crud: Crud,
                              product_factory):
    products = await product_factory(n=3)
    res = await ac.post("/products", json=products)
    res = await ac.post("/products", json=products[0:1])
    assert res.status_code == 201
    assert await crud.get_products_count() == 3