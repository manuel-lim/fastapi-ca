from dependency_injector.wiring import inject, Provide
# from typing import Annotated
from fastapi import HTTPException, Depends, status, BackgroundTasks
from pydantic_core.core_schema import DatetimeSchema
from sqlalchemy.sql.coercions import RoleImpl
from ulid import ULID
from datetime import datetime
from user.domain.user import User
from user.domain.repository.user_repo import IUserRepository
from user.infra.repository.user_repo import UserRepository
from utils.crypto import Crypto
from common.auth import create_access_token, Role
from user.application.send_welcome_email_task import SendWelcomeEmailTask

class UserService:
    @inject
    def __init__(
            self,
            # user_repo: IUserRepository = Depends(Provide[Container.user_repo]),
            user_repo: IUserRepository,
    ):
        # self.user_repo: IUserRepository = UserRepository()
        self.user_repo = user_repo
        self.ulid = ULID()
        self.crypto = Crypto()

    def create_user(self, name: str, email: str, password: str, memo: str):
        _user = None

        try:
            _user = self.user_repo.find_by_email(email)
        except HTTPException as e:
            if e.status_code != 422:
                raise e

        if _user:
            raise HTTPException(status_code=422)

        now = datetime.now()

        user: User = User(
            id=self.ulid.generate(),
            name=name,
            email=email,
            password=self.crypto.encrypt(password),
            memo=memo,
            created_at=now,
            updated_at=now
        )

        self.user_repo.save(user)
        SendWelcomeEmailTask().run(user.email)

        return user

    def update_user(self, user_id: str, name: str | None = None, password: str | None = None):
        user = self.user_repo.find_by_id(user_id)

        if name:
            user.name = name

        if password:
            user.password = self.crypto.encrypt(password)

        user.updated_at = datetime.now()
        self.user_repo.update(user)
        return user


    def get_users(self, page: int, items_per_page: int) -> tuple[int, list[User]]:
        return self.user_repo.get_users(page, items_per_page)


    def delete_user(self, user_id: str):
        self.user_repo.delete(user_id)

    def login(self, email: str, password: str):
        user = self.user_repo.find_by_email(email)

        if not self.crypto.verify(password, user.password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        access_token = create_access_token(payload={'user_id': user.id}, role=Role.USER)
        return access_token