import secrets
import string

from src.db.dao import user_dao
from src.db.dao.user_dao import (
    create_organization_member,
    get_organization_members,
    get_user_organization_memberships,
    remove_organization_member,
)
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

        # Map GraphQL field names to model field names
        user_data = input_data.copy()
        if "firstName" in user_data:
            user_data["first_name"] = user_data.pop("firstName")
        if "lastName" in user_data:
            user_data["last_name"] = user_data.pop("lastName")
        if "phoneNumber" in user_data:
            user_data["phone_number"] = user_data.pop("phoneNumber")

        return await user_dao.create_user(user_data)

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

        # Map GraphQL field names to model field names
        org_data = input_data.copy()
        if "phoneNumber" in org_data:
            org_data["phone_number"] = org_data.pop("phoneNumber")

        # Create organization
        organization = await user_dao.create_organization(org_data)

        # Automatically create owner membership for the creator
        await create_organization_member(
            user_id=org_data["created_by_user_id"],
            organization_id=organization.id,
            role="Owner",
        )

        return organization

    @staticmethod
    async def update_organization(organization_id: int, input_data: dict):
        # Map GraphQL field names to model field names
        org_data = input_data.copy()
        if "phoneNumber" in org_data:
            org_data["phone_number"] = org_data.pop("phoneNumber")
        return await user_dao.update_organization(organization_id, org_data)

    @staticmethod
    async def get_organization_members(organization_id: int):
        """Get all members of an organization"""
        return await get_organization_members(organization_id)

    @staticmethod
    async def get_user_organization_memberships(user_id: int):
        """Get all organization memberships for a user"""
        return await get_user_organization_memberships(user_id)

    @staticmethod
    async def invite_radiologist(
        organization_id: int, input_data: dict, current_user_id: int
    ):
        """Invite a radiologist to an organization"""
        # Generate temporary password for invited radiologist

        temp_password = "".join(
            secrets.choice(string.ascii_letters + string.digits + "!@#$%^&*")
            for _ in range(12)
        )

        # Create the user - keep camelCase field names for create_user validation
        user_data = {
            "firstName": input_data["firstName"],
            "lastName": input_data["lastName"],
            "email": input_data["email"],
            "phoneNumber": input_data.get("phoneNumber"),
            "password": temp_password,
            "temp_password": temp_password,
            "password_must_change": True,
        }
        user = await UserService.create_user(user_data)

        # Create organization membership
        await create_organization_member(user.id, organization_id, "Radiologist")

        return user

    @staticmethod
    async def remove_radiologist(user_id: int, organization_id: int):
        """Remove a radiologist from an organization"""
        return await remove_organization_member(user_id, organization_id)

    @staticmethod
    async def get_radiologist_password(user_id: int):
        """Get temporary password for a radiologist"""
        user = await user_dao.get_user_by_id(user_id)
        return user.temp_password if user else None

    @staticmethod
    async def force_password_reset(user_id: int):
        """Force password reset for a user"""

        # Generate temporary password
        temp_password = "".join(
            secrets.choice(string.ascii_letters + string.digits) for _ in range(12)
        )

        # Update user
        await user_dao.update_user_password_fields(
            user_id, temp_password=temp_password, password_must_change=True
        )
        return temp_password

    @staticmethod
    async def delete_organization(organization_id: int):
        return await user_dao.delete_organization(organization_id)
