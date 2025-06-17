from ariadne import ObjectType

from src.services.user_service import UserService

user_type = ObjectType("User")
organization_type = ObjectType("Organization")


@user_type.field("organization")
async def resolve_user_organization(user, *_):
    if user.organization_id:
        return await UserService.get_organization_by_id(user.organization_id)
    return None


@user_type.field("reports")
async def resolve_user_reports(user, *_):
    from src.services.report_service import ReportService

    return await ReportService.get_reports_by_user_id(user.id)


@organization_type.field("users")
async def resolve_organization_users(organization, *_):
    return await UserService.get_users_by_organization_id(organization.id)
