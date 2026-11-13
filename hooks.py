import asyncio

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.common.log import log
from backend.database.db import async_db_session
from backend.plugin.ai_buddy.agent.capabilities.extensions import register_ai_buddy_capability_builder
from backend.plugin.fba_buddy_billing.service.budget_service import fba_buddy_billing_budget_service
from backend.plugin.fba_buddy_billing.service.ledger_service import fba_buddy_billing_ledger_service

_RECONCILE_INTERVAL_SECONDS = 60


async def _reconcile_loop() -> None:
    """周期归集 AI Buddy 用量"""
    while True:
        try:
            async with async_db_session.begin() as db:
                result = await fba_buddy_billing_ledger_service.reconcile(db=db)
            if result.recorded:
                log.info(f'AI Buddy 计费归集完成 recorded={result.recorded} billed={result.billed}')
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            log.warning(f'AI Buddy 计费归集失败: {exc}')
        await asyncio.sleep(_RECONCILE_INTERVAL_SECONDS)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    管理计费归集后台任务

    :param app: FastAPI 应用
    :return:
    """
    task = asyncio.create_task(_reconcile_loop(), name='fba-buddy-billing-reconciler')
    try:
        yield
    finally:
        task.cancel()
        await asyncio.gather(task, return_exceptions=True)


def setup(app: FastAPI) -> None:
    """
    登记计费插件运行参数

    :param app: FastAPI 应用
    :return:
    """
    app.state.fba_buddy_billing_reconcile_interval = _RECONCILE_INTERVAL_SECONDS
    register_ai_buddy_capability_builder(fba_buddy_billing_budget_service.build_spend_limits)
