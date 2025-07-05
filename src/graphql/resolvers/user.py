from ariadne import ObjectType

from src.services.user_service import UserService

user_type = ObjectType("User")
organization_type = ObjectType("Organization")


# User field resolvers for camelCase mapping
@user_type.field("firstName")
def resolve_user_first_name(user, *_):
    return user.first_name


@user_type.field("lastName")
def resolve_user_last_name(user, *_):
    return user.last_name


@user_type.field("phoneNumber")
def resolve_user_phone_number(user, *_):
    return user.phone_number


@user_type.field("createdAt")
def resolve_user_created_at(user, *_):
    return user.created_at.isoformat() if user.created_at else None


# Organization field resolvers for camelCase mapping
@organization_type.field("phoneNumber")
def resolve_organization_phone_number(organization, *_):
    return organization.phone_number


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
