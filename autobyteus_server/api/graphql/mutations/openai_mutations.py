import strawberry
from typing import Optional
from autobyteus.llm.api.openai.openai_chat_api import OpenAIChat
from autobyteus.llm.api.openai.message_types import UserMessage
from ..types.llm_model_types import LLMModel

@strawberry.type
class OpenAIMutation:
    @strawberry.mutation
    async def send_openai_message(
        self, 
        message: str, 
        model: LLMModel,
        system_message: Optional[str] = None
    ) -> str:
        try:
            chat_api = OpenAIChat(
                model_name=model,
                system_message=system_message if system_message else "You are a helpful assistant."
            )
            
            user_message = UserMessage(message)
            response = chat_api.send_messages([user_message])
            
            return response.content
        except Exception as e:
            return f"Error in OpenAI API call: {str(e)}"