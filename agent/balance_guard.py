from collections.abc import Awaitable, Callable
from decimal import Decimal

from pydantic_ai import RunContext
from pydantic_ai.capabilities import AbstractCapability
from pydantic_ai.messages import ModelResponse
from pydantic_ai.models import ModelRequestContext

from backend.common.exception import errors
from backend.plugin.ai_buddy.dataclasses import ChatAgentDeps

INSUFFICIENT_BALANCE_CODE = 'billing_balance_insufficient'
INSUFFICIENT_BALANCE_MESSAGE = '计费账户余额不足，请联系管理员充值'


def has_insufficient_balance(
    balance: Decimal | None,
    *,
    minimum: Decimal = Decimal(0),
) -> bool:
    """
    判断计费余额是否已不足以下一轮运行

    :param balance: 账户当前余额，空值表示没有计费账户
    :param minimum: 允许的最低余额，负数表示容许一定负债
    :return:
    """
    return balance is not None and balance <= minimum


class InsufficientBalanceGuard(AbstractCapability[ChatAgentDeps]):
    """余额不足时在模型请求前阻断本轮运行"""

    id = 'billing-balance-guard'

    def __init__(self, *, balance: Decimal | None, minimum: Decimal = Decimal(0)) -> None:
        super().__init__()
        self._balance = balance
        self._minimum = minimum

    async def wrap_model_request(
        self,
        ctx: RunContext[ChatAgentDeps],
        *,
        request_context: ModelRequestContext,
        handler: Callable[[ModelRequestContext], Awaitable[ModelResponse]],
    ) -> ModelResponse:
        """
        在模型请求前校验计费余额

        :param ctx: 运行上下文
        :param request_context: 模型请求上下文
        :param handler: 后续模型请求处理器
        :return:
        """
        if has_insufficient_balance(self._balance, minimum=self._minimum):
            raise errors.RequestError(
                msg=INSUFFICIENT_BALANCE_MESSAGE,
                data={'code': INSUFFICIENT_BALANCE_CODE},
            )
        return await handler(request_context)
