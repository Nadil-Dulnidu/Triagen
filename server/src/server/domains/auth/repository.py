"""PullSense Server — Auth: Data access layer for users and organizations."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from server.domains.auth.models import Organization, OrganizationMembership, User
from server.infrastructure import get_logger

logger = get_logger(__name__)


class UserRepository:
    """Data access for User entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, user_id: str) -> User | None:
        return await self._session.get(User, user_id)

    async def get_by_clerk_id(self, clerk_user_id: str) -> User | None:
        stmt = select(User).where(User.clerk_user_id == clerk_user_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        stmt = select(User).where(User.email == email)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        clerk_user_id: str,
        email: str,
        username: str | None = None,
        display_name: str | None = None,
        avatar_url: str | None = None,
        github_username: str | None = None,
    ) -> User:
        user = User(
            clerk_user_id=clerk_user_id,
            email=email,
            username=username,
            display_name=display_name,
            avatar_url=avatar_url,
            github_username=github_username,
        )
        self._session.add(user)
        await self._session.flush()
        logger.info("user_created", clerk_user_id=clerk_user_id, email=email)
        return user

    async def update(self, user: User, **kwargs: object) -> User:
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        await self._session.flush()
        logger.info("user_updated", user_id=user.id)
        return user

    async def soft_delete(self, user: User) -> None:
        user.is_active = False
        await self._session.flush()
        logger.info("user_soft_deleted", user_id=user.id)


class OrganizationRepository:
    """Data access for Organization entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, org_id: str) -> Organization | None:
        return await self._session.get(Organization, org_id)

    async def get_by_clerk_id(self, clerk_org_id: str) -> Organization | None:
        stmt = select(Organization).where(Organization.clerk_org_id == clerk_org_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        clerk_org_id: str,
        name: str,
        slug: str | None = None,
    ) -> Organization:
        org = Organization(
            clerk_org_id=clerk_org_id,
            name=name,
            slug=slug,
        )
        self._session.add(org)
        await self._session.flush()
        logger.info("organization_created", clerk_org_id=clerk_org_id, name=name)
        return org

    async def update(self, org: Organization, **kwargs: object) -> Organization:
        for key, value in kwargs.items():
            if hasattr(org, key):
                setattr(org, key, value)
        await self._session.flush()
        logger.info("organization_updated", org_id=org.id)
        return org

    async def get_user_organizations(self, user_id: str) -> list[Organization]:
        stmt = (
            select(Organization)
            .join(OrganizationMembership)
            .where(OrganizationMembership.user_id == user_id)
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())


class MembershipRepository:
    """Data access for OrganizationMembership entities."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_membership(
        self, user_id: str, organization_id: str
    ) -> OrganizationMembership | None:
        stmt = select(OrganizationMembership).where(
            OrganizationMembership.user_id == user_id,
            OrganizationMembership.organization_id == organization_id,
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def create(
        self,
        user_id: str,
        organization_id: str,
        role: str = "member",
        clerk_membership_id: str | None = None,
    ) -> OrganizationMembership:
        membership = OrganizationMembership(
            user_id=user_id,
            organization_id=organization_id,
            role=role,
            clerk_membership_id=clerk_membership_id,
        )
        self._session.add(membership)
        await self._session.flush()
        logger.info(
            "membership_created",
            user_id=user_id,
            org_id=organization_id,
            role=role,
        )
        return membership

    async def get_org_members(self, organization_id: str) -> list[OrganizationMembership]:
        stmt = select(OrganizationMembership).where(
            OrganizationMembership.organization_id == organization_id
        )
        result = await self._session.execute(stmt)
        return list(result.scalars().all())

    async def delete_by_clerk_id(self, clerk_membership_id: str) -> None:
        stmt = select(OrganizationMembership).where(
            OrganizationMembership.clerk_membership_id == clerk_membership_id
        )
        result = await self._session.execute(stmt)
        membership = result.scalar_one_or_none()
        if membership:
            await self._session.delete(membership)
            await self._session.flush()
