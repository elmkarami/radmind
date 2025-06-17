from ariadne import QueryType

from src.services.report_service import ReportService
from src.services.user_service import UserService

query = QueryType()


@query.field("users")
async def resolve_users(*_, first=None, after=None, last=None, before=None):
    return await UserService.get_users_paginated(first, after, last, before)


@query.field("user")
async def resolve_user(*_, id):
    return await UserService.get_user_by_id(id)


@query.field("organizations")
async def resolve_organizations(*_, first=None, after=None, last=None, before=None):
    return await UserService.get_organizations_paginated(first, after, last, before)


@query.field("organization")
async def resolve_organization(*_, id):
    return await UserService.get_organization_by_id(id)


@query.field("studies")
async def resolve_studies(*_, first=None, after=None, last=None, before=None):
    return await ReportService.get_studies_paginated(first, after, last, before)


@query.field("study")
async def resolve_study(*_, id):
    return await ReportService.get_study_by_id(id)


@query.field("reports")
async def resolve_reports(*_, first=None, after=None, last=None, before=None):
    return await ReportService.get_reports_paginated(first, after, last, before)


@query.field("report")
async def resolve_report(*_, id):
    return await ReportService.get_report_by_id(id)
