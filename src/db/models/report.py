from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, List, Optional

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, relationship

from src.db.models.base import Base

if TYPE_CHECKING:
    from src.db.models.user import User


class Study(Base):
    __tablename__ = "study"
    id: Optional[int] = Column(Integer, primary_key=True, autoincrement=True)
    name: str = Column(String, nullable=False)
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())

    templates: Mapped[List["StudyTemplate"]] = relationship(
        "StudyTemplate", back_populates="study"
    )
    reports: Mapped[List["Report"]] = relationship("Report", back_populates="study")


class StudyTemplate(Base):
    __tablename__ = "studytemplate"
    id: Optional[int] = Column(Integer, primary_key=True, autoincrement=True)
    study_id: int = Column(Integer, ForeignKey("study.id"), nullable=False)
    section_names: List[str] = Column(ARRAY(String), default=list)
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())

    study: Mapped[Optional[Study]] = relationship("Study", back_populates="templates")


class ReportStatus(str, Enum):
    draft = "Draft"
    preliminary = "Preliminary"
    signed = "Signed"
    signed_with_addendum = "Signed with Addendum"


class Report(Base):
    __tablename__ = "report"
    id: Optional[int] = Column(Integer, primary_key=True, autoincrement=True)
    study_id: int = Column(Integer, ForeignKey("study.id"), nullable=False)
    template_id: int = Column(Integer, ForeignKey("studytemplate.id"), nullable=False)
    user_id: int = Column(Integer, ForeignKey("user.id"), nullable=False)
    created_at: datetime = Column(DateTime(timezone=True), server_default=func.now())
    updated_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)
    prompt_text: str = Column(String, nullable=False)
    result_text: Optional[str] = Column(String, nullable=True)
    status: ReportStatus = Column(String, default=ReportStatus.draft.value)

    study: Mapped[Optional[Study]] = relationship("Study", back_populates="reports")
    template: Mapped["StudyTemplate"] = relationship("StudyTemplate")
    user: Mapped[Optional["User"]] = relationship("User")
    history: Mapped[List["ReportHistory"]] = relationship(
        "ReportHistory", back_populates="report"
    )
    events: Mapped[List["ReportEvent"]] = relationship(
        "ReportEvent", back_populates="report"
    )


class ReportHistory(Base):
    __tablename__ = "reporthistory"
    id: Optional[int] = Column(Integer, primary_key=True, autoincrement=True)
    report_id: int = Column(Integer, ForeignKey("report.id"), nullable=False)
    timestamp: datetime = Column(DateTime(timezone=True), server_default=func.now())
    status: ReportStatus = Column(String, nullable=False)
    result_text: Optional[str] = Column(String, nullable=True)

    report: Mapped[Optional[Report]] = relationship("Report", back_populates="history")


class ReportEvent(Base):
    __tablename__ = "reportevent"
    id: Optional[int] = Column(Integer, primary_key=True, autoincrement=True)
    report_id: int = Column(Integer, ForeignKey("report.id"), nullable=False)
    event_type: str = Column(String, nullable=False)
    timestamp: datetime = Column(DateTime(timezone=True), server_default=func.now())
    details: Optional[str] = Column(String, nullable=True)

    report: Mapped[Optional[Report]] = relationship("Report", back_populates="events")


# class Study(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     name: str
#     created_at: datetime = Field(
#         sa_column=Column(DateTime(timezone=True), server_default=func.now())
#     )

#     templates: List["StudyTemplate"] = Relationship(back_populates="study")
#     reports: List["Report"] = Relationship(back_populates="study")


# class StudyTemplate(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     study_id: int = Field(foreign_key="study.id")
#     section_names: List[str] = Field(sa_column=Column(ARRAY(str)), default_factory=list)
#     created_at: datetime = Field(
#         sa_column=Column(DateTime(timezone=True), server_default=func.now())
#     )

#     study: Optional[Study] = Relationship(back_populates="templates")


# class ReportStatus(str, Enum):
#     draft = "Draft"
#     preliminary = "Preliminary"
#     signed = "Signed"
#     signed_with_addendum = "Signed with Addendum"


# class Report(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     study_id: int = Field(foreign_key="study.id")
#     template_id: Optional[int] = Field(default=None, foreign_key="studytemplate.id")
#     user_id: int = Field(foreign_key="user.id")
#     created_at: datetime = Field(
#         sa_column=Column(DateTime(timezone=True), server_default=func.now())
#     )
#     updated_at: Optional[DateTime] = Field(
#         sa_column=Column(DateTime(timezone=True), nullable=True)
#     )
#     prompt_text: Optional[str] = None
#     result_text: Optional[str] = None
#     status: ReportStatus = Field(default=ReportStatus.draft)

#     study: Optional[Study] = Relationship(back_populates="reports")
#     template: Optional[StudyTemplate] = Relationship()
#     user: Optional["User"] = Relationship()
#     history: List["ReportHistory"] = Relationship(back_populates="report")
#     events: List["ReportEvent"] = Relationship(back_populates="report")


# class ReportHistory(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     report_id: int = Field(foreign_key="report.id")
#     user_id: int = Field(foreign_key="user.id")
#     changed_at: Optional[DateTime] = Field(
#         sa_column=Column(DateTime(timezone=True), server_default=func.now())
#     )
#     prompt_text: Optional[str] = None
#     result_text: Optional[str] = None
#     status: ReportStatus
#     changed_fields: List[str] = Field(
#         sa_column=Column(ARRAY(str)), default_factory=list
#     )
#     created_at: datetime = Field(
#         sa_column=Column(DateTime(timezone=True), server_default=func.now())
#     )

#     report: Optional["Report"] = Relationship(back_populates="history")
#     user: Optional["User"] = Relationship()


# class ReportEvent(SQLModel, table=True):
#     id: Optional[int] = Field(default=None, primary_key=True)
#     report_id: int = Field(foreign_key="report.id")
#     user_id: int = Field(foreign_key="user.id")
#     old_status: ReportStatus
#     new_status: ReportStatus
#     event_time: Optional[DateTime] = Field(
#         sa_column=Column(DateTime(timezone=True), server_default=func.now())
#     )
#     created_at: datetime = Field(
#         sa_column=Column(DateTime(timezone=True), server_default=func.now())
#     )
#     notes: Optional[str] = None

#     report: Optional["Report"] = Relationship(back_populates="events")
#     user: Optional["User"] = Relationship()
