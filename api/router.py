from fastapi import APIRouter

from backend.core.conf import settings
from backend.plugin.ai_buddy_billing.api.v1.account import router as account_router
from backend.plugin.ai_buddy_billing.api.v1.budget import router as budget_router
from backend.plugin.ai_buddy_billing.api.v1.ledger import router as ledger_router
from backend.plugin.ai_buddy_billing.api.v1.price import router as price_router

v1 = APIRouter(prefix=settings.FASTAPI_API_V1_PATH)

v1.include_router(price_router, prefix='/ai-buddy-billing/prices', tags=['AI Buddy 计费价格'])
v1.include_router(account_router, prefix='/ai-buddy-billing/accounts', tags=['AI Buddy 计费账户'])
v1.include_router(budget_router, prefix='/ai-buddy-billing/budgets', tags=['AI Buddy 计费预算'])
v1.include_router(ledger_router, prefix='/ai-buddy-billing', tags=['AI Buddy 计费账本'])
