from datetime import datetime
from decimal import Decimal

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class CreateFbaBuddyBillingRechargeParam(SchemaBase):
    """AI Buddy 计费账户充值参数"""

    user_id: int = Field(description='用户 ID')
    amount: Decimal = Field(gt=0, description='充值金额')
    remark: str | None = Field(None, max_length=500, description='备注')


class CreateFbaBuddyBillingAdjustmentParam(SchemaBase):
    """AI Buddy 计费账户调整参数"""

    user_id: int = Field(description='用户 ID')
    amount: Decimal = Field(description='调整金额，正数增加余额，负数扣减余额')
    remark: str | None = Field(None, max_length=500, description='备注')


class GetFbaBuddyBillingAccountDetail(SchemaBase):
    """AI Buddy 计费账户详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='账户 ID')
    user_id: int = Field(description='用户 ID')
    balance: Decimal = Field(description='当前余额')
    currency: str = Field(description='结算币种')
    version: int = Field(description='余额版本号')
    created_time: datetime = Field(description='创建时间')
    updated_time: datetime | None = Field(None, description='更新时间')


class CreateFbaBuddyBillingAccountParam(SchemaBase):
    """创建 AI Buddy 计费账户参数"""

    user_id: int = Field(description='用户 ID')
    balance: Decimal = Field(default=Decimal(0), description='初始余额')
    currency: str = Field(default='USD', min_length=1, max_length=16, description='结算币种')
