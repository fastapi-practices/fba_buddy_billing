from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.exception import errors
from backend.common.pagination import paging_data
from backend.plugin.fba_buddy_billing.crud.crud_price import fba_buddy_billing_price_dao
from backend.plugin.fba_buddy_billing.schema.price import (
    CreateFbaBuddyBillingPriceParam,
    GetFbaBuddyBillingPriceDetail,
)
from backend.utils.timezone import timezone


class FbaBuddyBillingPriceService:
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
        stmt = await fba_buddy_billing_price_dao.get_select(
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
    ) -> list[GetFbaBuddyBillingPriceDetail]:
        """
        获取所有生效中的价格

        :param db: 数据库会话
        :param provider_id: 供应商 ID
        :param model_id: 模型 ID
        :return:
        """
        rows = await fba_buddy_billing_price_dao.get_all_active(
            db,
            provider_id=provider_id,
            model_id=model_id,
            effective_time=timezone.now(),
        )
        return [GetFbaBuddyBillingPriceDetail.model_validate(row) for row in rows]

    @staticmethod
    async def create(*, db: AsyncSession, obj: CreateFbaBuddyBillingPriceParam) -> GetFbaBuddyBillingPriceDetail:
        """
        创建价格版本并关闭上一版价格

        :param db: 数据库会话
        :param obj: 创建参数
        :return:
        """
        if obj.effective_to is not None and obj.effective_to <= obj.effective_from:
            raise errors.RequestError(msg='价格失效时间必须晚于生效时间')
        current = await fba_buddy_billing_price_dao.get_active(
            db,
            provider_id=obj.provider_id,
            model_id=obj.model_id,
            effective_time=obj.effective_from,
        )
        if current is not None and current.effective_from >= obj.effective_from:
            raise errors.ConflictError(msg='新价格生效时间必须晚于当前生效价格')
        if current is not None:
            await fba_buddy_billing_price_dao.close_active(
                db,
                provider_id=obj.provider_id,
                model_id=obj.model_id,
                effective_time=obj.effective_from,
            )
        row = await fba_buddy_billing_price_dao.create(db, obj)
        return GetFbaBuddyBillingPriceDetail.model_validate(row)


fba_buddy_billing_price_service: FbaBuddyBillingPriceService = FbaBuddyBillingPriceService()
