from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base
from app.models.mixins import IdIntPKMixin


class UserModel(IdIntPKMixin, Base):
    __tablename__ = "users"

    username: Mapped[str] = mapped_column(unique=True)
    password: Mapped[bytes]
    email: Mapped[str] = mapped_column(unique=True)
    active: Mapped[bool] = mapped_column(default=True)
