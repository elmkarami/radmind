import hashlib
from datetime import datetime
from typing import List, Optional

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.models.base import Base


class Organization(Base):
    __tablename__ = "organization"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    logo: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    address: Mapped[str] = mapped_column(String, nullable=False)
    phone_number: Mapped[str] = mapped_column(String, nullable=False)

    users: Mapped[List["User"]] = relationship("User", back_populates="organization")


class User(Base):
    __tablename__ = "user"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    first_name: Mapped[str] = mapped_column(String, nullable=False)
    last_name: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, nullable=False)
    phone_number: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    organization_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("organization.id"), nullable=True
    )
    password: Mapped[str] = mapped_column(String, nullable=False)
    role: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    organization: Mapped[Optional[Organization]] = relationship(
        "Organization", back_populates="users"
    )

    def set_password(self, plaintext_password: str) -> None:
        # Simple hash for demonstration; use a proper password hashing library in production!
        self.password = hashlib.sha256(plaintext_password.encode("utf-8")).hexdigest()
