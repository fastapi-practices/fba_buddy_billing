from datetime import datetime
from decimal import Decimal

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key


class AIBuddyBillingPrice(Base):
    """AI Buddy 模型价格表"""

    __tablename__ = 'ai_buddy_billing_price'
    __table_args__ = (
        sa.UniqueConstraint(
            'provider_id',
            'model_id',
            'effective_from',
            'deleted',
            name='uk_ai_buddy_billing_price_provider_model_effective_deleted',
        ),
        {'comment': 'AI Buddy 模型价格'},
    )

    id: Mapped[id_key] = mapped_column(init=False)
    provider_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='AI Buddy 供应商 ID')
    model_id: Mapped[str] = mapped_column(sa.String(512), index=True, comment='AI Buddy 模型 ID')
    effective_from: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), index=True, comment='价格生效时间')
    input_price: Mapped[Decimal] = mapped_column(sa.Numeric(20, 8), default=Decimal(0), comment='输入 token 每百万价格')
    output_price: Mapped[Decimal] = mapped_column(
        sa.Numeric(20, 8), default=Decimal(0), comment='输出 token 每百万价格'
    )
    cache_read_price: Mapped[Decimal] = mapped_column(
        sa.Numeric(20, 8), default=Decimal(0), comment='缓存读取 token 每百万价格'
    )
    cache_write_price: Mapped[Decimal] = mapped_column(
        sa.Numeric(20, 8), default=Decimal(0), comment='缓存写入 token 每百万价格'
    )
    input_audio_price: Mapped[Decimal] = mapped_column(
        sa.Numeric(20, 8), default=Decimal(0), comment='音频输入 token 每百万价格'
    )
    output_audio_price: Mapped[Decimal] = mapped_column(
        sa.Numeric(20, 8), default=Decimal(0), comment='音频输出 token 每百万价格'
    )
    cache_audio_read_price: Mapped[Decimal] = mapped_column(
        sa.Numeric(20, 8), default=Decimal(0), comment='音频缓存读取 token 每百万价格'
    )
    image_price: Mapped[Decimal] = mapped_column(sa.Numeric(20, 8), default=Decimal(0), comment='单张生成图片价格')
    effective_to: Mapped[datetime | None] = mapped_column(
        sa.DateTime(timezone=True), default=None, index=True, comment='价格失效时间'
    )
