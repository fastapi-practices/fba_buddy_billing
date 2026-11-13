from decimal import Decimal

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.plugin.ai_buddy_billing.model import AIBuddyBillingAccount
from backend.plugin.ai_buddy_billing.schema.account import CreateAIBuddyBillingAccountParam


class CRUDAIBuddyBillingAccount(CRUDPlus[AIBuddyBillingAccount]):
    """AI Buddy 计费账户数据库操作类"""

    async def get_select(self, *, user_id: int | None) -> Select:
        """
        获取计费账户查询表达式

        :param user_id: 用户 ID
        :return:
        """
        filters = {'deleted': 0}
        if user_id is not None:
            filters['user_id'] = user_id
        return await self.select_order('user_id', 'asc', **filters)

    async def get_by_user(self, db: AsyncSession, user_id: int) -> AIBuddyBillingAccount | None:
        """
        获取用户计费账户

        :param db: 数据库会话
        :param user_id: 用户 ID
        :return:
        """
        return await self.select_model_by_column(db, user_id=user_id, deleted=0)

    async def get_by_user_for_update(self, db: AsyncSession, user_id: int) -> AIBuddyBillingAccount | None:
        """
        锁定并获取用户计费账户

        :param db: 数据库会话
        :param user_id: 用户 ID
        :return:
        """
        stmt = await self.select(user_id=user_id, deleted=0)
        return (await db.execute(stmt.with_for_update().limit(1))).scalar_one_or_none()

    async def create(self, db: AsyncSession, obj: CreateAIBuddyBillingAccountParam) -> AIBuddyBillingAccount:
        """
        创建计费账户

        :param db: 数据库会话
        :param obj: 创建参数
        :return:
        """
        return await self.create_model(db, obj, flush=True)

    async def update_balance(
        self,
        db: AsyncSession,
        *,
        pk: int,
        balance: Decimal,
        expected_version: int,
    ) -> int:
        """
        更新账户余额

        :param db: 数据库会话
        :param pk: 账户 ID
        :param balance: 最新余额
        :param expected_version: 预期版本号
        :return:
        """
        return await self.update_model_by_column(
            db,
            {'balance': balance, 'version': self.model.version + 1},
            id=pk,
            version=expected_version,
            deleted=0,
        )


ai_buddy_billing_account_dao: CRUDAIBuddyBillingAccount = CRUDAIBuddyBillingAccount(AIBuddyBillingAccount)
