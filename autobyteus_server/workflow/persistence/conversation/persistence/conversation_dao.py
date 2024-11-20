from autobyteus_server.workflow.persistence.conversation.domain.models import (
    Message,
    StepConversation,
    ConversationHistory,
)
from typing import List
from datetime import datetime
import pymongo

class ConversationDAO:
    def __init__(self):
        self.client = pymongo.MongoClient("mongodb://localhost:27017/")
        self.db = self.client["autobyteus"]
        self.collection = self.db["conversations"]

    def save_message(self, step_conversation_id: str, message: Message):
        self.collection.update_one(
            {"step_conversation_id": step_conversation_id},
            {"$push": {"messages": message.__dict__}},
            upsert=True
        )

    def update_total_cost(self, step_conversation_id: str, total_cost: float):
        self.collection.update_one(
            {"step_conversation_id": step_conversation_id},
            {"$set": {"total_cost": total_cost}}
        )

    def get_conversation_history(self, step_name: str, page: int, page_size: int) -> ConversationHistory:
        total_conversations = self.collection.count_documents({"step_name": step_name})
        total_pages = (total_conversations + page_size - 1) // page_size
        conversations_cursor = self.collection.find({"step_name": step_name}).skip((page - 1) * page_size).limit(page_size)
        conversations = []
        for doc in conversations_cursor:
            messages = [Message(**msg) for msg in doc.get('messages', [])]
            conversation = StepConversation(
                step_conversation_id=doc['step_conversation_id'],
                step_name=doc['step_name'],
                created_at=doc['created_at'],
                messages=messages,
                total_cost=doc.get('total_cost', 0.0)
            )
            conversations.append(conversation)
        return ConversationHistory(
            conversations=conversations,
            total_conversations=total_conversations,
            total_pages=total_pages,
            current_page=page
        )
    def get_total_cost(
        self,
        step_name: Optional[str],
        start_date: datetime,
        end_date: datetime,
    ) -> float:
        query = {
            "created_at": {"$gte": start_date, "$lte": end_date},
        }
        if step_name:
            query["step_name"] = step_name

        pipeline = [
            {"$match": query},
            {"$group": {"_id": None, "total_cost": {"$sum": "$total_cost"}}},
        ]

        result = list(self.collection.aggregate(pipeline))
        if result:
            return result[0]["total_cost"]
        else:
            return 0.0

    # Other methods...