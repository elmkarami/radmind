from ariadne import ObjectType

from src.services.report_service import ReportService
from src.services.user_service import UserService

user_type = ObjectType("User")
organization_type = ObjectType("Organization")
organization_member_type = ObjectType("OrganizationMember")


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


@user_type.field("mustChangePassword")
def resolve_user_must_change_password(user, *_):
    return user.password_must_change


@user_type.field("organizationMemberships")
async def resolve_user_organization_memberships(user, *_):
    return await UserService.get_user_organization_memberships(user.id)


# Organization field resolvers for camelCase mapping
@organization_type.field("phoneNumber")
def resolve_organization_phone_number(organization, *_):
    return organization.phone_number


@organization_type.field("createdBy")
async def resolve_organization_created_by(organization, *_):
    return await UserService.get_user_by_id(organization.created_by_user_id)


@organization_type.field("members")
async def resolve_organization_members(organization, *_):
    return await UserService.get_organization_members(organization.id)


@user_type.field("reports")
async def resolve_user_reports(user, *_):
    return await ReportService.get_reports_by_user_id(user.id)


# OrganizationMember field resolvers
@organization_member_type.field("user")
async def resolve_organization_member_user(member, *_):
    return await UserService.get_user_by_id(member.user_id)


@organization_member_type.field("organization")
async def resolve_organization_member_organization(member, *_):
    return await UserService.get_organization_by_id(member.organization_id)


@organization_member_type.field("createdAt")
def resolve_organization_member_created_at(member, *_):
    return member.created_at.isoformat() if member.created_at else None
