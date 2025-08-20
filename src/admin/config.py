from fastadmin import SqlAlchemyModelAdmin, register
from fastapi import FastAPI

from src.db.models.report import (
    Report,
    ReportEvent,
    ReportHistory,
    Study,
    StudyTemplate,
)
from src.db.models.user import Organization, User
from src.db.session import async_session_factory


# Register User admin
@register(User, sqlalchemy_sessionmaker=async_session_factory)
class UserAdmin(SqlAlchemyModelAdmin):
    list_display = ("id", "first_name", "last_name", "email", "role", "created_at")
    list_filter = ("role", "created_at")
    search_fields = ("first_name", "last_name", "email")
    exclude = ("password",)  # Don't show password field
    list_per_page = 20


# Register Organization admin
@register(Organization, sqlalchemy_sessionmaker=async_session_factory)
class OrganizationAdmin(SqlAlchemyModelAdmin):
    list_display = ("id", "name", "address", "phone_number")
    search_fields = ("name", "address")
    list_per_page = 20


# Register Study admin
@register(Study, sqlalchemy_sessionmaker=async_session_factory)
class StudyAdmin(SqlAlchemyModelAdmin):
    list_display = ("id", "name", "created_at")
    list_filter = ("created_at",)
    search_fields = ("name",)
    list_per_page = 20


# Register StudyTemplate admin
@register(StudyTemplate, sqlalchemy_sessionmaker=async_session_factory)
class StudyTemplateAdmin(SqlAlchemyModelAdmin):
    list_display = ("id", "study_id", "created_at")
    list_filter = ("created_at",)
    list_per_page = 20


# Register Report admin
@register(Report, sqlalchemy_sessionmaker=async_session_factory)
class ReportAdmin(SqlAlchemyModelAdmin):
    list_display = ("id", "study_id", "user_id", "status", "created_at", "updated_at")
    list_filter = ("status", "created_at", "updated_at")
    search_fields = ("prompt_text", "result_text")
    list_per_page = 20


# Register ReportHistory admin
@register(ReportHistory, sqlalchemy_sessionmaker=async_session_factory)
class ReportHistoryAdmin(SqlAlchemyModelAdmin):
    list_display = ("id", "report_id", "status", "timestamp")
    list_filter = ("status", "timestamp")
    list_per_page = 20


# Register ReportEvent admin
@register(ReportEvent, sqlalchemy_sessionmaker=async_session_factory)
class ReportEventAdmin(SqlAlchemyModelAdmin):
    list_display = ("id", "report_id", "event_type", "timestamp")
    list_filter = ("event_type", "timestamp")
    search_fields = ("event_type", "details")
    list_per_page = 20


def setup_admin(app: FastAPI):
    """Setup FastAdmin for the FastAPI app"""
    # The registration happens via decorators above
    # Just need to mount the admin app
    pass
