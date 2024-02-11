from datetime import datetime
from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import Base
from app.crud.base import CRUDBase

ModelType = TypeVar('ModelType', bound=Base)
CRUDType = TypeVar('CRUDType', bound=CRUDBase)


def close_project(obj: ModelType) -> None:
    """Закрытие сбора, добавление даты закрытия."""

    obj.fully_invested = True
    obj.close_date = datetime.now()


async def donate(
    project: ModelType, all_donation: CRUDType, session: AsyncSession
) -> ModelType:
    """Инвестирование."""

    donations = await all_donation.get_multi_open(session)
    for donation in donations:
        money_for_project = project.full_amount - project.invested_amount
        money_for_donate = donation.full_amount - donation.invested_amount
        to_donate = min(money_for_project, money_for_donate)
        donation.invested_amount += to_donate
        project.invested_amount += to_donate
        if donation.full_amount == donation.invested_amount:
            close_project(donation)
        if project.full_amount == project.invested_amount:
            close_project(project)
            break
    session.add_all((*donations, project))
    await session.commit()
    await session.refresh(project)
    return project