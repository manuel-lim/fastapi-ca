import asyncio
from datetime import datetime
from fastapi import APIRouter
from typing import Annotated
from fastapi import APIRouter, Depends
from config import Settings, get_settings

router = APIRouter(prefix="/async-test")

async def async_task(num):
    print("async_task", num)
    await asyncio.sleep(1)
    return num

@router.post("")
async def async_example():
    now = datetime.now()
    results = await asyncio.gather(async_task(1), async_task(2), async_task(3))
    print(datetime.now() - now)

    return {"results": results}

@router.get("")
async def info(settings: Annotated[Settings, Depends(get_settings)]):
    return {
        'database_username': settings.database_username,
        'database_password': settings.database_password,
        'jwt_secret_key': settings.jwt_secret,
    }