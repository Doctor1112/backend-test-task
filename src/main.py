from fastapi import FastAPI, Depends
from src.db.init_db import get_db
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()


@app.get("/")
def index(db: AsyncSession = Depends(get_db)):
    return "Hi"