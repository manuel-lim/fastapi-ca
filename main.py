from containers import Container
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from user.interface.controller.user_controller import router as user_router
from user.interface.controller.async_ex import router as async_ex_router

app = FastAPI()
app.include_router(user_router)
app.include_router(async_ex_router)

app.container = Container()


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	return JSONResponse(status_code=400, content=exc.errors())
