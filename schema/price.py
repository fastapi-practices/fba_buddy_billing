from datetime import datetime
from decimal import Decimal

from pydantic import AwareDatetime, ConfigDict, Field

from backend.common.schema import SchemaBase


class AIBuddyBillingPriceQueryParam(SchemaBase):
    """AI Buddy 计费价格查询参数"""

    provider_id: int | None = Field(None, description='供应商 ID')
    model_id: str | None = Field(None, description='模型 ID')
    active: bool | None = Field(None, description='是否只查询生效中的价格')


class AIBuddyBillingPriceSchemaBase(SchemaBase):
    """AI Buddy 计费价格基础模型"""

    provider_id: int = Field(description='供应商 ID')
    model_id: str = Field(min_length=1, max_length=512, description='模型 ID')
    input_price: Decimal = Field(default=Decimal(0), ge=0, description='输入 token 每百万价格')
    output_price: Decimal = Field(default=Decimal(0), ge=0, description='输出 token 每百万价格')
    cache_read_price: Decimal = Field(default=Decimal(0), ge=0, description='缓存读取 token 每百万价格')
    cache_write_price: Decimal = Field(default=Decimal(0), ge=0, description='缓存写入 token 每百万价格')
    input_audio_price: Decimal = Field(default=Decimal(0), ge=0, description='音频输入 token 每百万价格')
    output_audio_price: Decimal = Field(default=Decimal(0), ge=0, description='音频输出 token 每百万价格')
    cache_audio_read_price: Decimal = Field(default=Decimal(0), ge=0, description='音频缓存读取 token 每百万价格')
    image_price: Decimal = Field(default=Decimal(0), ge=0, description='单张生成图片价格')
    effective_from: AwareDatetime | None = Field(None, description='价格生效时间，需携带时区偏移')
    effective_to: AwareDatetime | None = Field(None, description='价格失效时间，需携带时区偏移')


class CreateAIBuddyBillingPriceParam(AIBuddyBillingPriceSchemaBase):
    """创建 AI Buddy 计费价格参数"""

    effective_from: AwareDatetime = Field(description='价格生效时间，需携带时区偏移')


class UpdateAIBuddyBillingPriceParam(SchemaBase):
    """更新 AI Buddy 计费价格参数"""

    input_price: Decimal = Field(default=Decimal(0), ge=0, description='输入 token 每百万价格')
    output_price: Decimal = Field(default=Decimal(0), ge=0, description='输出 token 每百万价格')
    cache_read_price: Decimal = Field(default=Decimal(0), ge=0, description='缓存读取 token 每百万价格')
    cache_write_price: Decimal = Field(default=Decimal(0), ge=0, description='缓存写入 token 每百万价格')
    input_audio_price: Decimal = Field(default=Decimal(0), ge=0, description='音频输入 token 每百万价格')
    output_audio_price: Decimal = Field(default=Decimal(0), ge=0, description='音频输出 token 每百万价格')
    cache_audio_read_price: Decimal = Field(default=Decimal(0), ge=0, description='音频缓存读取 token 每百万价格')
    image_price: Decimal = Field(default=Decimal(0), ge=0, description='单张生成图片价格')
    effective_to: AwareDatetime | None = Field(None, description='价格失效时间，需携带时区偏移')


class GetAIBuddyBillingPriceDetail(AIBuddyBillingPriceSchemaBase):
    """AI Buddy 计费价格详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='价格 ID')
    created_time: datetime = Field(description='创建时间')
    updated_time: datetime | None = Field(None, description='更新时间')
