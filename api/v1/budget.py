from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query, Request

from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseModel, ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction
from backend.plugin.fba_buddy_billing.schema.budget import (
    CreateFbaBuddyBillingBudgetParam,
    FbaBuddyBillingBudgetQueryParam,
    GetFbaBuddyBillingBudgetDetail,
    UpdateFbaBuddyBillingBudgetParam,
)
from backend.plugin.fba_buddy_billing.service.budget_service import fba_buddy_billing_budget_service

router = APIRouter()


@router.get(
    '',
    summary='分页获取 AI Buddy 计费预算',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_fba_buddy_billing_budgets_paginated(
    request: Request,
    db: CurrentSession,
    query: Annotated[FbaBuddyBillingBudgetQueryParam, Query()],
) -> ResponseSchemaModel[PageData[GetFbaBuddyBillingBudgetDetail]]:
    user_id = query.user_id if request.user.is_superuser else request.user.id
    data = await fba_buddy_billing_budget_service.get_list(
        db=db,
        user_id=user_id,
        window=query.window,
        status=query.status,
    )
    return response_base.success(data=data)


@router.post(
    '',
    summary='创建 AI Buddy 计费预算',
    dependencies=[
        Depends(RequestPermission('ai:billing:budget:add')),
        DependsRBAC,
    ],
)
async def create_fba_buddy_billing_budget(
    db: CurrentSessionTransaction,
    obj: CreateFbaBuddyBillingBudgetParam,
) -> ResponseSchemaModel[GetFbaBuddyBillingBudgetDetail]:
    data = await fba_buddy_billing_budget_service.create(db=db, obj=obj)
    return response_base.success(data=data)


@router.put(
    '/{pk}',
    summary='更新 AI Buddy 计费预算',
    dependencies=[
        Depends(RequestPermission('ai:billing:budget:edit')),
        DependsRBAC,
    ],
)
async def update_fba_buddy_billing_budget(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='预算 ID')],
    obj: UpdateFbaBuddyBillingBudgetParam,
) -> ResponseSchemaModel[GetFbaBuddyBillingBudgetDetail]:
    data = await fba_buddy_billing_budget_service.update(db=db, pk=pk, obj=obj)
    return response_base.success(data=data)


@router.delete(
    '/{pk}',
    summary='删除 AI Buddy 计费预算',
    dependencies=[
        Depends(RequestPermission('ai:billing:budget:del')),
        DependsRBAC,
    ],
)
async def delete_fba_buddy_billing_budget(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='预算 ID')],
) -> ResponseModel:
    await fba_buddy_billing_budget_service.delete(db=db, pk=pk)
    return response_base.success()
