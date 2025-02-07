from app.models import UserModel
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[UserModel]):
    def __init__(self):
        super().__init__(UserModel)


user_repo = UserRepository()
