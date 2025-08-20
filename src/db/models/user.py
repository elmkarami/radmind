from datetime import datetime
from enum import Enum
from typing import List, Optional

import bcrypt
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.models.base import Base


class UserRole(str, Enum):
    OWNER = "Owner"
    RADIOLOGIST = "Radiologist"


class Organization(Base):
    __tablename__ = "organization"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    logo: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    address: Mapped[str] = mapped_column(String, nullable=False)
    phone_number: Mapped[str] = mapped_column(String, nullable=False)
    created_by_user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("user.id"), nullable=False
    )

    created_by: Mapped["User"] = relationship("User", foreign_keys=[created_by_user_id])
    members: Mapped[List["OrganizationMember"]] = relationship(
        "OrganizationMember", back_populates="organization"
    )


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
    password: Mapped[str] = mapped_column(String, nullable=False)
    password_must_change: Mapped[bool] = mapped_column(Boolean, default=True)
    temp_password: Mapped[Optional[str]] = mapped_column(String, nullable=True)

    organization_memberships: Mapped[List["OrganizationMember"]] = relationship(
        "OrganizationMember", back_populates="user"
    )

    def set_password(self, plaintext_password: str) -> None:
        """Hash password using bcrypt"""
        salt = bcrypt.gensalt()
        self.password = bcrypt.hashpw(plaintext_password.encode("utf-8"), salt).decode(
            "utf-8"
        )

    def check_password(self, plaintext_password: str) -> bool:
        """Check password against stored hash"""
        return bcrypt.checkpw(
            plaintext_password.encode("utf-8"), self.password.encode("utf-8")
        )


class OrganizationMember(Base):
    __tablename__ = "organization_member"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("user.id"), nullable=False)
    organization_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("organization.id"), nullable=False
    )
    role: Mapped[UserRole] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    user: Mapped["User"] = relationship(
        "User", back_populates="organization_memberships"
    )
    organization: Mapped["Organization"] = relationship(
        "Organization", back_populates="members"
    )
