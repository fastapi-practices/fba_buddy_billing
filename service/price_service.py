from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.exception import errors
from backend.common.pagination import paging_data
from backend.plugin.ai_buddy_billing.crud.crud_ledger import ai_buddy_billing_ledger_dao
from backend.plugin.ai_buddy_billing.crud.crud_price import ai_buddy_billing_price_dao
from backend.plugin.ai_buddy_billing.schema.price import (
    CreateAIBuddyBillingPriceParam,
    GetAIBuddyBillingPriceDetail,
    UpdateAIBuddyBillingPriceParam,
)
from backend.utils.timezone import timezone


class AIBuddyBillingPriceService:
    """AI Buddy 计费价格服务类"""

    @staticmethod
    async def get_list(
        *,
        db: AsyncSession,
        provider_id: int | None,
        model_id: str | None,
        active: bool | None,
    ) -> dict[str, Any]:
        """
        分页获取价格

        :param db: 数据库会话
        :param provider_id: 供应商 ID
        :param model_id: 模型 ID
        :param active: 是否只查询生效中的价格
        :return:
        """
        effective_time = timezone.now() if active else None
        stmt = await ai_buddy_billing_price_dao.get_select(
            provider_id=provider_id,
            model_id=model_id,
            active=active,
            effective_time=effective_time,
        )
        return await paging_data(db, stmt)

    @staticmethod
    async def get_all(
        *,
        db: AsyncSession,
        provider_id: int | None = None,
        model_id: str | None = None,
    ) -> list[GetAIBuddyBillingPriceDetail]:
        """
        获取所有生效中的价格

        :param db: 数据库会话
        :param provider_id: 供应商 ID
        :param model_id: 模型 ID
        :return:
        """
        rows = await ai_buddy_billing_price_dao.get_all_active(
            db,
            provider_id=provider_id,
            model_id=model_id,
            effective_time=timezone.now(),
        )
        return [GetAIBuddyBillingPriceDetail.model_validate(row) for row in rows]

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateAIBuddyBillingPriceParam) -> GetAIBuddyBillingPriceDetail:
        """
        创建价格版本并关闭上一版价格

        :param db: 数据库会话
        :param obj: 创建参数
        :return:
        """
        if obj.effective_to is not None and obj.effective_to <= obj.effective_from:
            raise errors.RequestError(msg='价格失效时间必须晚于生效时间')
        current = await ai_buddy_billing_price_dao.get_active(
            db,
            provider_id=obj.provider_id,
            model_id=obj.model_id,
            effective_time=obj.effective_from,
        )
        if current is not None and current.effective_from >= obj.effective_from:
            raise errors.ConflictError(msg='新价格生效时间必须晚于当前生效价格')
        if current is not None:
            await ai_buddy_billing_price_dao.close_active(
                db,
                provider_id=obj.provider_id,
                model_id=obj.model_id,
                effective_time=obj.effective_from,
            )
        row = await ai_buddy_billing_price_dao.create(db, obj)
        return GetAIBuddyBillingPriceDetail.model_validate(row)

    @staticmethod
    async def update(
        *,
        db: AsyncSession,
        pk: int,
        obj: UpdateAIBuddyBillingPriceParam,
    ) -> GetAIBuddyBillingPriceDetail:
        """
        更新价格版本

        :param db: 数据库会话
        :param pk: 价格 ID
        :param obj: 更新参数
        :return:
        """
        price = await ai_buddy_billing_price_dao.get(db, pk)
        if price is None:
            raise errors.NotFoundError(msg='计费价格不存在')
        if obj.effective_to is not None and obj.effective_to <= price.effective_from:
            raise errors.RequestError(msg='价格失效时间必须晚于生效时间')
        values = obj.model_dump(exclude_unset=True)
        if values:
            await ai_buddy_billing_price_dao.update(db, pk=pk, values=values)
        return GetAIBuddyBillingPriceDetail.model_validate(await ai_buddy_billing_price_dao.get(db, pk))

    @staticmethod
    async def delete(*, db: AsyncSession, pk: int) -> int:
        """
        删除价格版本

        :param db: 数据库会话
        :param pk: 价格 ID
        :return:
        """
        price = await ai_buddy_billing_price_dao.get(db, pk)
        if price is None:
            raise errors.NotFoundError(msg='计费价格不存在')
        if await ai_buddy_billing_ledger_dao.get_by_price(db, price_id=pk) is not None:
            raise errors.RequestError(msg='价格已用于结算，请改为设置失效时间')
        return await ai_buddy_billing_price_dao.delete(db, pk=pk)


ai_buddy_billing_price_service: AIBuddyBillingPriceService = AIBuddyBillingPriceService()
