from decimal import Decimal

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.enums import StatusType
from backend.common.model import Base, id_key


class AIBuddyBillingBudget(Base):
    """AI Buddy 计费预算表"""

    __tablename__ = 'ai_buddy_billing_budget'
    __table_args__ = (
        sa.UniqueConstraint('user_id', 'window', 'deleted', name='uk_ai_buddy_billing_budget_user_window_deleted'),
        {'comment': 'AI Buddy 计费预算'},
    )

    id: Mapped[id_key] = mapped_column(init=False)
    user_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='系统用户 ID')
    window: Mapped[str] = mapped_column(sa.String(32), index=True, comment='预算窗口')
    usd_limit: Mapped[Decimal | None] = mapped_column(sa.Numeric(20, 8), default=None, comment='USD 上限')
    token_limit: Mapped[int | None] = mapped_column(sa.BigInteger, default=None, comment='token 总量上限')
    warn_at: Mapped[float | None] = mapped_column(sa.Float, default=None, comment='预警比例')
    status: Mapped[int] = mapped_column(default=StatusType.enable.value, comment='状态（0停用 1正常）')
