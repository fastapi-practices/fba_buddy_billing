from collections.abc import Sequence
from datetime import datetime
from typing import Any

from sqlalchemy import Select, or_, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.plugin.ai_buddy_billing.model import AIBuddyBillingPrice
from backend.plugin.ai_buddy_billing.schema.price import CreateAIBuddyBillingPriceParam


class CRUDAIBuddyBillingPrice(CRUDPlus[AIBuddyBillingPrice]):
    """AI Buddy 计费价格数据库操作类"""

    async def get(self, db: AsyncSession, pk: int) -> AIBuddyBillingPrice | None:
        """
        获取价格记录

        :param db: 数据库会话
        :param pk: 价格 ID
        :return:
        """
        return await self.select_model(db, pk, deleted=0)

    async def get_select(
        self,
        *,
        provider_id: int | None,
        model_id: str | None,
        active: bool | None,
        effective_time: datetime | None = None,
    ) -> Select:
        """
        获取价格查询表达式

        :param provider_id: 供应商 ID
        :param model_id: 模型 ID
        :param active: 是否只查询生效中的价格
        :param effective_time: 生效判断时间
        :return:
        """
        filters = {'deleted': 0}
        if provider_id is not None:
            filters['provider_id'] = provider_id
        if model_id is not None:
            filters['model_id'] = model_id
        whereclause = ()
        if active:
            at = effective_time
            whereclause = (
                self.model.effective_from <= at,
                or_(self.model.effective_to.is_(None), self.model.effective_to > at),
            )
        return await self.select_order(
            ['effective_from', 'id'],
            ['desc', 'desc'],
            *whereclause,
            **filters,
        )

    async def get_active(
        self,
        db: AsyncSession,
        *,
        provider_id: int,
        model_id: str,
        effective_time: datetime,
    ) -> AIBuddyBillingPrice | None:
        """
        获取指定时间生效的价格

        :param db: 数据库会话
        :param provider_id: 供应商 ID
        :param model_id: 模型 ID
        :param effective_time: 生效判断时间
        :return:
        """
        rows = await self.select_models_order(
            db,
            'effective_from',
            'desc',
            self.model.effective_from <= effective_time,
            or_(self.model.effective_to.is_(None), self.model.effective_to > effective_time),
            limit=1,
            provider_id=provider_id,
            model_id=model_id,
            deleted=0,
        )
        return rows[0] if rows else None

    async def get_all_active(
        self,
        db: AsyncSession,
        *,
        provider_id: int | None = None,
        model_id: str | None = None,
        effective_time: datetime | None = None,
    ) -> Sequence[AIBuddyBillingPrice]:
        """
        获取当前生效的价格列表

        :param db: 数据库会话
        :param provider_id: 供应商 ID
        :param model_id: 模型 ID
        :param effective_time: 生效判断时间
        :return:
        """
        filters = {'deleted': 0}
        if provider_id is not None:
            filters['provider_id'] = provider_id
        if model_id is not None:
            filters['model_id'] = model_id
        whereclause = ()
        if effective_time is not None:
            whereclause = (
                self.model.effective_from <= effective_time,
                or_(self.model.effective_to.is_(None), self.model.effective_to > effective_time),
            )
        return await self.select_models_order(
            db,
            ['provider_id', 'model_id'],
            ['asc', 'asc'],
            *whereclause,
            **filters,
        )

    async def close_active(
        self,
        db: AsyncSession,
        *,
        provider_id: int,
        model_id: str,
        effective_time: datetime,
    ) -> None:
        """
        关闭上一版生效价格

        :param db: 数据库会话
        :param provider_id: 供应商 ID
        :param model_id: 模型 ID
        :param effective_time: 新价格生效时间
        :return:
        """
        await db.execute(
            update(self.model)
            .where(
                self.model.deleted == 0,
                self.model.provider_id == provider_id,
                self.model.model_id == model_id,
                self.model.effective_from <= effective_time,
                or_(self.model.effective_to.is_(None), self.model.effective_to > effective_time),
            )
            .values(effective_to=effective_time)
        )

    async def update(self, db: AsyncSession, *, pk: int, values: dict[str, Any]) -> int:
        """
        更新价格记录

        :param db: 数据库会话
        :param pk: 价格 ID
        :param values: 更新字段
        :return:
        """
        return await self.update_model_by_column(db, values, id=pk, deleted=0)

    async def create(self, db: AsyncSession, obj: CreateAIBuddyBillingPriceParam) -> AIBuddyBillingPrice:
        """
        创建价格记录

        :param db: 数据库会话
        :param obj: 创建参数
        :return:
        """
        return await self.create_model(db, obj, flush=True)


ai_buddy_billing_price_dao: CRUDAIBuddyBillingPrice = CRUDAIBuddyBillingPrice(AIBuddyBillingPrice)
