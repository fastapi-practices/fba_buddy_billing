from collections.abc import Sequence
from typing import Any

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.plugin.fba_buddy_billing.model import FbaBuddyBillingBudget
from backend.plugin.fba_buddy_billing.schema.budget import CreateFbaBuddyBillingBudgetParam
from backend.utils.timezone import timezone


class CRUDFbaBuddyBillingBudget(CRUDPlus[FbaBuddyBillingBudget]):
    """AI Buddy 计费预算数据库操作类"""

    async def get(self, db: AsyncSession, pk: int) -> FbaBuddyBillingBudget | None:
        """
        获取预算记录

        :param db: 数据库会话
        :param pk: 预算 ID
        :return:
        """
        return await self.select_model(db, pk, deleted=0)

    async def get_select(
        self,
        *,
        user_id: int | None,
        window: str | None,
        status: int | None,
    ) -> Select:
        """
        获取预算查询表达式

        :param user_id: 用户 ID
        :param window: 预算窗口
        :param status: 状态
        :return:
        """
        filters = {'deleted': 0}
        if user_id is not None:
            filters['user_id'] = user_id
        if window is not None:
            filters['window'] = window
        if status is not None:
            filters['status'] = status
        return await self.select_order(['user_id', 'window'], ['asc', 'asc'], **filters)

    async def get_all_by_user(
        self,
        db: AsyncSession,
        *,
        user_id: int,
    ) -> Sequence[FbaBuddyBillingBudget]:
        """
        获取用户启用的预算

        :param db: 数据库会话
        :param user_id: 用户 ID
        :return:
        """
        return await self.select_models_order(
            db,
            'window',
            'asc',
            deleted=0,
            user_id=user_id,
            status=1,
        )

    async def get_by_user_window(
        self,
        db: AsyncSession,
        *,
        user_id: int,
        window: str,
    ) -> FbaBuddyBillingBudget | None:
        """
        获取用户指定窗口的预算

        :param db: 数据库会话
        :param user_id: 用户 ID
        :param window: 预算窗口
        :return:
        """
        return await self.select_model_by_column(db, user_id=user_id, window=window, deleted=0)

    async def create(self, db: AsyncSession, obj: CreateFbaBuddyBillingBudgetParam) -> FbaBuddyBillingBudget:
        """
        创建预算记录

        :param db: 数据库会话
        :param obj: 创建参数
        :return:
        """
        return await self.create_model(db, obj, flush=True)

    async def update(self, db: AsyncSession, *, pk: int, values: dict[str, Any]) -> int:
        """
        更新预算记录

        :param db: 数据库会话
        :param pk: 预算 ID
        :param values: 更新字段
        :return:
        """
        return await self.update_model_by_column(db, values, id=pk, deleted=0)

    async def delete(self, db: AsyncSession, *, pk: int) -> int:
        """
        删除预算记录

        :param db: 数据库会话
        :param pk: 预算 ID
        :return:
        """
        return await self.delete_model_by_column(
            db,
            logical_deletion=True,
            deleted_flag_column='deleted',
            deleted_flag_value=self.model.id,
            deleted_at_column='deleted_time',
            deleted_at_factory=timezone.now,
            id=pk,
            deleted=0,
        )


fba_buddy_billing_budget_dao: CRUDFbaBuddyBillingBudget = CRUDFbaBuddyBillingBudget(FbaBuddyBillingBudget)
