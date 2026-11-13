from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.plugin.ai_buddy_billing.model import AIBuddyBillingLedger
from backend.plugin.ai_buddy_billing.schema.ledger import CreateAIBuddyBillingLedgerParam


class CRUDAIBuddyBillingLedger(CRUDPlus[AIBuddyBillingLedger]):
    """AI Buddy 用量账本数据库操作类"""

    async def get_by_price(self, db: AsyncSession, price_id: int) -> AIBuddyBillingLedger | None:
        """
        获取使用指定价格的账本记录

        :param db: 数据库会话
        :param price_id: 价格 ID
        :return:
        """
        return await self.select_model_by_column(db, price_id=price_id, deleted=0)

    async def get_select(
        self,
        *,
        user_id: int | None,
        conversation_id: str | None,
        provider_id: int | None,
        model_id: str | None,
        status: str | None,
        start_time: datetime | None,
        end_time: datetime | None,
    ) -> Select:
        """
        获取账本查询表达式

        :param query: 查询参数
        :return:
        """
        filters = {'deleted': 0}
        if user_id is not None:
            filters['user_id'] = user_id
        if conversation_id is not None:
            filters['conversation_id'] = conversation_id
        if provider_id is not None:
            filters['provider_id'] = provider_id
        if model_id is not None:
            filters['model_id'] = model_id
        if status is not None:
            filters['status'] = status
        if start_time is not None:
            filters['usage_time__ge'] = start_time
        if end_time is not None:
            filters['usage_time__le'] = end_time
        return await self.select_order(['usage_time', 'id'], ['desc', 'desc'], **filters)

    async def get_summary(
        self,
        db: AsyncSession,
        *,
        user_id: int | None,
        start_time: datetime | None,
        end_time: datetime | None,
    ) -> dict[str, Any]:
        """
        汇总账本用量和费用

        :param db: 数据库会话
        :param user_id: 用户 ID
        :param start_time: 开始时间
        :param end_time: 结束时间
        :return:
        """
        stmt = select(
            func.count(self.model.id),
            func.coalesce(func.sum(self.model.input_tokens), 0),
            func.coalesce(func.sum(self.model.output_tokens), 0),
            func.coalesce(func.sum(self.model.cache_read_tokens), 0),
            func.coalesce(func.sum(self.model.cache_write_tokens), 0),
            func.coalesce(func.sum(self.model.generated_images), 0),
            func.coalesce(func.sum(self.model.provider_cost), Decimal(0)),
            func.coalesce(func.sum(self.model.billed_cost), Decimal(0)),
        ).where(self.model.deleted == 0)
        if user_id is not None:
            stmt = stmt.where(self.model.user_id == user_id)
        if start_time is not None:
            stmt = stmt.where(self.model.usage_time >= start_time)
        if end_time is not None:
            stmt = stmt.where(self.model.usage_time <= end_time)
        row = (await db.execute(stmt)).one()
        return {
            'usage_count': row[0],
            'input_tokens': row[1],
            'output_tokens': row[2],
            'cache_read_tokens': row[3],
            'cache_write_tokens': row[4],
            'generated_images': row[5],
            'provider_cost': row[6],
            'billed_cost': row[7],
        }

    async def create(self, db: AsyncSession, obj: CreateAIBuddyBillingLedgerParam) -> AIBuddyBillingLedger:
        """
        创建账本记录

        :param db: 数据库会话
        :param obj: 创建参数
        :return:
        """
        return await self.create_model(db, obj, flush=True)


ai_buddy_billing_ledger_dao: CRUDAIBuddyBillingLedger = CRUDAIBuddyBillingLedger(AIBuddyBillingLedger)
