from datetime import datetime
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.common.exception import errors
from backend.common.pagination import paging_data
from backend.plugin.ai_buddy_billing.crud.crud_account import ai_buddy_billing_account_dao
from backend.plugin.ai_buddy_billing.crud.crud_ledger import ai_buddy_billing_ledger_dao
from backend.plugin.ai_buddy_billing.crud.crud_price import ai_buddy_billing_price_dao
from backend.plugin.ai_buddy_billing.crud.crud_transaction import ai_buddy_billing_transaction_dao
from backend.plugin.ai_buddy_billing.crud.crud_usage_source import ai_buddy_billing_usage_source_dao
from backend.plugin.ai_buddy_billing.enums import AIBuddyBillingLedgerStatus, AIBuddyBillingTransactionType
from backend.plugin.ai_buddy_billing.model import AIBuddyBillingLedger, AIBuddyBillingPrice
from backend.plugin.ai_buddy_billing.schema.account import CreateAIBuddyBillingAccountParam
from backend.plugin.ai_buddy_billing.schema.ledger import (
    CreateAIBuddyBillingLedgerParam,
    GetAIBuddyBillingReconcileDetail,
    GetAIBuddyBillingSummaryDetail,
)
from backend.plugin.ai_buddy_billing.schema.transaction import CreateAIBuddyBillingTransactionParam
from backend.plugin.ai_buddy_billing.utils.usage import BillingUsageRecord, calculate_token_cost, extract_usage_records


