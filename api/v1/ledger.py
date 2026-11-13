from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request

from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction
from backend.plugin.fba_buddy_billing.schema.ledger import (
    FbaBuddyBillingLedgerQueryParam,
    GetFbaBuddyBillingLedgerDetail,
    GetFbaBuddyBillingReconcileDetail,
    GetFbaBuddyBillingSummaryDetail,
)
from backend.plugin.fba_buddy_billing.service.ledger_service import fba_buddy_billing_ledger_service

router = APIRouter()


@router.get(
    '/ledger',
    summary='分页获取 AI Buddy 用量账本',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_fba_buddy_billing_ledgers_paginated(
    request: Request,
    db: CurrentSession,
    query: Annotated[FbaBuddyBillingLedgerQueryParam, Query()],
) -> ResponseSchemaModel[PageData[GetFbaBuddyBillingLedgerDetail]]:
    user_id = query.user_id if request.user.is_superuser else request.user.id
    data = await fba_buddy_billing_ledger_service.get_list(
        db=db,
        user_id=user_id,
        conversation_id=query.conversation_id,
        provider_id=query.provider_id,
        model_id=query.model_id,
        status=query.status,
        start_time=query.start_time,
        end_time=query.end_time,
    )
    return response_base.success(data=data)


@router.get('/summary', summary='获取 AI Buddy 用量汇总', dependencies=[DependsJwtAuth])
async def get_fba_buddy_billing_summary(
    request: Request,
    db: CurrentSession,
    query: Annotated[FbaBuddyBillingLedgerQueryParam, Query()],
) -> ResponseSchemaModel[GetFbaBuddyBillingSummaryDetail]:
    user_id = query.user_id if request.user.is_superuser else request.user.id
    data = await fba_buddy_billing_ledger_service.get_summary(
        db=db,
        user_id=user_id,
        start_time=query.start_time,
        end_time=query.end_time,
    )
    return response_base.success(data=data)


@router.post(
    '/reconcile',
    summary='归集 AI Buddy 用量',
    dependencies=[
        Depends(RequestPermission('ai:billing:reconcile')),
        DependsRBAC,
    ],
)
async def reconcile_fba_buddy_billing(
    db: CurrentSessionTransaction,
) -> ResponseSchemaModel[GetFbaBuddyBillingReconcileDetail]:
    data = await fba_buddy_billing_ledger_service.reconcile(db=db)
    return response_base.success(data=data)
