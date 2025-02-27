import traceback
from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from pydantic import BaseModel


# from user.application.user_service import UserService
from containers import Container
from user.application import user_service
from user.application.user_service import UserService
import logging

router = APIRouter(prefix="/users")

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)

class CreateUserBody(BaseModel):
    name: str
    email: str
    password: str

class UpdateUser(BaseModel):
    name: str | None = None
    password: str | None = None


@router.post("", status_code=201)
@inject
def create_user(
        user: CreateUserBody,
        user_service: UserService = Depends(Provide[Container.user_service]),
):
    created_user = user_service.create_user(name=user.name, email=user.email, password=user.password, memo='')

    return created_user

@router.put('/{user_id}')
@inject
def update_user(
        user_id: str,
        user: UpdateUser,
        user_service: UserService = Depends(Provide[Container.user_service])):

    try:
        user = user_service.update_user(user_id, name=user.name, password=user.password)
    except Exception as e:
        logger.error(traceback.format_exc())
    return user

@router.get("")
@inject
def get_users(page: int = 1, item_per_page: int = 10, user_service: UserService = Depends(Provide[Container.user_service])):
    total_count, users = user_service.get_users(page, item_per_page)
    return {
        'total_count': total_count,
        'page': page,
        'users': users,
    }

@router.delete("", status_code=204)
@inject
def delete_user(user_id: str, user_service: UserService = Depends(Provide[Container.user_service])):
    user_service.delete_user(user_id)
