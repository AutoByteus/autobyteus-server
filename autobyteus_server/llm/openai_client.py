# File: autobyteus_server/llm/openai_client.py

from autobyteus.llm.api.openai.openai_chat_api import OpenAIChat
from autobyteus.llm.models import LLMModel

class OpenAIClient:
    async def send_message(self, message: str, model: LLMModel.OpenaiApiModels, system_message: str = "You are a helpful assistant."):
        try:
            chat_api = OpenAIChat(
                model=model.value,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": message}
                ]
            )
            user_message = UserMessage(message)
            response = chat_api.send_messages([user_message])
            
            return response.content
        except Exception as e:
            return f"Error in OpenAI API call: {str(e)}"