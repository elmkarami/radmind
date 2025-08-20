from typing import Optional

from sqlalchemy import select

from src.db import db
from src.db.models.user import OrganizationMember, User, UserRole


class PermissionService:
    """Service to handle permission and role-based access control"""

    async def check_user_role_in_organization(
        self, user_id: int, organization_id: int, required_role: UserRole
    ) -> bool:
        """Check if user has the required role in a specific organization"""
        stmt = select(OrganizationMember).where(
            OrganizationMember.user_id == user_id,
            OrganizationMember.organization_id == organization_id,
            OrganizationMember.role == required_role.value,
        )
        result = await db.session.execute(stmt)
        membership = result.scalar_one_or_none()
        return membership is not None

    async def user_has_role_anywhere(
        self, user_id: int, required_role: UserRole
    ) -> bool:
        """Check if user has the required role in any organization"""
        stmt = select(OrganizationMember).where(
            OrganizationMember.user_id == user_id,
            OrganizationMember.role == required_role.value,
        )
        result = await db.session.execute(stmt)
        membership = result.scalar_one_or_none()
        return membership is not None

    async def get_user_organizations_with_role(
        self, user_id: int, role: UserRole
    ) -> list[int]:
        """Get list of organization IDs where user has the specified role"""
        stmt = select(OrganizationMember.organization_id).where(
            OrganizationMember.user_id == user_id, OrganizationMember.role == role.value
        )
        result = await db.session.execute(stmt)
        return [row[0] for row in result.fetchall()]

    async def is_owner_of_organization(
        self, user_id: int, organization_id: int
    ) -> bool:
        """Check if user is owner of specific organization"""
        return await self.check_user_role_in_organization(
            user_id, organization_id, UserRole.OWNER
        )

    async def is_radiologist_in_organization(
        self, user_id: int, organization_id: int
    ) -> bool:
        """Check if user is radiologist in specific organization"""
        return await self.check_user_role_in_organization(
            user_id, organization_id, UserRole.RADIOLOGIST
        )

    async def can_access_organization_data(
        self, user_id: int, organization_id: int
    ) -> bool:
        """Check if user can access organization data (any role)"""
        stmt = select(OrganizationMember).where(
            OrganizationMember.user_id == user_id,
            OrganizationMember.organization_id == organization_id,
        )
        result = await db.session.execute(stmt)
        membership = result.scalar_one_or_none()
        return membership is not None
