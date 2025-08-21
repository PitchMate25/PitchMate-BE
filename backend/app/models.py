from datetime import datetime
from sqlalchemy import String, BigInteger, DateTime, func, UniqueConstraint  # UniqueConstraint 쓰면 함께 임포트
from sqlalchemy.orm import Mapped, mapped_column
from .database import Base

class User(Base):
    __tablename__ = "app_user"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    provider: Mapped[str] = mapped_column(String(20), nullable=False)   # 'google'|'kakao'|'naver'
    external_id: Mapped[str] = mapped_column(String(100), nullable=False) # provider user id (sub)
    email: Mapped[str | None] = mapped_column(String(255))
    name: Mapped[str | None] = mapped_column(String(255))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    last_login_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (UniqueConstraint("provider", "external_id", name="uq_provider_external"),)