class AIBuddyBillingLedgerService:
    """AI Buddy 用量账本服务类"""

    @staticmethod
    async def get_list(
        *,
        db: AsyncSession,
        user_id: int | None,
        conversation_id: str | None,
        provider_id: int | None,
        model_id: str | None,
        status: str | None,
        start_time: datetime | None,
        end_time: datetime | None,
    ) -> dict[str, Any]:
        """
        分页获取用量账本

        :param db: 数据库会话
        :param user_id: 用户 ID
        :param conversation_id: 对话 ID
        :param provider_id: 供应商 ID
        :param model_id: 模型 ID
        :param status: 账本状态
        :param start_time: 开始时间
        :param end_time: 结束时间
        :return:
        """
        return await paging_data(
            db,
            await ai_buddy_billing_ledger_dao.get_select(
                user_id=user_id,
                conversation_id=conversation_id,
                provider_id=provider_id,
                model_id=model_id,
                status=status,
                start_time=start_time,
                end_time=end_time,
            ),
        )

    @staticmethod
    async def get_summary(
        *,
        db: AsyncSession,
        user_id: int | None = None,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> GetAIBuddyBillingSummaryDetail:
        """
        获取用量汇总

        :param db: 数据库会话
        :param user_id: 用户 ID
        :param start_time: 开始时间
        :param end_time: 结束时间
        :return:
        """
        summary = await ai_buddy_billing_ledger_dao.get_summary(
            db,
            user_id=user_id,
            start_time=start_time,
            end_time=end_time,
        )
        return GetAIBuddyBillingSummaryDetail(
            start_time=start_time,
            end_time=end_time,
            usage_count=summary['usage_count'],
            input_tokens=summary['input_tokens'],
            output_tokens=summary['output_tokens'],
            cache_read_tokens=summary['cache_read_tokens'],
            cache_write_tokens=summary['cache_write_tokens'],
            generated_images=summary['generated_images'],
            provider_cost=summary['provider_cost'],
            billed_cost=summary['billed_cost'],
        )

    async def reconcile(self, *, db: AsyncSession, limit: int = 500) -> GetAIBuddyBillingReconcileDetail:
        """
        归集 AI Buddy 消息用量并扣减账户余额

        :param db: 数据库会话
        :param limit: 单次扫描消息数量
        :return:
        """
        rows = await ai_buddy_billing_usage_source_dao.get_list(db, limit=limit)
        recorded = 0
        billed = 0
        unpriced = 0
        for message, user_id in rows:
            payloads = list(message.model_messages or [])
            records = extract_usage_records(
                payloads=payloads,
                model_id=message.model_id,
                fallback_time=message.created_time,
            )
            if not records:
                await ai_buddy_billing_ledger_dao.create(
                    db,
                    CreateAIBuddyBillingLedgerParam(
                        source_message_id=message.id,
                        source_response_index=0,
                        user_id=user_id,
                        conversation_id=message.conversation_id,
                        provider_id=message.provider_id,
                        model_id=message.model_id,
                        usage_time=message.created_time,
                        status=AIBuddyBillingLedgerStatus.unpriced.value,
                    ),
                )
                recorded += 1
                unpriced += 1
                continue
            for record in records:
                price = await ai_buddy_billing_price_dao.get_active(
                    db,
                    provider_id=message.provider_id,
                    model_id=record.model_id,
                    effective_time=record.usage_time,
                )
                billed_cost, status, price_id = self._resolve_cost(record=record, price=price)
                ledger = await ai_buddy_billing_ledger_dao.create(
                    db,
                    CreateAIBuddyBillingLedgerParam(
                        source_message_id=message.id,
                        source_response_index=record.response_index,
                        user_id=user_id,
                        conversation_id=message.conversation_id,
                        provider_id=message.provider_id,
                        model_id=record.model_id,
                        run_id=record.run_id,
                        usage_time=record.usage_time,
                        input_tokens=record.input_tokens,
                        output_tokens=record.output_tokens,
                        cache_read_tokens=record.cache_read_tokens,
                        cache_write_tokens=record.cache_write_tokens,
                        input_audio_tokens=record.input_audio_tokens,
                        output_audio_tokens=record.output_audio_tokens,
                        cache_audio_read_tokens=record.cache_audio_read_tokens,
                        generated_images=record.generated_images,
                        provider_cost=record.provider_cost,
                        billed_cost=billed_cost,
                        price_id=price_id,
                        status=status.value,
                    ),
                )
                recorded += 1
                if status == AIBuddyBillingLedgerStatus.unpriced:
                    unpriced += 1
                else:
                    billed += 1
                if billed_cost > 0:
                    await self._charge_usage(
                        db=db,
                        user_id=user_id,
                        ledger=ledger,
                        billed_cost=billed_cost,
                    )
        return GetAIBuddyBillingReconcileDetail(
            processed=len(rows),
            recorded=recorded,
            billed=billed,
            unpriced=unpriced,
        )

    @staticmethod
    def _resolve_cost(
        *,
        record: BillingUsageRecord,
        price: AIBuddyBillingPrice | None,
    ) -> tuple[Decimal, AIBuddyBillingLedgerStatus, int | None]:
        """
        解析单次用量的结算费用

        :param record: 用量记录
        :param price: 生效价格
        :return:
        """
        if price is not None:
            rates = {
                'input_price': price.input_price,
                'output_price': price.output_price,
                'cache_read_price': price.cache_read_price,
                'cache_write_price': price.cache_write_price,
                'input_audio_price': price.input_audio_price,
                'output_audio_price': price.output_audio_price,
                'cache_audio_read_price': price.cache_audio_read_price,
            }
            billed_cost = calculate_token_cost(usage=record, rates=rates)
            billed_cost += Decimal(record.generated_images) * price.image_price
            return billed_cost.quantize(Decimal('0.00000001')), AIBuddyBillingLedgerStatus.billed, price.id
        if record.provider_cost is not None:
            return (
                max(record.provider_cost, Decimal(0)).quantize(Decimal('0.00000001')),
                AIBuddyBillingLedgerStatus.provider_cost,
                None,
            )
        return Decimal(0), AIBuddyBillingLedgerStatus.unpriced, None

    @staticmethod
    async def _charge_usage(
        *,
        db: AsyncSession,
        user_id: int,
        ledger: AIBuddyBillingLedger,
        billed_cost: Decimal,
    ) -> None:
        """
        为账本记录扣减用户余额

        :param db: 数据库会话
        :param user_id: 用户 ID
        :param ledger: 账本记录
        :param billed_cost: 结算费用
        :return:
        """
        account = await ai_buddy_billing_account_dao.get_by_user_for_update(db, user_id)
        if account is None:
            account = await ai_buddy_billing_account_dao.create(
                db,
                CreateAIBuddyBillingAccountParam(user_id=user_id),
            )
        balance_after = account.balance - billed_cost
        updated = await ai_buddy_billing_account_dao.update_balance(
            db,
            pk=account.id,
            balance=balance_after,
            expected_version=account.version,
        )
        if not updated:
            raise errors.ConflictError(msg='计费账户已变更，请重新归集')
        await ai_buddy_billing_transaction_dao.create(
            db,
            CreateAIBuddyBillingTransactionParam(
                account_id=account.id,
                user_id=user_id,
                transaction_type=AIBuddyBillingTransactionType.consume.value,
                amount=-billed_cost,
                balance_after=balance_after,
                currency=account.currency,
                reference_type='usage',
                reference_id=str(ledger.id),
            ),
        )


ai_buddy_billing_ledger_service: AIBuddyBillingLedgerService = AIBuddyBillingLedgerService()
