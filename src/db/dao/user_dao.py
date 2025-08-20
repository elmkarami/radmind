from typing import Any, Dict, List, Optional

from sqlalchemy import select

from src.db import db
from src.db.models.user import Organization, OrganizationMember, User
from src.utils.pagination import Connection, paginate


async def get_all_users() -> List[User]:
    stmt = select(User)
    result = await db.session.execute(stmt)
    return result.scalars().all()


async def get_users_paginated(
    first: Optional[int] = None,
    after: Optional[str] = None,
    last: Optional[int] = None,
    before: Optional[str] = None,
) -> Connection[User]:
    return await paginate(
        model=User,
        first=first,
        after=after,
        last=last,
        before=before,
    )


async def get_user_by_id(user_id: int) -> Optional[User]:
    stmt = select(User).where(User.id == user_id)
    result = await db.session.execute(stmt)
    return result.scalar_one_or_none()


async def get_user_by_email(email: str) -> Optional[User]:
    stmt = select(User).where(User.email == email)
    result = await db.session.execute(stmt)
    return result.scalar_one_or_none()


async def get_users_by_organization_id(organization_id: int) -> List[User]:
    stmt = select(User).where(User.organization_id == organization_id)
    result = await db.session.execute(stmt)
    return result.scalars().all()


async def create_user(user_data: Dict[str, Any]) -> User:
    user = User(**user_data)
    if "password" in user_data:
        user.set_password(user_data["password"])
    db.session.add(user)
    await db.session.commit()
    await db.session.refresh(user)
    return user


async def update_user(user_id: int, user_data: Dict[str, Any]) -> Optional[User]:
    stmt = select(User).where(User.id == user_id)
    result = await db.session.execute(stmt)
    user = result.scalar_one_or_none()
    if user:
        for key, value in user_data.items():
            setattr(user, key, value)
        await db.session.commit()
        await db.session.refresh(user)
    return user


async def delete_user(user_id: int) -> bool:
    stmt = select(User).where(User.id == user_id)
    result = await db.session.execute(stmt)
    user = result.scalar_one_or_none()
    if user:
        await db.session.delete(user)
        await db.session.commit()
        return True
    return False


async def get_all_organizations() -> List[Organization]:
    stmt = select(Organization)
    result = await db.session.execute(stmt)
    return result.scalars().all()


async def get_organizations_paginated(
    first: Optional[int] = None,
    after: Optional[str] = None,
    last: Optional[int] = None,
    before: Optional[str] = None,
) -> Connection[Organization]:
    return await paginate(
        model=Organization,
        first=first,
        after=after,
        last=last,
        before=before,
    )


async def get_organization_by_id(organization_id: int) -> Optional[Organization]:
    stmt = select(Organization).where(Organization.id == organization_id)
    result = await db.session.execute(stmt)
    return result.scalar_one_or_none()


async def create_organization(org_data: Dict[str, Any]) -> Organization:
    organization = Organization(**org_data)
    db.session.add(organization)
    await db.session.commit()
    await db.session.refresh(organization)
    return organization


async def update_organization(
    organization_id: int, org_data: Dict[str, Any]
) -> Optional[Organization]:
    stmt = select(Organization).where(Organization.id == organization_id)
    result = await db.session.execute(stmt)
    organization = result.scalar_one_or_none()
    if organization:
        for key, value in org_data.items():
            setattr(organization, key, value)
        await db.session.commit()
        await db.session.refresh(organization)
    return organization


async def delete_organization(organization_id: int) -> bool:
    stmt = select(Organization).where(Organization.id == organization_id)
    result = await db.session.execute(stmt)
    organization = result.scalar_one_or_none()
    if organization:
        # First delete all organization members to avoid foreign key constraint violations
        members_stmt = select(OrganizationMember).where(
            OrganizationMember.organization_id == organization_id
        )
        members_result = await db.session.execute(members_stmt)
        members = members_result.scalars().all()

        for member in members:
            await db.session.delete(member)

        # Then delete the organization
        await db.session.delete(organization)
        await db.session.commit()
        return True
    return False


async def get_organization_members(organization_id: int):
    """Get all members of an organization"""
    stmt = select(OrganizationMember).where(
        OrganizationMember.organization_id == organization_id
    )
    result = await db.session.execute(stmt)
    return result.scalars().all()


async def get_user_organization_memberships(user_id: int):
    """Get all organization memberships for a user"""
    stmt = select(OrganizationMember).where(OrganizationMember.user_id == user_id)
    result = await db.session.execute(stmt)
    return result.scalars().all()


async def create_organization_member(user_id: int, organization_id: int, role: str):
    """Create an organization membership"""
    member = OrganizationMember(
        user_id=user_id, organization_id=organization_id, role=role
    )
    db.session.add(member)
    await db.session.commit()
    await db.session.refresh(member)
    return member


async def remove_organization_member(user_id: int, organization_id: int):
    """Remove a user from an organization"""
    stmt = select(OrganizationMember).where(
        OrganizationMember.user_id == user_id,
        OrganizationMember.organization_id == organization_id,
    )
    result = await db.session.execute(stmt)
    member = result.scalar_one_or_none()

    if member:
        await db.session.delete(member)
        await db.session.commit()
        return True
    return False


async def update_user_password_fields(user_id: int, **fields):
    """Update user password-related fields"""
    stmt = select(User).where(User.id == user_id)
    result = await db.session.execute(stmt)
    user = result.scalar_one_or_none()

    if user:
        for field, value in fields.items():
            setattr(user, field, value)
        await db.session.commit()
        await db.session.refresh(user)
    return user
