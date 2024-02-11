from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from src.db.init_db import get_db
from src.crud import Crud

async def get_crud(db: AsyncSession = Depends(get_db)):
    return Crud(db)