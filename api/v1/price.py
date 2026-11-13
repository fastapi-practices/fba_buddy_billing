from typing import Annotated

from fastapi import APIRouter, Depends, Query

from backend.common.pagination import DependsPagination, PageData
from backend.common.response.response_schema import ResponseSchemaModel, response_base
from backend.common.security.jwt import DependsJwtAuth
from backend.common.security.permission import RequestPermission
from backend.common.security.rbac import DependsRBAC
from backend.database.db import CurrentSession, CurrentSessionTransaction
from backend.plugin.fba_buddy_billing.schema.price import (
    CreateFbaBuddyBillingPriceParam,
    FbaBuddyBillingPriceQueryParam,
    GetFbaBuddyBillingPriceDetail,
)
from backend.plugin.fba_buddy_billing.service.price_service import fba_buddy_billing_price_service

router = APIRouter()


@router.get(
    '/active',
    summary='获取当前生效的 AI Buddy 模型价格',
    dependencies=[DependsJwtAuth],
)
async def get_active_fba_buddy_billing_prices(
    db: CurrentSession,
    query: Annotated[FbaBuddyBillingPriceQueryParam, Query()],
) -> ResponseSchemaModel[list[GetFbaBuddyBillingPriceDetail]]:
    data = await fba_buddy_billing_price_service.get_all(
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
async def get_fba_buddy_billing_prices_paginated(
    db: CurrentSession,
    query: Annotated[FbaBuddyBillingPriceQueryParam, Query()],
) -> ResponseSchemaModel[PageData[GetFbaBuddyBillingPriceDetail]]:
    data = await fba_buddy_billing_price_service.get_list(
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
async def create_fba_buddy_billing_price(
    db: CurrentSessionTransaction,
    obj: CreateFbaBuddyBillingPriceParam,
) -> ResponseSchemaModel[GetFbaBuddyBillingPriceDetail]:
    data = await fba_buddy_billing_price_service.create(db=db, obj=obj)
    return response_base.success(data=data)
