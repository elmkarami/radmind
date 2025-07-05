from ariadne import MutationType

from src.services.report_service import ReportService
from src.services.user_service import UserService

mutation = MutationType()


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
    return await UserService.create_organization(input)


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
    return await ReportService.create_report(input)


@mutation.field("updateReport")
async def resolve_update_report(*_, id, input):
    return await ReportService.update_report(int(id), input)


@mutation.field("deleteReport")
async def resolve_delete_report(*_, id):
    return await ReportService.delete_report(int(id))
