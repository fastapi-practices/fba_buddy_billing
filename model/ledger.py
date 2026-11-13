from datetime import datetime
from decimal import Decimal

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key


class AIBuddyBillingLedger(Base):
    """AI Buddy 用量账本表"""

    __tablename__ = 'ai_buddy_billing_ledger'
    __table_args__ = (
        sa.UniqueConstraint(
            'source_message_id',
            'source_response_index',
            'deleted',
            name='uk_ai_buddy_billing_ledger_source_response_deleted',
        ),
        {'comment': 'AI Buddy 用量账本'},
    )

    id: Mapped[id_key] = mapped_column(init=False)
    source_message_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='AI Buddy 消息 ID')
    source_response_index: Mapped[int] = mapped_column(sa.Integer, comment='模型响应序号')
    user_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='系统用户 ID')
    conversation_id: Mapped[str] = mapped_column(sa.String(64), index=True, comment='AI Buddy 对话 ID')
    provider_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='AI Buddy 供应商 ID')
    model_id: Mapped[str] = mapped_column(sa.String(512), index=True, comment='AI Buddy 模型 ID')
    usage_time: Mapped[datetime] = mapped_column(sa.DateTime(timezone=True), index=True, comment='用量发生时间')
    run_id: Mapped[str | None] = mapped_column(sa.String(64), default=None, index=True, comment='模型运行 ID')
    input_tokens: Mapped[int] = mapped_column(sa.BigInteger, default=0, comment='输入 token 数')
    output_tokens: Mapped[int] = mapped_column(sa.BigInteger, default=0, comment='输出 token 数')
    cache_read_tokens: Mapped[int] = mapped_column(sa.BigInteger, default=0, comment='缓存读取 token 数')
    cache_write_tokens: Mapped[int] = mapped_column(sa.BigInteger, default=0, comment='缓存写入 token 数')
    input_audio_tokens: Mapped[int] = mapped_column(sa.BigInteger, default=0, comment='音频输入 token 数')
    output_audio_tokens: Mapped[int] = mapped_column(sa.BigInteger, default=0, comment='音频输出 token 数')
    cache_audio_read_tokens: Mapped[int] = mapped_column(sa.BigInteger, default=0, comment='音频缓存读取 token 数')
    generated_images: Mapped[int] = mapped_column(sa.Integer, default=0, comment='生成图片数量')
    provider_cost: Mapped[Decimal | None] = mapped_column(sa.Numeric(20, 8), default=None, comment='供应商成本')
    billed_cost: Mapped[Decimal] = mapped_column(sa.Numeric(20, 8), default=Decimal(0), comment='结算费用')
    price_id: Mapped[int | None] = mapped_column(sa.BigInteger, default=None, index=True, comment='使用的价格 ID')
    status: Mapped[str] = mapped_column(sa.String(32), default='unpriced', comment='账本状态')
