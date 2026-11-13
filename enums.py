from backend.common.enums import StrEnum


class AIBuddyBillingTransactionType(StrEnum):
    """AI Buddy 计费账户流水类型"""

    recharge = 'recharge'
    consume = 'consume'
    adjust = 'adjust'
    refund = 'refund'


class AIBuddyBillingLedgerStatus(StrEnum):
    """AI Buddy 计费账本状态"""

    billed = 'billed'
    provider_cost = 'provider_cost'
    unpriced = 'unpriced'


class AIBuddyBillingBudgetWindow(StrEnum):
    """AI Buddy 计费预算窗口"""

    run = 'run'
    conversation = 'conversation'
    day = 'day'
    month = 'month'
    total = 'total'
