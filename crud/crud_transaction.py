from datetime import datetime

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.plugin.fba_buddy_billing.model import FbaBuddyBillingTransaction
from backend.plugin.fba_buddy_billing.schema.transaction import CreateFbaBuddyBillingTransactionParam


class CRUDFbaBuddyBillingTransaction(CRUDPlus[FbaBuddyBillingTransaction]):
    """AI Buddy 计费流水数据库操作类"""

    async def get_select(
        self,
        *,
        user_id: int | None,
        transaction_type: str | None,
        start_time: datetime | None,
        end_time: datetime | None,
    ) -> Select:
        """
        获取流水查询表达式

        :param query: 查询参数
        :return:
        """
        filters = {'deleted': 0}
        if user_id is not None:
            filters['user_id'] = user_id
        if transaction_type is not None:
            filters['transaction_type'] = transaction_type
        if start_time is not None:
            filters['created_time__ge'] = start_time
        if end_time is not None:
            filters['created_time__le'] = end_time
        return await self.select_order('id', 'desc', **filters)

    async def create(self, db: AsyncSession, obj: CreateFbaBuddyBillingTransactionParam) -> FbaBuddyBillingTransaction:
        """
        创建计费流水

        :param db: 数据库会话
        :param obj: 创建参数
        :return:
        """
        return await self.create_model(db, obj, flush=True)


fba_buddy_billing_transaction_dao: CRUDFbaBuddyBillingTransaction = CRUDFbaBuddyBillingTransaction(
    FbaBuddyBillingTransaction
)
