import strawberry
from typing import Optional
from autobyteus.llm.models import LLMModel as OriginalLLMModel
from enum import Enum

@strawberry.enum
class LLMModel(str, Enum):
    # NVIDIA Models
    NVIDIA_LLAMA_3_1_NEMOTRON_70B_INSTRUCT_API = "nvidia/llama-3.1-nemotron-70b-instruct"

    # OpenAI models
    GPT_4o = "GPT-4o-rpa"
    o1_PREVIEW = "o1-preview-rpa"
    o1_MINI = "o1-mini-rpa"

    GPT_4o_API = "gpt-4o"
    O1_PREVIEW_API = "o1-preview"
    O1_MINI_API = "o1-mini"
    CHATGPT_4O_LATEST_API = "chatgpt-4o-latest"
    GPT_3_5_TURBO_API = "gpt-3.5-turbo"
    OPENROUTER_O1_MINI_API = "openai/o1-mini-2024-09-12"

    # Mistral models
    MISTRAL_SMALL = "mistral-small-rpa"
    MISTRAL_MEDIUM = "mistral-medium-rpa"
    MISTRAL_LARGE = "mistral-large-rpa"
    MISTRAL_SMALL_API = "mistral-small"
    MISTRAL_MEDIUM_API = "mistral-medium"
    MISTRAL_LARGE_API = "mistral-large-latest"

    # Groq models
    GEMMA_2_9B_IT = "gemma2-9b-it-rpa"
    GEMMA_7B_IT = "gemma-7b-it-rpa"
    LLAMA_3_1_405B_REASONING = "llama-3-1-405b-reasoning-rpa"
    LLAMA_3_1_70B_VERSATILE = "llama-3-1-70b-versatile-rpa"
    LLAMA_3_1_8B_INSTANT = "llama-3-1-8b-instant-rpa"
    LLAMA3_70B_8192 = "llama3-70b-8192-rpa"
    LLAMA3_8B_8192 = "llama3-8b-8192-rpa"
    MIXTRAL_8X7B_32768 = "mixtral-8x7b-32768-rpa"
    GEMMA_2_9B_IT_API = "gemma2-9b-it"
    GEMMA_7B_IT_API = "gemma-7b-it"
    LLAMA_3_1_405B_REASONING_API = "llama-3-1-405b-reasoning"
    LLAMA_3_1_70B_VERSATILE_API = "llama-3-1-70b-versatile"
    LLAMA_3_1_8B_INSTANT_API = "llama-3-1-8b-instant"
    LLAMA3_70B_8192_API = "llama3-70b-8192"
    LLAMA3_8B_8192_API = "llama3-8b-8192"
    MIXTRAL_8X7B_32768_API = "mixtral-8x7b-32768"

    # Gemini models
    GEMINI_1_0_PRO = "gemini-1-0-pro-rpa"
    GEMINI_1_5_PRO = "gemini-1-5-pro-rpa"
    GEMINI_1_5_PRO_EXPERIMENTAL = "gemini-1-5-pro-experimental-rpa"
    GEMINI_1_5_FLASH = "gemini-1-5-flash-rpa"
    GEMMA_2_2B = "gemma-2-2b-rpa"
    GEMMA_2_9B = "gemma-2-9b-rpa"
    GEMMA_2_27B = "gemma-2-27b-rpa"
    GEMINI_1_0_PRO_API = "gemini-1-0-pro"
    GEMINI_1_5_PRO_API = "gemini-1-5-pro"
    GEMINI_1_5_PRO_EXPERIMENTAL_API = "gemini-1-5-pro-experimental"
    GEMINI_1_5_FLASH_API = "gemini-1.5-flash"
    GEMMA_2_2B_API = "gemma-2-2b"
    GEMMA_2_9B_API = "gemma-2-9b"
    GEMMA_2_27B_API = "gemma-2-27b"

    # Claude models
    CLAUDE_3_HAIKU = "Claude3Haiku-rpa"
    CLAUDE_3_OPUS = "Claude3Opus-rpa"
    CLAUDE_3_5_SONNET = "Claude35Sonnet-rpa"

    CLAUDE_3_OPUS_API = "claude-3-opus-20240229"
    CLAUDE_3_SONNET_API = "claude-3-sonnet-20240229"
    CLAUDE_3_HAIKU_API = "claude-3-haiku-20240307"
    CLAUDE_3_5_SONNET_API = "claude-3-5-sonnet-20240620"
    BEDROCK_CLAUDE_3_5_SONNET_API = "anthropic.claude-3-5-sonnet-20240620-v1:0"

    # Perplexity models
    LLAMA_3_1_SONAR_LARGE_128K_ONLINE = "llama-3-1-sonar-large-128k-online-rpa"
    LLAMA_3_1_SONAR_SMALL_128K_ONLINE = "llama-3-1-sonar-small-128k-online-rpa"
    LLAMA_3_1_SONAR_LARGE_128K_CHAT = "llama-3-1-sonar-large-128k-chat-rpa"
    LLAMA_3_1_SONAR_SMALL_128K_CHAT = "llama-3-1-sonar-small-128k-chat-rpa"
    LLAMA_3_1_8B_INSTRUCT = "llama-3-1-8b-instruct-rpa"
    LLAMA_3_1_70B_INSTRUCT = "llama-3-1-70b-instruct-rpa"
    GEMMA_2_27B_IT = "gemma-2-27b-it-rpa"
    NEMOTRON_4_340B_INSTRUCT = "nemotron-4-340b-instruct-rpa"
    MIXTRAL_8X7B_INSTRUCT = "mixtral-8x7b-instruct-rpa"
    LLAMA_3_1_SONAR_LARGE_128K_ONLINE_API = "llama-3-1-sonar-large-128k-online"
    LLAMA_3_1_SONAR_SMALL_128K_ONLINE_API = "llama-3-1-sonar-small-128k-online"
    LLAMA_3_1_SONAR_LARGE_128K_CHAT_API = "llama-3-1-sonar-large-128k-chat"
    LLAMA_3_1_SONAR_SMALL_128K_CHAT_API = "llama-3-1-sonar-small-128k-chat"
    LLAMA_3_1_8B_INSTRUCT_API = "llama-3-1-8b-instruct"
    LLAMA_3_1_70B_INSTRUCT_API = "llama-3-1-70b-instruct"
    GEMMA_2_27B_IT_API = "gemma-2-27b-it"
    NEMOTRON_4_340B_INSTRUCT_API = "nemotron-4-340b-instruct"
    MIXTRAL_8X7B_INSTRUCT_API = "mixtral-8x7b-instruct"

    def __str__(self):
        return self.value

def convert_to_original_llm_model(model: Optional[LLMModel]) -> Optional[OriginalLLMModel]:
    if model is None:
        return None
    return OriginalLLMModel.from_name(model.name)
