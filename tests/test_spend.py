from datetime import UTC, datetime
from decimal import Decimal

import pytest

from pydantic import ValidationError
from pydantic_ai.messages import ModelResponse, RequestUsage, TextPart

from backend.plugin.ai_buddy_billing.model import AIBuddyBillingBudget, AIBuddyBillingPrice
from backend.plugin.ai_buddy_billing.schema.budget import CreateAIBuddyBillingBudgetParam
from backend.plugin.ai_buddy_billing.utils.spend import build_spend_budgets, build_spend_price


def test_build_spend_budgets() -> None:
    budgets = build_spend_budgets(
        budgets=[
            AIBuddyBillingBudget(
                user_id=1,
                window='day',
                usd_limit=Decimal(10),
                token_limit=100_000,
                warn_at=0.8,
            )
        ]
    )
    assert len(budgets) == 1
    assert budgets[0].usd == Decimal(10)
    assert budgets[0].tokens == 100_000
    assert budgets[0].window == 'day'
    assert budgets[0].scope is not None


def test_build_spend_price() -> None:
    price = AIBuddyBillingPrice(
        provider_id=1,
        model_id='demo',
        effective_from=datetime(2026, 1, 1, tzinfo=UTC),
        input_price=Decimal(1),
        output_price=Decimal(2),
    )
    price_response = build_spend_price(prices=[price], primary_model_id='demo')
    assert price_response is not None
    response = ModelResponse(
        parts=[TextPart(content='hello')],
        usage=RequestUsage(input_tokens=1_000_000, output_tokens=2_000_000),
        model_name='demo',
    )
    assert price_response(response) == Decimal('5.00000000')


def test_budget_requires_limit() -> None:
    with pytest.raises(ValidationError):
        CreateAIBuddyBillingBudgetParam(user_id=1, window='day')
