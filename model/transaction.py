from decimal import Decimal

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key


class AIBuddyBillingTransaction(Base):
    """AI Buddy 计费账户流水表"""

    __tablename__ = 'ai_buddy_billing_transaction'
    __table_args__ = (
        sa.UniqueConstraint(
            'reference_type',
            'reference_id',
            'deleted',
            name='uk_ai_buddy_billing_transaction_reference_deleted',
        ),
        {'comment': 'AI Buddy 计费账户流水'},
    )

    id: Mapped[id_key] = mapped_column(init=False)
    account_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='计费账户 ID')
    user_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='系统用户 ID')
    transaction_type: Mapped[str] = mapped_column(sa.String(32), index=True, comment='流水类型')
    amount: Mapped[Decimal] = mapped_column(sa.Numeric(20, 8), comment='变动金额')
    balance_after: Mapped[Decimal] = mapped_column(sa.Numeric(20, 8), comment='变动后余额')
    reference_type: Mapped[str] = mapped_column(sa.String(32), comment='关联对象类型')
    reference_id: Mapped[str] = mapped_column(sa.String(128), comment='关联对象 ID')
    currency: Mapped[str] = mapped_column(sa.String(16), default='USD', comment='结算币种')
    remark: Mapped[str | None] = mapped_column(sa.Text, default=None, comment='备注')
