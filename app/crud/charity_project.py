from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud.base import CRUDBase
from app.models import CharityProject


class CRUDCharity(CRUDBase[CharityProject]):

    async def get_project_by_name(
        self,
        project_name: str,
        session: AsyncSession,
    ) -> Optional[int]:
        """Возвращает проект по имени."""

        project = await session.execute(
            select(CharityProject.id).where(
                CharityProject.name == project_name,
            )
        )

        return project.scalars().first()

    async def get(
        self,
        obj_id: int,
        session: AsyncSession,
    ) -> Optional[CharityProject]:
        """Возвращает проект."""

        project = await session.execute(
            select(self.model).where(
                self.model.id == obj_id,
            )
        )
        return project.scalars().first()


charity_crud = CRUDCharity(CharityProject)