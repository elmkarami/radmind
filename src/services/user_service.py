from src.db.dao import user_dao
from src.utils.validators import (
    validate_email,
    validate_password,
    validate_phone_number,
)


class UserService:
    @staticmethod
    async def get_all_users():
        return await user_dao.get_all_users()

    @staticmethod
    async def get_users_paginated(first=None, after=None, last=None, before=None):
        return await user_dao.get_users_paginated(first, after, last, before)

    @staticmethod
    async def get_user_by_id(user_id: int):
        return await user_dao.get_user_by_id(user_id)

    @staticmethod
    async def get_users_by_organization_id(organization_id: int):
        return await user_dao.get_users_by_organization_id(organization_id)

    @staticmethod
    async def create_user(input_data: dict):
        # Validate required fields
        if not input_data.get("firstName") or not input_data.get("firstName").strip():
            raise ValueError("First name is required")
        if not input_data.get("lastName") or not input_data.get("lastName").strip():
            raise ValueError("Last name is required")
        if not input_data.get("email") or not input_data.get("email").strip():
            raise ValueError("Email is required")
        if not input_data.get("password") or not input_data.get("password").strip():
            raise ValueError("Password is required")

        # Validate email format
        validate_email(input_data["email"])

        # Validate password strength
        validate_password(input_data["password"])

        # Validate phone number if provided
        if input_data.get("phoneNumber"):
            validate_phone_number(input_data["phoneNumber"])

        return await user_dao.create_user(input_data)

    @staticmethod
    async def update_user(user_id: int, input_data: dict):
        return await user_dao.update_user(user_id, input_data)

    @staticmethod
    async def delete_user(user_id: int):
        return await user_dao.delete_user(user_id)

    @staticmethod
    async def get_all_organizations():
        return await user_dao.get_all_organizations()

    @staticmethod
    async def get_organizations_paginated(
        first=None, after=None, last=None, before=None
    ):
        return await user_dao.get_organizations_paginated(first, after, last, before)

    @staticmethod
    async def get_organization_by_id(organization_id: int):
        return await user_dao.get_organization_by_id(organization_id)

    @staticmethod
    async def create_organization(input_data: dict):
        # Validate required fields
        if not input_data.get("name") or not input_data.get("name").strip():
            raise ValueError("Organization name is required")
        if not input_data.get("address") or not input_data.get("address").strip():
            raise ValueError("Address is required")
        if (
            not input_data.get("phoneNumber")
            or not input_data.get("phoneNumber").strip()
        ):
            raise ValueError("Phone number is required")

        # Validate phone number format
        validate_phone_number(input_data["phoneNumber"])

        return await user_dao.create_organization(input_data)

    @staticmethod
    async def update_organization(organization_id: int, input_data: dict):
        return await user_dao.update_organization(organization_id, input_data)

    @staticmethod
    async def delete_organization(organization_id: int):
        return await user_dao.delete_organization(organization_id)
