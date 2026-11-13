from decimal import Decimal
from typing import Any

from pydantic_ai_harness.spend import RedisSpendStore, SpendLimits
from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.enums import StatusType
from backend.common.exception import errors
from backend.common.pagination import paging_data
from backend.core.conf import settings
from backend.database.redis import redis_client
from backend.plugin.ai_buddy.dataclasses import CapabilityContext, CapabilityResult
from backend.plugin.fba_buddy_billing.crud.crud_budget import fba_buddy_billing_budget_dao
from backend.plugin.fba_buddy_billing.crud.crud_price import fba_buddy_billing_price_dao
from backend.plugin.fba_buddy_billing.enums import FbaBuddyBillingBudgetWindow
from backend.plugin.fba_buddy_billing.schema.budget import (
    CreateFbaBuddyBillingBudgetParam,
    GetFbaBuddyBillingBudgetDetail,
    UpdateFbaBuddyBillingBudgetParam,
)
from backend.plugin.fba_buddy_billing.utils.spend import build_spend_budgets, build_spend_price
from backend.utils.timezone import timezone

_SPEND_STORE = RedisSpendStore(
    client=redis_client,
    prefix=f'{settings.PLUGIN_REDIS_PREFIX}:ai-buddy-billing:spend',
)


class FbaBuddyBillingBudgetService:
    """AI Buddy 计费预算服务类"""

    @staticmethod
    async def get_list(
        *,
        db: AsyncSession,
        user_id: int | None,
        window: FbaBuddyBillingBudgetWindow | None,
        status: StatusType | None,
    ) -> dict[str, Any]:
        """
        分页获取计费预算

        :param db: 数据库会话
        :param user_id: 用户 ID
        :param window: 预算窗口
        :param status: 状态
        :return:
        """
        stmt = await fba_buddy_billing_budget_dao.get_select(
            user_id=user_id,
            window=window.value if window is not None else None,
            status=status.value if status is not None else None,
        )
        return await paging_data(db, stmt)

    async def create(
        self, *, db: AsyncSession, obj: CreateFbaBuddyBillingBudgetParam
    ) -> GetFbaBuddyBillingBudgetDetail:
        """
        创建计费预算

        :param db: 数据库会话
        :param obj: 创建参数
        :return:
        """
        self._validate_limits(usd_limit=obj.usd_limit, token_limit=obj.token_limit)
        existing = await fba_buddy_billing_budget_dao.get_by_user_window(
            db,
            user_id=obj.user_id,
            window=obj.window.value,
        )
        if existing is not None:
            raise errors.ConflictError(msg='该用户和预算窗口已存在配置')
        row = await fba_buddy_billing_budget_dao.create(db, obj)
        return GetFbaBuddyBillingBudgetDetail.model_validate(row)

    async def update(
        self,
        *,
        db: AsyncSession,
        pk: int,
        obj: UpdateFbaBuddyBillingBudgetParam,
    ) -> GetFbaBuddyBillingBudgetDetail:
        """
        更新计费预算

        :param db: 数据库会话
        :param pk: 预算 ID
        :param obj: 更新参数
        :return:
        """
        current = await fba_buddy_billing_budget_dao.get(db, pk)
        if current is None:
            raise errors.NotFoundError(msg='计费预算不存在')
        payload = obj.model_dump(exclude_unset=True)
        values: dict[str, Any] = {}
        for field in ('usd_limit', 'token_limit', 'warn_at'):
            if field in payload:
                values[field] = payload[field]
        if obj.status is not None:
            values['status'] = obj.status.value
        usd_limit = values.get('usd_limit', current.usd_limit)
        token_limit = values.get('token_limit', current.token_limit)
        self._validate_limits(usd_limit=usd_limit, token_limit=token_limit)
        if values:
            await fba_buddy_billing_budget_dao.update(db, pk=pk, values=values)
        return GetFbaBuddyBillingBudgetDetail.model_validate(await fba_buddy_billing_budget_dao.get(db, pk))

    @staticmethod
    async def delete(*, db: AsyncSession, pk: int) -> int:
        """
        删除计费预算

        :param db: 数据库会话
        :param pk: 预算 ID
        :return:
        """
        count = await fba_buddy_billing_budget_dao.delete(db, pk=pk)
        if not count:
            raise errors.NotFoundError(msg='计费预算不存在')
        return count

    @staticmethod
    async def build_spend_limits(*, ctx: CapabilityContext) -> CapabilityResult:
        """
        构建用户预算对应的 Harness SpendLimits

        :param ctx: 能力构建上下文
        :return:
        """
        if ctx.user_id is None:
            return CapabilityResult(capability=None)
        budgets = await fba_buddy_billing_budget_dao.get_all_by_user(db=ctx.db, user_id=ctx.user_id)
        if not budgets:
            return CapabilityResult(capability=None)
        prices = await fba_buddy_billing_price_dao.get_all_active(db=ctx.db, effective_time=timezone.now())
        primary_model_id = getattr(ctx.forwarded_props, 'model_id', None)
        return CapabilityResult(
            capability=SpendLimits(
                budgets=build_spend_budgets(budgets=budgets),
                store=_SPEND_STORE,
                price=build_spend_price(prices=prices, primary_model_id=primary_model_id),
                on_unpriced='zero',
            )
        )

    @staticmethod
    def _validate_limits(*, usd_limit: Decimal | None, token_limit: int | None) -> None:
        """
        校验预算至少配置一个上限

        :param usd_limit: USD 上限
        :param token_limit: token 上限
        :return:
        """
        if usd_limit is None and token_limit is None:
            raise errors.RequestError(msg='USD 和 token 上限至少配置一个')


fba_buddy_billing_budget_service: FbaBuddyBillingBudgetService = FbaBuddyBillingBudgetService()
