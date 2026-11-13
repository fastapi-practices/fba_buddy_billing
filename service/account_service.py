from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.exception import errors
from backend.common.pagination import paging_data
from backend.database.db import uuid4_str
from backend.plugin.fba_buddy_billing.crud.crud_account import fba_buddy_billing_account_dao
from backend.plugin.fba_buddy_billing.crud.crud_transaction import fba_buddy_billing_transaction_dao
from backend.plugin.fba_buddy_billing.enums import FbaBuddyBillingTransactionType
from backend.plugin.fba_buddy_billing.schema.account import (
    CreateFbaBuddyBillingAccountParam,
    CreateFbaBuddyBillingAdjustmentParam,
    CreateFbaBuddyBillingRechargeParam,
    GetFbaBuddyBillingAccountDetail,
)
from backend.plugin.fba_buddy_billing.schema.transaction import CreateFbaBuddyBillingTransactionParam


class FbaBuddyBillingAccountService:
    """AI Buddy 计费账户服务类"""

    @staticmethod
    async def get(*, db: AsyncSession, user_id: int) -> GetFbaBuddyBillingAccountDetail:
        """
        获取计费账户

        :param db: 数据库会话
        :param user_id: 用户 ID
        :return:
        """
        account = await fba_buddy_billing_account_dao.get_by_user(db, user_id)
        if account is None:
            raise errors.NotFoundError(msg='计费账户不存在')
        return GetFbaBuddyBillingAccountDetail.model_validate(account)

    @staticmethod
    async def get_list(
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
        stmt = await fba_buddy_billing_transaction_dao.get_select(
            user_id=user_id,
            transaction_type=transaction_type,
            start_time=start_time,
            end_time=end_time,
        )
        return await paging_data(db, stmt)

    async def recharge(
        self, *, db: AsyncSession, obj: CreateFbaBuddyBillingRechargeParam
    ) -> GetFbaBuddyBillingAccountDetail:
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
            transaction_type=FbaBuddyBillingTransactionType.recharge,
            remark=obj.remark,
        )

    async def adjust(
        self, *, db: AsyncSession, obj: CreateFbaBuddyBillingAdjustmentParam
    ) -> GetFbaBuddyBillingAccountDetail:
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
            transaction_type=FbaBuddyBillingTransactionType.adjust,
            remark=obj.remark,
        )

    @staticmethod
    async def _apply_transaction(
        *,
        db: AsyncSession,
        user_id: int,
        amount: Decimal,
        transaction_type: FbaBuddyBillingTransactionType,
        remark: str | None,
    ) -> GetFbaBuddyBillingAccountDetail:
        """
        写入账户余额流水

        :param db: 数据库会话
        :param user_id: 用户 ID
        :param amount: 变动金额
        :param transaction_type: 流水类型
        :param remark: 备注
        :return:
        """
        account = await fba_buddy_billing_account_dao.get_by_user_for_update(db, user_id)
        if account is None:
            account = await fba_buddy_billing_account_dao.create(
                db,
                CreateFbaBuddyBillingAccountParam(user_id=user_id),
            )
        balance_after = account.balance + amount
        if transaction_type != FbaBuddyBillingTransactionType.recharge and balance_after < 0:
            raise errors.RequestError(msg='余额不足，无法完成扣减')
        updated = await fba_buddy_billing_account_dao.update_balance(
            db,
            pk=account.id,
            balance=balance_after,
            expected_version=account.version,
        )
        if not updated:
            raise errors.ConflictError(msg='计费账户已变更，请重试')
        await fba_buddy_billing_transaction_dao.create(
            db,
            CreateFbaBuddyBillingTransactionParam(
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
        return GetFbaBuddyBillingAccountDetail.model_validate(
            await fba_buddy_billing_account_dao.get_by_user(db, user_id)
        )


fba_buddy_billing_account_service: FbaBuddyBillingAccountService = FbaBuddyBillingAccountService()
