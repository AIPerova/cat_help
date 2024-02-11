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
    obj_1: ModelType, obj_2: CRUDType, session: AsyncSession
) -> ModelType:
    """Инвестирование."""

    all_obj = await obj_2.get_multi_open(session)
    for obj in all_obj:
        money_for_project = obj_1.full_amount - obj_1.invested_amount
        money_for_donate = obj.full_amount - obj.invested_amount
        to_donate = min(money_for_project, money_for_donate)
        obj.invested_amount += to_donate
        obj_1.invested_amount += to_donate
        if obj.full_amount == obj.invested_amount:
            close_project(obj)
        if obj_1.full_amount == obj_1.invested_amount:
            close_project(obj_1)
            break
    session.add_all((*all_obj, obj_1))
    await session.commit()
    await session.refresh(obj_1)
    return obj_1