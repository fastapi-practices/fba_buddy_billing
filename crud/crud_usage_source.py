from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy_crud_plus import CRUDPlus

from backend.plugin.ai_buddy.model import AIBuddyConversation, AIBuddyMessage
from backend.plugin.ai_buddy_billing.model import AIBuddyBillingLedger


class CRUDAIBuddyBillingUsageSource(CRUDPlus[AIBuddyMessage]):
    """AI Buddy 用量来源查询类"""

    async def get_list(self, db: AsyncSession, *, limit: int) -> list[tuple[AIBuddyMessage, int]]:
        """
        获取尚未归集的 AI Buddy 助手消息

        :param db: 数据库会话
        :param limit: 单次扫描数量
        :return:
        """
        processed = select(AIBuddyBillingLedger.id).where(
            AIBuddyBillingLedger.source_message_id == self.model.id,
            AIBuddyBillingLedger.deleted == 0,
        )
        stmt = (
            select(AIBuddyMessage, AIBuddyConversation.user_id)
            .join(AIBuddyConversation, AIBuddyConversation.conversation_id == self.model.conversation_id)
            .where(
                self.model.deleted == 0,
                self.model.role == 'assistant',
                AIBuddyConversation.deleted == 0,
                ~exists(processed),
            )
            .order_by(self.model.id.asc())
            .limit(limit)
        )
        return list((await db.execute(stmt)).all())


ai_buddy_billing_usage_source_dao: CRUDAIBuddyBillingUsageSource = CRUDAIBuddyBillingUsageSource(AIBuddyMessage)
