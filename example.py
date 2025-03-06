import time
from fastapi import FastAPI, Request

import asyncio
from contextvars import ContextVar
from fastapi import APIRouter

foo_context: ContextVar[str] = ContextVar('foo', default='bar')
router = APIRouter(prefix='/context')

@router.get('')
async def context_test(var: str):
    foo_context.set(var)
    await asyncio.sleep(1)

    return {
        'var': var,
        'context_var': foo_context.get()
    }

def create_sample_middleware(app: FastAPI):
    @app.middleware('http')
    async def add_process_time_header(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        process_time = time.time() - start_time
        response.headers['X-Process-Time'] = str(process_time)
        return response