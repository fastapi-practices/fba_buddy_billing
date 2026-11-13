from datetime import datetime
from decimal import Decimal

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class FbaBuddyBillingLedgerQueryParam(SchemaBase):
    """AI Buddy 用量账本查询参数"""

    user_id: int | None = Field(None, description='用户 ID')
    conversation_id: str | None = Field(None, description='对话 ID')
    provider_id: int | None = Field(None, description='供应商 ID')
    model_id: str | None = Field(None, description='模型 ID')
    status: str | None = Field(None, description='账本状态')
    start_time: datetime | None = Field(None, description='开始时间')
    end_time: datetime | None = Field(None, description='结束时间')


class GetFbaBuddyBillingLedgerDetail(SchemaBase):
    """AI Buddy 用量账本详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='账本 ID')
    source_message_id: int = Field(description='AI Buddy 消息 ID')
    source_response_index: int = Field(description='模型响应序号')
    user_id: int = Field(description='用户 ID')
    conversation_id: str = Field(description='对话 ID')
    provider_id: int = Field(description='供应商 ID')
    model_id: str = Field(description='模型 ID')
    run_id: str | None = Field(None, description='模型运行 ID')
    usage_time: datetime = Field(description='用量发生时间')
    input_tokens: int = Field(description='输入 token 数')
    output_tokens: int = Field(description='输出 token 数')
    cache_read_tokens: int = Field(description='缓存读取 token 数')
    cache_write_tokens: int = Field(description='缓存写入 token 数')
    input_audio_tokens: int = Field(description='音频输入 token 数')
    output_audio_tokens: int = Field(description='音频输出 token 数')
    cache_audio_read_tokens: int = Field(description='音频缓存读取 token 数')
    generated_images: int = Field(description='生成图片数量')
    provider_cost: Decimal | None = Field(None, description='供应商成本')
    billed_cost: Decimal = Field(description='结算费用')
    price_id: int | None = Field(None, description='使用的价格 ID')
    status: str = Field(description='账本状态')
    created_time: datetime = Field(description='创建时间')


class GetFbaBuddyBillingSummaryDetail(SchemaBase):
    """AI Buddy 计费汇总"""

    start_time: datetime | None = Field(None, description='开始时间')
    end_time: datetime | None = Field(None, description='结束时间')
    usage_count: int = Field(description='用量记录数')
    input_tokens: int = Field(description='输入 token 数')
    output_tokens: int = Field(description='输出 token 数')
    cache_read_tokens: int = Field(description='缓存读取 token 数')
    cache_write_tokens: int = Field(description='缓存写入 token 数')
    generated_images: int = Field(description='生成图片数量')
    provider_cost: Decimal = Field(description='供应商成本')
    billed_cost: Decimal = Field(description='结算费用')


class GetFbaBuddyBillingReconcileDetail(SchemaBase):
    """AI Buddy 计费归集结果"""

    processed: int = Field(description='扫描的消息数')
    recorded: int = Field(description='写入账本的响应数')
    billed: int = Field(description='已计费的响应数')
    unpriced: int = Field(description='未定价的响应数')


class CreateFbaBuddyBillingLedgerParam(SchemaBase):
    """创建 AI Buddy 用量账本参数"""

    source_message_id: int = Field(description='AI Buddy 消息 ID')
    source_response_index: int = Field(ge=0, description='模型响应序号')
    user_id: int = Field(description='用户 ID')
    conversation_id: str = Field(min_length=1, max_length=64, description='对话 ID')
    provider_id: int = Field(description='供应商 ID')
    model_id: str = Field(min_length=1, max_length=512, description='模型 ID')
    usage_time: datetime = Field(description='用量发生时间')
    run_id: str | None = Field(None, max_length=64, description='模型运行 ID')
    input_tokens: int = Field(default=0, ge=0, description='输入 token 数')
    output_tokens: int = Field(default=0, ge=0, description='输出 token 数')
    cache_read_tokens: int = Field(default=0, ge=0, description='缓存读取 token 数')
    cache_write_tokens: int = Field(default=0, ge=0, description='缓存写入 token 数')
    input_audio_tokens: int = Field(default=0, ge=0, description='音频输入 token 数')
    output_audio_tokens: int = Field(default=0, ge=0, description='音频输出 token 数')
    cache_audio_read_tokens: int = Field(default=0, ge=0, description='音频缓存读取 token 数')
    generated_images: int = Field(default=0, ge=0, description='生成图片数量')
    provider_cost: Decimal | None = Field(None, ge=0, description='供应商成本')
    billed_cost: Decimal = Field(default=Decimal(0), ge=0, description='结算费用')
    price_id: int | None = Field(None, description='使用的价格 ID')
    status: str = Field(default='unpriced', min_length=1, max_length=32, description='账本状态')
