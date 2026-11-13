from datetime import datetime
from decimal import Decimal
from typing import Self

from pydantic import ConfigDict, Field, model_validator

from backend.common.enums import StatusType
from backend.common.schema import SchemaBase
from backend.plugin.fba_buddy_billing.enums import FbaBuddyBillingBudgetWindow


class FbaBuddyBillingBudgetQueryParam(SchemaBase):
    """AI Buddy 计费预算查询参数"""

    user_id: int | None = Field(None, description='用户 ID')
    window: FbaBuddyBillingBudgetWindow | None = Field(None, description='预算窗口')
    status: StatusType | None = Field(None, description='状态')


class FbaBuddyBillingBudgetSchemaBase(SchemaBase):
    """AI Buddy 计费预算基础模型"""

    user_id: int = Field(description='用户 ID')
    window: FbaBuddyBillingBudgetWindow = Field(description='预算窗口')
    usd_limit: Decimal | None = Field(None, gt=0, description='USD 上限')
    token_limit: int | None = Field(None, gt=0, description='token 总量上限')
    warn_at: float | None = Field(None, gt=0, le=1, description='预警比例')
    status: StatusType = Field(default=StatusType.enable, description='状态')


class CreateFbaBuddyBillingBudgetParam(FbaBuddyBillingBudgetSchemaBase):
    """创建 AI Buddy 计费预算参数"""

    @model_validator(mode='after')
    def validate_limits(self) -> Self:
        """校验预算至少配置一个上限"""
        if self.usd_limit is None and self.token_limit is None:
            raise ValueError('USD 和 token 上限至少配置一个')
        return self


class UpdateFbaBuddyBillingBudgetParam(SchemaBase):
    """更新 AI Buddy 计费预算参数"""

    usd_limit: Decimal | None = Field(None, gt=0, description='USD 上限')
    token_limit: int | None = Field(None, gt=0, description='token 总量上限')
    warn_at: float | None = Field(None, gt=0, le=1, description='预警比例')
    status: StatusType | None = Field(None, description='状态')


class GetFbaBuddyBillingBudgetDetail(FbaBuddyBillingBudgetSchemaBase):
    """AI Buddy 计费预算详情"""

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(description='预算 ID')
    created_time: datetime = Field(description='创建时间')
    updated_time: datetime | None = Field(None, description='更新时间')
