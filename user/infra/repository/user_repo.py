from fastapi import HTTPException

from database import SessionLocal
from user.domain.repository.user_repo import IUserRepository
from user.domain.user import User as UserVo
from user.infra.db_models.user import User

from utils.db_utils import row_to_dict


class UserRepository(IUserRepository):
    def save(self, user: UserVo):
        new_user = User(
            id=user.id,
            email=user.email,
            name=user.name,
            password=user.password,
            created_at=user.created_at,
            updated_at=user.updated_at
        )

        with SessionLocal() as db:
            try:
                db = SessionLocal()
                db.add(new_user)
                db.commit()
            finally:
                db.close()

    def find_by_email(self, email: str) -> UserVo:
        with SessionLocal() as db:
            user = db.query(User).filter(User.email == email).first()

            if not user:
                raise HTTPException(status_code=422)

            return UserVo(**row_to_dict(user))
            # return UserVo(
            #     id=user.id,
            #     name=user.name,
            #     email=user.email,
            #     password=user.password,
            #     created_at=user.created_at,
            #     updated_at=user.updated_at
            # )

    def find_by_id(self, user_id: str) -> UserVo:
        with SessionLocal() as db:
            user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=422)

        return UserVo(**row_to_dict(user))

    def update(self, user_vo: UserVo):
        with SessionLocal() as db:
            user = db.query(User).filter(User.id == user_vo.id).first()

            if not user:
                raise HTTPException(status_code=422)

            user.name = user_vo.name
            user.password = user_vo.password

            db.add(user)
            db.commit()

        return user

    def get_users(self, page: int = 1, item_per_page: int = 10) -> tuple[int, list[UserVo]]:
        with SessionLocal() as db:
            query = db.query(User)
            total_count = query.count()

            offset = (page - 1) * item_per_page
            users = query.limit(item_per_page).offset(offset).all()

            # result = db.query(User).pagination.page(page, item_per_page)
            # total_count = result.total
            # users = result.items
            return total_count, [UserVo(**row_to_dict(user)) for user in users]

    def delete(self, user_id: str):
        with SessionLocal() as db:
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise HTTPException(status_code=422)

            db.delete(user)
            db.commit()