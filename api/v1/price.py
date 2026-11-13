from typing import Annotated

from fastapi import APIRouter, Depends, Path, Query

from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import (
    ResponseModel,
    ResponseSchemaModel,
    response_base,
)
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction
from backend.plugin.ai_buddy_billing.schema.price import (
    AIBuddyBillingPriceQueryParam,
    CreateAIBuddyBillingPriceParam,
    GetAIBuddyBillingPriceDetail,
    UpdateAIBuddyBillingPriceParam,
)
from backend.plugin.ai_buddy_billing.service.price_service import ai_buddy_billing_price_service

router = APIRouter()


@router.get(
    '/active',
    summary='获取当前生效的 AI Buddy 模型价格',
    dependencies=[DependsJwtAuth],
)
async def get_active_ai_buddy_billing_prices(
    db: CurrentSession,
    query: Annotated[AIBuddyBillingPriceQueryParam, Query()],
) -> ResponseSchemaModel[list[GetAIBuddyBillingPriceDetail]]:
    data = await ai_buddy_billing_price_service.get_all(
        db=db,
        provider_id=query.provider_id,
        model_id=query.model_id,
    )
    return response_base.success(data=data)


@router.get(
    '',
    summary='分页获取 AI Buddy 模型价格',
    dependencies=[
        DependsJwtAuth,
        DependsPagination,
    ],
)
async def get_ai_buddy_billing_prices_paginated(
    db: CurrentSession,
    query: Annotated[AIBuddyBillingPriceQueryParam, Query()],
) -> ResponseSchemaModel[PageData[GetAIBuddyBillingPriceDetail]]:
    data = await ai_buddy_billing_price_service.get_list(
        db=db,
        provider_id=query.provider_id,
        model_id=query.model_id,
        active=query.active,
    )
    return response_base.success(data=data)


@router.post(
    '',
    summary='创建 AI Buddy 模型价格',
    dependencies=[
        Depends(RequestPermission('ai:billing:price:add')),
        DependsRBAC,
    ],
)
async def create_ai_buddy_billing_price(
    db: CurrentSessionTransaction,
    obj: CreateAIBuddyBillingPriceParam,
) -> ResponseSchemaModel[GetAIBuddyBillingPriceDetail]:
    data = await ai_buddy_billing_price_service.create(db=db, obj=obj)
    return response_base.success(data=data)


@router.put(
    '/{pk}',
    summary='更新 AI Buddy 模型价格',
    dependencies=[
        Depends(RequestPermission('ai:billing:price:edit')),
        DependsRBAC,
    ],
)
async def update_ai_buddy_billing_price(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='价格 ID')],
    obj: UpdateAIBuddyBillingPriceParam,
) -> ResponseSchemaModel[GetAIBuddyBillingPriceDetail]:
    data = await ai_buddy_billing_price_service.update(db=db, pk=pk, obj=obj)
    return response_base.success(data=data)


@router.delete(
    '/{pk}',
    summary='删除 AI Buddy 模型价格',
    dependencies=[
        Depends(RequestPermission('ai:billing:price:del')),
        DependsRBAC,
    ],
)
async def delete_ai_buddy_billing_price(
    db: CurrentSessionTransaction,
    pk: Annotated[int, Path(description='价格 ID')],
) -> ResponseModel:
    await ai_buddy_billing_price_service.delete(db=db, pk=pk)
    return response_base.success()
