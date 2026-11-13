from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction
from backend.plugin.ai_buddy_billing.schema.account import (
    AIBuddyBillingAccountQueryParam,
    CreateAIBuddyBillingAdjustmentParam,
    CreateAIBuddyBillingRechargeParam,
    GetAIBuddyBillingAccountDetail,
)
from backend.plugin.ai_buddy_billing.schema.transaction import (
    AIBuddyBillingTransactionQueryParam,
    GetAIBuddyBillingTransactionDetail,
)
from backend.plugin.ai_buddy_billing.service.account_service import ai_buddy_billing_account_service

router = APIRouter()


@router.get(
    '',
    summary='分页获取 AI Buddy 计费账户',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
        Depends(RequestPermission('ai:billing:account:list')),
        DependsRBAC,
    ],
)
async def get_ai_buddy_billing_accounts_paginated(
    db: CurrentSession,
    query: Annotated[AIBuddyBillingAccountQueryParam, Query()],
) -> ResponseSchemaModel[PageData[GetAIBuddyBillingAccountDetail]]:
    data = await ai_buddy_billing_account_service.get_list(db=db, user_id=query.user_id)
    return response_base.success(data=data)


@router.get('/me', summary='获取我的 AI Buddy 计费账户', dependencies=[DependsJwtAuth])
async def get_my_ai_buddy_billing_account(
    request: Request,
    db: CurrentSession,
) -> ResponseSchemaModel[GetAIBuddyBillingAccountDetail]:
    data = await ai_buddy_billing_account_service.get(db=db, user_id=request.user.id)
    return response_base.success(data=data)


@router.get(
    '/transactions',
    summary='分页获取 AI Buddy 计费流水',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_ai_buddy_billing_transactions_paginated(
    request: Request,
    db: CurrentSession,
    query: Annotated[AIBuddyBillingTransactionQueryParam, Query()],
) -> ResponseSchemaModel[PageData[GetAIBuddyBillingTransactionDetail]]:
    user_id = query.user_id if request.user.is_superuser else request.user.id
    data = await ai_buddy_billing_account_service.get_transaction_list(
        db=db,
        user_id=user_id,
        transaction_type=query.transaction_type,
        start_time=query.start_time,
        end_time=query.end_time,
    )
    return response_base.success(data=data)


@router.post(
    '/recharges',
    summary='为 AI Buddy 计费账户充值',
    dependencies=[
        Depends(RequestPermission('ai:billing:account:recharge')),
        DependsRBAC,
    ],
)
async def recharge_ai_buddy_billing_account(
    db: CurrentSessionTransaction,
    obj: CreateAIBuddyBillingRechargeParam,
) -> ResponseSchemaModel[GetAIBuddyBillingAccountDetail]:
    data = await ai_buddy_billing_account_service.recharge(db=db, obj=obj)
    return response_base.success(data=data)


@router.post(
    '/adjustments',
    summary='调整 AI Buddy 计费账户余额',
    dependencies=[
        Depends(RequestPermission('ai:billing:account:adjust')),
        DependsRBAC,
    ],
)
async def adjust_ai_buddy_billing_account(
    db: CurrentSessionTransaction,
    obj: CreateAIBuddyBillingAdjustmentParam,
) -> ResponseSchemaModel[GetAIBuddyBillingAccountDetail]:
    data = await ai_buddy_billing_account_service.adjust(db=db, obj=obj)
    return response_base.success(data=data)
