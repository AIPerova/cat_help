from datetime import datetime
from typing import TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import Base
from app.crud.base import CRUDBase

ModelType = TypeVar('ModelType', bound=Base)
CRUDType = TypeVar('CRUDType', bound=CRUDBase)


def close_project(obj: ModelType) -> None:
    """Закрытие сбора/доната, добавление даты закрытия."""

    obj.fully_invested = True
    obj.close_date = datetime.now()


async def donate(
    from_invest: ModelType, to_invest: CRUDType, session: AsyncSession
) -> ModelType:
    """Инвестирование."""

    all_obj = await to_invest.get_multi_open(session)
    for obj in all_obj:
        money_for_project = from_invest.full_amount - from_invest.invested_amount
        money_for_donate = obj.full_amount - obj.invested_amount
        to_donate = min(money_for_project, money_for_donate)
        obj.invested_amount += to_donate
        from_invest.invested_amount += to_donate
        if obj.full_amount == obj.invested_amount:
            close_project(obj)
        if from_invest.full_amount == from_invest.invested_amount:
            close_project(from_invest)
            break
    session.add_all((*all_obj, from_invest))
    await session.commit()
    await session.refresh(from_invest)
    return from_invest