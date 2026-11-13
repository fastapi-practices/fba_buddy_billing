from decimal import Decimal

import sqlalchemy as sa

from sqlalchemy.orm import Mapped, mapped_column

from backend.common.model import Base, id_key


class FbaBuddyBillingAccount(Base):
    """AI Buddy 计费账户表"""

    __tablename__ = 'fba_buddy_billing_account'
    __table_args__ = (
        sa.UniqueConstraint('user_id', 'deleted', name='uk_fba_buddy_billing_account_user_deleted'),
        {'comment': 'AI Buddy 计费账户'},
    )

    id: Mapped[id_key] = mapped_column(init=False)
    user_id: Mapped[int] = mapped_column(sa.BigInteger, index=True, comment='系统用户 ID')
    balance: Mapped[Decimal] = mapped_column(sa.Numeric(20, 8), default=Decimal(0), comment='当前余额')
    currency: Mapped[str] = mapped_column(sa.String(16), default='USD', comment='结算币种')
    version: Mapped[int] = mapped_column(sa.BigInteger, default=0, comment='余额版本号')
