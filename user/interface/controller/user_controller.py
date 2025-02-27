import traceback
from datetime import datetime
from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, EmailStr, Field


# from user.application.user_service import UserService
from containers import Container
from user.application import user_service
from user.application.user_service import UserService
import logging

router = APIRouter(prefix="/users")

logger = logging.getLogger("uvicorn")
logger.setLevel(logging.INFO)


class CreateUserBody(BaseModel):
    name: str = Field(min_length=2, max_length=32)
    email: EmailStr = Field(max_length=64)
    password: str = Field(min_length=8, max_length=32)


class UpdateUser(BaseModel):
    name: str | None = Field(min_length=2, max_length=32, default=None)
    password: str | None = Field(min_length=8, max_length=32, default=None)


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime
    updated_at: datetime


class GetUsersResponse(BaseModel):
    total_count: int
    page: int
    users: list[UserResponse]

@router.post("", status_code=201, response_model=UserResponse)
@inject
def create_user(
        user: CreateUserBody,
        user_service: UserService = Depends(Provide[Container.user_service]),
) -> UserResponse:
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

@router.get("", response_model=GetUsersResponse)
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

@router.post('/login')
@inject
def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], user_service: UserService = Depends(Provide[Container.user_service])):
    access_token = user_service.login(email=form_data.username, password=form_data.password)
    return {'access_token': access_token, 'token_type': 'bearer'}
