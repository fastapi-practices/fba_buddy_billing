from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import UTC, datetime
from decimal import Decimal, InvalidOperation
from typing import Any


@dataclass(frozen=True, slots=True)
class BillingUsageRecord:
    """AI Buddy 单次模型响应用量"""

    response_index: int
    run_id: str | None
    model_id: str
    usage_time: datetime
    input_tokens: int
    output_tokens: int
    cache_read_tokens: int
    cache_write_tokens: int
    input_audio_tokens: int
    output_audio_tokens: int
    cache_audio_read_tokens: int
    generated_images: int
    provider_cost: Decimal | None
    details: dict[str, int]


def _as_int(value: Any, default: int = 0) -> int:
    """规范整数用量，忽略布尔值和非法值"""
    if isinstance(value, bool) or value is None:
        return default
    try:
        number = int(value)
    except (TypeError, ValueError):
        return default
    return max(number, 0)


def _as_decimal(value: Any) -> Decimal | None:
    """规范金额，保留供应商提供的费用"""
    if value is None or isinstance(value, bool):
        return None
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return None
    return result if result.is_finite() and result >= 0 else None


def _as_datetime(value: Any, fallback: datetime) -> datetime:
    """解析响应时间，缺少时间时使用消息时间"""
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=UTC)
    if isinstance(value, str):
        try:
            parsed = datetime.fromisoformat(value)
        except ValueError:
            return fallback
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=UTC)
    return fallback


def extract_usage_records(
    *,
    payloads: Sequence[Any],
    model_id: str,
    fallback_time: datetime,
) -> list[BillingUsageRecord]:
    """
    从 AI Buddy 原始模型消息提取模型响应用量

    :param payloads: 原始模型消息 JSON 列表
    :param provider_id: 供应商 ID
    :param model_id: 消息默认模型 ID
    :param fallback_time: 用量时间兜底值
    :return:
    """
    records: list[BillingUsageRecord] = []
    for response_index, payload in enumerate(payloads):
        if not isinstance(payload, Mapping):
            continue
        usage = payload.get('usage')
        if not isinstance(usage, Mapping):
            continue
        raw_details = usage.get('details')
        details = (
            {
                str(key): _as_int(value)
                for key, value in raw_details.items()
                if isinstance(value, (int, float, str)) and not isinstance(value, bool)
            }
            if isinstance(raw_details, Mapping)
            else {}
        )
        generated_images = max(
            _as_int(details.get('generated_images')),
            _as_int(details.get('images')),
            _as_int(details.get('output_images')),
        )
        input_tokens = _as_int(usage.get('input_tokens'))
        output_tokens = _as_int(usage.get('output_tokens'))
        cache_read_tokens = _as_int(usage.get('cache_read_tokens'))
        cache_write_tokens = _as_int(usage.get('cache_write_tokens'))
        input_audio_tokens = _as_int(usage.get('input_audio_tokens'))
        output_audio_tokens = _as_int(usage.get('output_audio_tokens'))
        cache_audio_read_tokens = _as_int(usage.get('cache_audio_read_tokens'))
        provider_cost = _as_decimal(usage.get('cost'))
        if not any((
            input_tokens,
            output_tokens,
            cache_read_tokens,
            cache_write_tokens,
            input_audio_tokens,
            output_audio_tokens,
            cache_audio_read_tokens,
            generated_images,
            provider_cost is not None,
            details,
        )):
            continue
        records.append(
            BillingUsageRecord(
                response_index=response_index,
                run_id=str(payload['run_id']) if payload.get('run_id') else None,
                model_id=str(payload.get('model_name') or model_id),
                usage_time=_as_datetime(payload.get('timestamp'), fallback_time),
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                cache_read_tokens=cache_read_tokens,
                cache_write_tokens=cache_write_tokens,
                input_audio_tokens=input_audio_tokens,
                output_audio_tokens=output_audio_tokens,
                cache_audio_read_tokens=cache_audio_read_tokens,
                generated_images=generated_images,
                provider_cost=provider_cost,
                details=details,
            )
        )
    return records


def calculate_token_cost(*, usage: BillingUsageRecord, rates: Mapping[str, Decimal]) -> Decimal:
    """
    按每百万 token 单价计算模型费用

    :param usage: 用量记录
    :param rates: token 单价映射
    :return:
    """
    tokens = {
        'input_price': usage.input_tokens,
        'output_price': usage.output_tokens,
        'cache_read_price': usage.cache_read_tokens,
        'cache_write_price': usage.cache_write_tokens,
        'input_audio_price': usage.input_audio_tokens,
        'output_audio_price': usage.output_audio_tokens,
        'cache_audio_read_price': usage.cache_audio_read_tokens,
    }
    cost = sum(
        (Decimal(tokens[name]) * rate / Decimal(1_000_000) for name, rate in rates.items() if name in tokens),
        Decimal(0),
    )
    return cost.quantize(Decimal('0.00000001'))
