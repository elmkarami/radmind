from ariadne import MutationType

from src.api.auth_context import get_current_user
from src.services.auth_service import AuthService
from src.services.report_service import ReportService
from src.services.user_service import UserService

mutation = MutationType()


@mutation.field("login")
async def resolve_login(*_, email, password):
    return await AuthService.login(email, password)


@mutation.field("changePassword")
async def resolve_change_password(*_, currentPassword, newPassword):
    current_user = get_current_user()
    return await AuthService.change_password(
        current_user.id, currentPassword, newPassword
    )


@mutation.field("createUser")
async def resolve_create_user(*_, input):
    return await UserService.create_user(input)


@mutation.field("updateUser")
async def resolve_update_user(*_, id, input):
    return await UserService.update_user(int(id), input)


@mutation.field("deleteUser")
async def resolve_delete_user(*_, id):
    return await UserService.delete_user(int(id))


@mutation.field("createOrganization")
async def resolve_create_organization(*_, input):
    current_user = get_current_user()
    # Add current user as creator
    input_with_creator = input.copy()
    input_with_creator["created_by_user_id"] = current_user.id
    return await UserService.create_organization(input_with_creator)


@mutation.field("updateOrganization")
async def resolve_update_organization(*_, id, input):
    return await UserService.update_organization(int(id), input)


@mutation.field("deleteOrganization")
async def resolve_delete_organization(*_, id):
    return await UserService.delete_organization(int(id))


@mutation.field("createStudy")
async def resolve_create_study(*_, input):
    return await ReportService.create_study(input)


@mutation.field("updateStudy")
async def resolve_update_study(*_, id, input):
    return await ReportService.update_study(int(id), input)


@mutation.field("deleteStudy")
async def resolve_delete_study(*_, id):
    return await ReportService.delete_study(int(id))


@mutation.field("createReport")
async def resolve_create_report(*_, input):
    current_user = get_current_user()
    # Add user ID from auth context to input
    input_with_user = input.copy()
    input_with_user["userId"] = current_user.id
    return await ReportService.create_report(input_with_user)


@mutation.field("updateReport")
async def resolve_update_report(*_, id, input):
    return await ReportService.update_report(int(id), input)


@mutation.field("deleteReport")
async def resolve_delete_report(*_, id):
    return await ReportService.delete_report(int(id))


@mutation.field("inviteRadiologist")
async def resolve_invite_radiologist(*_, organizationId, input):
    current_user = get_current_user()
    return await UserService.invite_radiologist(
        int(organizationId), input, current_user.id
    )


@mutation.field("removeRadiologist")
async def resolve_remove_radiologist(*_, userId, organizationId):
    return await UserService.remove_radiologist(int(userId), int(organizationId))


@mutation.field("getRadiologistPassword")
async def resolve_get_radiologist_password(*_, userId):
    return await UserService.get_radiologist_password(int(userId))


@mutation.field("forcePasswordReset")
async def resolve_force_password_reset(*_, userId):
    return await UserService.force_password_reset(int(userId))
