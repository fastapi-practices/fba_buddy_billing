from datetime import UTC, datetime, timedelta, timezone

import pytest

from pydantic import ValidationError

from backend.plugin.ai_buddy_billing.schema.ledger import AIBuddyBillingLedgerQueryParam
from backend.plugin.ai_buddy_billing.schema.price import (
    CreateAIBuddyBillingPriceParam,
    UpdateAIBuddyBillingPriceParam,
)
from backend.plugin.ai_buddy_billing.schema.transaction import AIBuddyBillingTransactionQueryParam

_SHANGHAI = timezone(timedelta(hours=8))


def test_price_accepts_offset_aware_datetime() -> None:
    row = CreateAIBuddyBillingPriceParam(
        provider_id=1,
        model_id='gpt-4o',
        effective_from='2024-05-01T00:00:00+08:00',
    )
    assert row.effective_from == datetime(2024, 5, 1, tzinfo=_SHANGHAI)


def test_price_accepts_utc_datetime() -> None:
    row = UpdateAIBuddyBillingPriceParam(effective_to='2024-06-01T00:00:00Z')
    assert row.effective_to == datetime(2024, 6, 1, tzinfo=UTC)


@pytest.mark.parametrize(
    ('schema', 'kwargs'),
    [
        (
            CreateAIBuddyBillingPriceParam,
            {'provider_id': 1, 'model_id': 'gpt-4o', 'effective_from': '2024-05-01 00:00:00'},
        ),
        (UpdateAIBuddyBillingPriceParam, {'effective_to': '2024-06-01 00:00:00'}),
        (AIBuddyBillingLedgerQueryParam, {'start_time': '2024-05-01 00:00:00'}),
        (AIBuddyBillingTransactionQueryParam, {'end_time': '2024-05-01 00:00:00'}),
    ],
)
def test_naive_datetime_is_rejected(schema: type, kwargs: dict[str, object]) -> None:
    with pytest.raises(ValidationError):
        schema(**kwargs)
