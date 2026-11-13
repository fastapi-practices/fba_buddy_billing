from datetime import datetime
from decimal import Decimal

from pydantic import ConfigDict, Field

from backend.common.schema import SchemaBase


class FbaBuddyBillingTransactionQueryParam(SchemaBase):
    """AI Buddy 计费流水查询参数"""

    user_id: int | None = Field(None, description='用户 ID')
    transaction_type: str | None = Field(None, description='流水类型')
    start_time: datetime | None = Field(None, description='开始时间')
    end_time: datetime | None = Field(None, description='结束时间')


class GetFbaBuddyBillingTransactionDetail(SchemaBase):
    """AI Buddy 计费流水详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='流水 ID')
    account_id: int = Field(description='账户 ID')
    user_id: int = Field(description='用户 ID')
    transaction_type: str = Field(description='流水类型')
    amount: Decimal = Field(description='变动金额')
    balance_after: Decimal = Field(description='变动后余额')
    currency: str = Field(description='结算币种')
    reference_type: str = Field(description='关联对象类型')
    reference_id: str = Field(description='关联对象 ID')
    remark: str | None = Field(None, description='备注')
    created_time: datetime = Field(description='创建时间')


class CreateFbaBuddyBillingTransactionParam(SchemaBase):
    """创建 AI Buddy 计费流水参数"""

    account_id: int = Field(description='账户 ID')
    user_id: int = Field(description='用户 ID')
    transaction_type: str = Field(min_length=1, max_length=32, description='流水类型')
    amount: Decimal = Field(description='变动金额')
    balance_after: Decimal = Field(description='变动后余额')
    currency: str = Field(default='USD', min_length=1, max_length=16, description='结算币种')
    reference_type: str = Field(min_length=1, max_length=32, description='关联对象类型')
    reference_id: str = Field(min_length=1, max_length=128, description='关联对象 ID')
    remark: str | None = Field(None, max_length=500, description='备注')
