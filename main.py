from containers import Container
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.requests import Request
from fastapi.responses import JSONResponse

from user.interface.controller.user_controller import router as user_router
from note.interface.controllers.note_controller import router as note_router

from middlewares import create_middlewares

app = FastAPI()
app.include_router(user_router)
app.include_router(note_router)

app.container = Container()

create_middlewares(app)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
	return JSONResponse(status_code=400, content=exc.errors())
