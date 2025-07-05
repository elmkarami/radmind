from ariadne import ObjectType

from src.services.report_service import ReportService
from src.services.user_service import UserService

report_type = ObjectType("Report")
study_type = ObjectType("Study")
study_template_type = ObjectType("StudyTemplate")
report_history_type = ObjectType("ReportHistory")
report_event_type = ObjectType("ReportEvent")


# Report field resolvers for camelCase mapping
@report_type.field("promptText")
def resolve_report_prompt_text(report, *_):
    return report.prompt_text


@report_type.field("resultText")
def resolve_report_result_text(report, *_):
    return report.result_text


@report_type.field("createdAt")
def resolve_report_created_at(report, *_):
    return report.created_at.isoformat() if report.created_at else None


@report_type.field("updatedAt")
def resolve_report_updated_at(report, *_):
    return report.updated_at.isoformat() if report.updated_at else None


@report_type.field("study")
async def resolve_report_study(report, *_):
    return await ReportService.get_study_by_id(report.study_id)


@report_type.field("template")
async def resolve_report_template(report, *_):
    if report.template_id:
        return await ReportService.get_template_by_id(report.template_id)
    return None


@report_type.field("user")
async def resolve_report_user(report, *_):
    return await UserService.get_user_by_id(report.user_id)


@report_type.field("history")
async def resolve_report_history(report, *_):
    return await ReportService.get_report_history_by_report_id(report.id)


@report_type.field("events")
async def resolve_report_events(report, *_):
    return await ReportService.get_report_events_by_report_id(report.id)


@study_type.field("templates")
async def resolve_study_templates(study, *_):
    return await ReportService.get_templates_by_study_id(study.id)


@study_type.field("reports")
async def resolve_study_reports(study, *_):
    return await ReportService.get_reports_by_study_id(study.id)


@study_template_type.field("study")
async def resolve_template_study(template, *_):
    return await ReportService.get_study_by_id(template.study_id)


@report_history_type.field("report")
async def resolve_history_report(history, *_):
    return await ReportService.get_report_by_id(history.report_id)


@report_event_type.field("report")
async def resolve_event_report(event, *_):
    return await ReportService.get_report_by_id(event.report_id)


# Study field resolvers for camelCase mapping
@study_type.field("createdAt")
def resolve_study_created_at(study, *_):
    return study.created_at.isoformat() if study.created_at else None


# StudyTemplate field resolvers for camelCase mapping
@study_template_type.field("sectionNames")
def resolve_template_section_names(template, *_):
    return template.section_names


@study_template_type.field("createdAt")
def resolve_template_created_at(template, *_):
    return template.created_at.isoformat() if template.created_at else None


# ReportHistory field resolvers for camelCase mapping
@report_history_type.field("resultText")
def resolve_history_result_text(history, *_):
    return history.result_text


# ReportEvent field resolvers for camelCase mapping
@report_event_type.field("eventType")
def resolve_event_type(event, *_):
    return event.event_type
