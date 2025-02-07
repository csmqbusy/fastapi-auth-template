from sqlalchemy import ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.models import Base
from app.models.mixins import IdUuidPkMixin


class RefreshTokenModel(IdUuidPkMixin, Base):
    __tablename__ = "refresh_tokens"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    token_hash: Mapped[str] = mapped_column(nullable=False, index=True)
    created_at: Mapped[int]
    expires_at: Mapped[int]
    device_info: Mapped[dict] = mapped_column(JSON, nullable=False)
