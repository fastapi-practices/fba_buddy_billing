from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.exception import errors
from backend.common.pagination import paging_data
from backend.core.conf import settings
from backend.database.db import uuid4_str
from backend.plugin.ai_buddy.dataclasses import CapabilityContext, CapabilityResult
from backend.plugin.ai_buddy_billing.agent.balance_guard import (
    InsufficientBalanceGuard,
    has_insufficient_balance,
)
from backend.plugin.ai_buddy_billing.crud.crud_account import ai_buddy_billing_account_dao
from backend.plugin.ai_buddy_billing.crud.crud_transaction import ai_buddy_billing_transaction_dao
from backend.plugin.ai_buddy_billing.enums import AIBuddyBillingTransactionType
from backend.plugin.ai_buddy_billing.schema.account import (
    CreateAIBuddyBillingAccountParam,
    CreateAIBuddyBillingAdjustmentParam,
    CreateAIBuddyBillingRechargeParam,
    GetAIBuddyBillingAccountDetail,
)
from backend.plugin.ai_buddy_billing.schema.transaction import CreateAIBuddyBillingTransactionParam


class AIBuddyBillingAccountService:
    """AI Buddy 计费账户服务类"""

    @staticmethod
    async def get(*, db: AsyncSession, user_id: int) -> GetAIBuddyBillingAccountDetail:
        """
        获取计费账户

        :param db: 数据库会话
        :param user_id: 用户 ID
        :return:
        """
        account = await ai_buddy_billing_account_dao.get_by_user(db, user_id)
        if account is None:
            raise errors.NotFoundError(msg='计费账户不存在')
        return GetAIBuddyBillingAccountDetail.model_validate(account)

    @staticmethod
    async def build_balance_guard(*, ctx: CapabilityContext) -> CapabilityResult:
        """
        构建余额不足校验能力

        :param ctx: 能力构建上下文
        :return:
        """
        if not settings.AI_BUDDY_BILLING_BALANCE_GUARD_ENABLED:
            return CapabilityResult(capability=None)
        if ctx.user_id is None:
            return CapabilityResult(capability=None)
        if ctx.is_superuser and settings.AI_BUDDY_BILLING_BALANCE_GUARD_SKIP_SUPERUSER:
            return CapabilityResult(capability=None)
        account = await ai_buddy_billing_account_dao.get_by_user(ctx.db, ctx.user_id)
        if account is None:
            return CapabilityResult(capability=None)
        minimum = settings.AI_BUDDY_BILLING_BALANCE_MIN_USD
        if not has_insufficient_balance(account.balance, minimum=minimum):
            return CapabilityResult(capability=None)
        return CapabilityResult(capability=InsufficientBalanceGuard(balance=account.balance, minimum=minimum))

    @staticmethod
    async def get_list(*, db: AsyncSession, user_id: int | None) -> dict[str, Any]:
        """
        分页获取计费账户

        :param db: 数据库会话
        :param user_id: 用户 ID
        :return:
        """
        stmt = await ai_buddy_billing_account_dao.get_select(user_id=user_id)
        return await paging_data(db, stmt)

    @staticmethod
    async def get_transaction_list(
        *,
        db: AsyncSession,
        user_id: int | None,
        transaction_type: str | None,
        start_time: datetime | None,
        end_time: datetime | None,
    ) -> dict[str, Any]:
        """
        分页获取计费流水

        :param db: 数据库会话
        :param user_id: 用户 ID
        :param transaction_type: 流水类型
        :param start_time: 开始时间
        :param end_time: 结束时间
        :return:
        """
        stmt = await ai_buddy_billing_transaction_dao.get_select(
            user_id=user_id,
            transaction_type=transaction_type,
            start_time=start_time,
            end_time=end_time,
        )
        return await paging_data(db, stmt)

    async def recharge(
        self, *, db: AsyncSession, obj: CreateAIBuddyBillingRechargeParam
    ) -> GetAIBuddyBillingAccountDetail:
        """
        为用户充值

        :param db: 数据库会话
        :param obj: 充值参数
        :return:
        """
        return await self._apply_transaction(
            db=db,
            user_id=obj.user_id,
            amount=obj.amount,
            transaction_type=AIBuddyBillingTransactionType.recharge,
            remark=obj.remark,
        )

    async def adjust(
        self, *, db: AsyncSession, obj: CreateAIBuddyBillingAdjustmentParam
    ) -> GetAIBuddyBillingAccountDetail:
        """
        调整用户余额

        :param db: 数据库会话
        :param obj: 调整参数
        :return:
        """
        if obj.amount == 0:
            raise errors.RequestError(msg='调整金额不能为零')
        return await self._apply_transaction(
            db=db,
            user_id=obj.user_id,
            amount=obj.amount,
            transaction_type=AIBuddyBillingTransactionType.adjust,
            remark=obj.remark,
        )

    @staticmethod
    async def _apply_transaction(
        *,
        db: AsyncSession,
        user_id: int,
        amount: Decimal,
        transaction_type: AIBuddyBillingTransactionType,
        remark: str | None,
    ) -> GetAIBuddyBillingAccountDetail:
        """
        写入账户余额流水

        :param db: 数据库会话
        :param user_id: 用户 ID
        :param amount: 变动金额
        :param transaction_type: 流水类型
        :param remark: 备注
        :return:
        """
        account = await ai_buddy_billing_account_dao.get_by_user_for_update(db, user_id)
        if account is None:
            account = await ai_buddy_billing_account_dao.create(
                db,
                CreateAIBuddyBillingAccountParam(user_id=user_id),
            )
        balance_after = account.balance + amount
        if transaction_type != AIBuddyBillingTransactionType.recharge and balance_after < 0:
            raise errors.RequestError(msg='余额不足，无法完成扣减')
        updated = await ai_buddy_billing_account_dao.update_balance(
            db,
            pk=account.id,
            balance=balance_after,
            expected_version=account.version,
        )
        if not updated:
            raise errors.ConflictError(msg='计费账户已变更，请重试')
        await ai_buddy_billing_transaction_dao.create(
            db,
            CreateAIBuddyBillingTransactionParam(
                account_id=account.id,
                user_id=user_id,
                transaction_type=transaction_type.value,
                amount=amount,
                balance_after=balance_after,
                currency=account.currency,
                reference_type='manual',
                reference_id=uuid4_str(),
                remark=remark,
            ),
        )
        return GetAIBuddyBillingAccountDetail.model_validate(
            await ai_buddy_billing_account_dao.get_by_user(db, user_id)
        )


ai_buddy_billing_account_service: AIBuddyBillingAccountService = AIBuddyBillingAccountService()
