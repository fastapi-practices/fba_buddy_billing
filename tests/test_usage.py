from datetime import UTC, datetime
from decimal import Decimal

from backend.plugin.fba_buddy_billing.utils.usage import calculate_token_cost, extract_usage_records


def test_extract_usage_records() -> None:
    payloads = [
        {'kind': 'request'},
        {
            'kind': 'response',
            'run_id': 'run-1',
            'model_name': 'demo',
            'timestamp': '2026-11-12T10:00:00Z',
            'usage': {
                'input_tokens': 1_000_000,
                'output_tokens': 2_000_000,
                'cache_read_tokens': 3_000_000,
                'cache_write_tokens': 4_000_000,
                'details': {'generated_images': 2},
                'cost': '0.25',
            },
        },
    ]
    records = extract_usage_records(
        payloads=payloads,
        model_id='fallback',
        fallback_time=datetime(2026, 11, 12, tzinfo=UTC),
    )
    assert len(records) == 1
    assert records[0].response_index == 1
    assert records[0].model_id == 'demo'
    assert records[0].generated_images == 2
    assert records[0].provider_cost == Decimal('0.25')


def test_calculate_token_cost() -> None:
    records = extract_usage_records(
        payloads=[{'kind': 'response', 'usage': {'input_tokens': 1_000_000, 'output_tokens': 2_000_000}}],
        model_id='demo',
        fallback_time=datetime(2026, 11, 12, tzinfo=UTC),
    )
    cost = calculate_token_cost(
        usage=records[0],
        rates={
            'input_price': Decimal(1),
            'output_price': Decimal(2),
        },
    )
    assert cost == Decimal('5.00000000')
