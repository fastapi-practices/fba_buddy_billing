import asyncio

from decimal import Decimal

import pytest

from pydantic_ai.models import ModelRequestContext

from backend.common.exception import errors
from backend.plugin.ai_buddy_billing.agent.balance_guard import (
    INSUFFICIENT_BALANCE_CODE,
    INSUFFICIENT_BALANCE_MESSAGE,
    InsufficientBalanceGuard,
    has_insufficient_balance,
)


@pytest.mark.parametrize(
    ('balance', 'minimum', 'expected'),
    [
        (None, Decimal(0), False),
        (Decimal(10), Decimal(0), False),
        (Decimal('0.00000001'), Decimal(0), False),
        (Decimal(0), Decimal(0), True),
        (Decimal(-1), Decimal(0), True),
        (Decimal(-1), Decimal(-5), False),
        (Decimal(-5), Decimal(-5), True),
    ],
)
def test_has_insufficient_balance(
    balance: Decimal | None,
    minimum: Decimal,
    *,
    expected: bool,
) -> None:
    assert has_insufficient_balance(balance, minimum=minimum) is expected


def test_guard_blocks_run_when_balance_exhausted() -> None:
    calls: list[object] = []

    def handler(request_context: ModelRequestContext) -> None:
        calls.append(request_context)

    guard = InsufficientBalanceGuard(balance=Decimal(0))
    with pytest.raises(errors.RequestError) as exc_info:
        asyncio.run(
            guard.wrap_model_request(
                None,  # type: ignore[arg-type]
                request_context=None,  # type: ignore[arg-type]
                handler=handler,  # type: ignore[arg-type]
            )
        )
    assert exc_info.value.msg == INSUFFICIENT_BALANCE_MESSAGE
    assert exc_info.value.data == {'code': INSUFFICIENT_BALANCE_CODE}
    assert calls == []


def test_guard_allows_debt_within_tolerance() -> None:
    calls: list[object] = []

    async def handler(request_context: ModelRequestContext) -> object:
        await asyncio.sleep(0)
        calls.append(request_context)
        return 'response'

    guard = InsufficientBalanceGuard(balance=Decimal(-1), minimum=Decimal(-5))
    assert (
        asyncio.run(
            guard.wrap_model_request(
                None,  # type: ignore[arg-type]
                request_context=object(),  # type: ignore[arg-type]
                handler=handler,  # type: ignore[arg-type]
            )
        )
        == 'response'
    )
    assert len(calls) == 1


def test_guard_passes_request_when_balance_available() -> None:
    calls: list[object] = []

    async def handler(request_context: ModelRequestContext) -> object:
        await asyncio.sleep(0)
        calls.append(request_context)
        return 'response'

    context = object()
    guard = InsufficientBalanceGuard(balance=Decimal(5))
    result = asyncio.run(
        guard.wrap_model_request(
            None,  # type: ignore[arg-type]
            request_context=context,  # type: ignore[arg-type]
            handler=handler,  # type: ignore[arg-type]
        )
    )
    assert result == 'response'
    assert calls == [context]
