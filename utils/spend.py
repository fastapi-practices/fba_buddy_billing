from collections.abc import Sequence
from decimal import Decimal

from pydantic_ai import ModelResponse
from pydantic_ai.tools import RunContext
from pydantic_ai_harness.spend import Budget, PriceFunc

from backend.plugin.ai_buddy.dataclasses import ChatAgentDeps
from backend.plugin.ai_buddy_billing.model import AIBuddyBillingBudget, AIBuddyBillingPrice
from backend.plugin.ai_buddy_billing.utils.usage import BillingUsageRecord, calculate_token_cost


def _user_scope(ctx: RunContext[ChatAgentDeps]) -> str:
    """按运行用户隔离预算计数"""
    return f'user:{ctx.deps.user_id}'


def build_spend_budgets(*, budgets: Sequence[AIBuddyBillingBudget]) -> tuple[Budget[ChatAgentDeps], ...]:
    """
    将计费预算转换为 Harness 预算

    :param budgets: 启用的计费预算
    :return:
    """
    return tuple(
        Budget(
            usd=budget.usd_limit,
            tokens=budget.token_limit,
            window=budget.window,
            scope=_user_scope,
            warn_at=budget.warn_at,
            name=f'billing-{budget.window}',
        )
        for budget in budgets
    )


def build_spend_price(
    *,
    prices: Sequence[AIBuddyBillingPrice],
    primary_model_id: str | None,
) -> PriceFunc | None:
    """
    构建 Billing 历史价格定价函数

    :param prices: 当前生效价格
    :param primary_model_id: 本轮主模型 ID
    :return:
    """
    price_by_model: dict[str, AIBuddyBillingPrice] = {}
    ambiguous: set[str] = set()
    for price in prices:
        if price.model_id == primary_model_id:
            price_by_model[price.model_id] = price
    for price in prices:
        if price.model_id == primary_model_id:
            continue
        if price.model_id in ambiguous:
            continue
        if price.model_id not in price_by_model:
            price_by_model[price.model_id] = price
        else:
            price_by_model.pop(price.model_id)
            ambiguous.add(price.model_id)
    if not price_by_model:
        return None

    def price_response(response: ModelResponse) -> Decimal | None:
        """按 Billing 历史价格计算单次模型响应费用"""
        model_id = response.model_name or primary_model_id
        price = price_by_model.get(model_id or '')
        if price is None:
            return None
        usage = response.usage
        details = usage.details or {}
        generated_images = max(
            int(details.get('generated_images') or 0),
            int(details.get('images') or 0),
            int(details.get('output_images') or 0),
        )
        record = BillingUsageRecord(
            response_index=0,
            run_id=response.run_id,
            model_id=model_id or '',
            usage_time=response.timestamp,
            input_tokens=usage.input_tokens or 0,
            output_tokens=usage.output_tokens or 0,
            cache_read_tokens=usage.cache_read_tokens or 0,
            cache_write_tokens=usage.cache_write_tokens or 0,
            input_audio_tokens=usage.input_audio_tokens or 0,
            output_audio_tokens=usage.output_audio_tokens or 0,
            cache_audio_read_tokens=usage.cache_audio_read_tokens or 0,
            generated_images=generated_images,
            provider_cost=None,
            details={},
        )
        rates = {
            'input_price': price.input_price,
            'output_price': price.output_price,
            'cache_read_price': price.cache_read_price,
            'cache_write_price': price.cache_write_price,
            'input_audio_price': price.input_audio_price,
            'output_audio_price': price.output_audio_price,
            'cache_audio_read_price': price.cache_audio_read_price,
        }
        cost = calculate_token_cost(usage=record, rates=rates)
        cost += Decimal(generated_images) * price.image_price
        return cost.quantize(Decimal('0.00000001'))

    return price_response
