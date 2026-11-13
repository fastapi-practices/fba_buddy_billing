from backend.common.enums import StrEnum


class FbaBuddyBillingTransactionType(StrEnum):
    """AI Buddy 计费账户流水类型"""

    recharge = 'recharge'
    consume = 'consume'
    adjust = 'adjust'
    refund = 'refund'


class FbaBuddyBillingLedgerStatus(StrEnum):
    """AI Buddy 计费账本状态"""

    billed = 'billed'
    provider_cost = 'provider_cost'
    unpriced = 'unpriced'


class FbaBuddyBillingBudgetWindow(StrEnum):
    """AI Buddy 计费预算窗口"""

    run = 'run'
    conversation = 'conversation'
    day = 'day'
    month = 'month'
    total = 'total'
