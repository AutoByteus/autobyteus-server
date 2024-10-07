import strawberry
from typing import Optional
from autobyteus.llm.models import LLMModel as OriginalLLMModel
from enum import Enum

@strawberry.enum
class LLMModel(Enum):
    class OpenAIRpaModels(Enum):
        GPT_3_5_TURBO = "gpt-3.5-turbo"
        GPT_4 = "gpt-4"
        GPT_4_0613 = "gpt-4-0613"
        GPT_4o = "GPT-4o"
        o1_PREVIEW = "o1-preview"
        o1_MINI = "o1-mini"
    class OpenaiApiModels(Enum):

        GPT_3_5_TURBO_API = "gpt-3.5-turbo-api"
        GPT_4_API = "gpt-4-api"
        GPT_4_0613_API = "gpt-4-0613-api"
        GPT_4o_API = "gpt-4o-api"
        o1_PREVIEW_API = "o1-preview-api"
        o1_MINI_API = "o1-mini-api"

    class MistralRpaModels(Enum):
        MISTRAL_SMALL = "mistral-small"
        MISTRAL_MEDIUM = "mistral-medium"
        MISTRAL_LARGE = "mistral-large"
    class MistralApiModels(Enum):
        MISTRAL_SMALL_API = "mistral-small-api"
        MISTRAL_MEDIUM_API = "mistral-medium-api"
        MISTRAL_LARGE_API = "mistral-large-api"

    class GroqRpaModels(Enum):
        GEMMA_2_9B_IT = "gemma2-9b-it"
        GEMMA_7B_IT = "gemma-7b-it"
        LLAMA_3_1_405B_REASONING = "llama-3-1-405b-reasoning"
        LLAMA_3_1_70B_VERSATILE = "llama-3-1-70b-versatile"
        LLAMA_3_1_8B_INSTANT = "llama-3-1-8b-instant"
        LLAMA3_70B_8192 = "llama3-70b-8192"
        LLAMA3_8B_8192 = "llama3-8b-8192"
        MIXTRAL_8X7B_32768 = "mixtral-8x7b-32768"
    class GroqApiModels(Enum):

        GEMMA_2_9B_IT_API = "gemma2-9b-it-api"
        GEMMA_7B_IT_API = "gemma-7b-it-api"
        LLAMA_3_1_405B_REASONING_API = "llama-3-1-405b-reasoning-api"
        LLAMA_3_1_70B_VERSATILE_API = "llama-3-1-70b-versatile-api"
        LLAMA_3_1_8B_INSTANT_API = "llama-3-1-8b-instant-api"
        LLAMA3_70B_8192_API = "llama3-70b-8192-api"
        LLAMA3_8B_8192_API = "llama3-8b-8192-api"
        MIXTRAL_8X7B_32768_API = "mixtral-8x7b-32768-api"

    class GeminiRpaModels(Enum):
        GEMINI_1_0_PRO = "gemini-1-0-pro"
        GEMINI_1_5_PRO = "gemini-1-5-pro"
        GEMINI_1_5_PRO_EXPERIMENTAL = "gemini-1-5-pro-experimental"
        GEMINI_1_5_FLASH = "gemini-1-5-flash"
        GEMMA_2_2B = "gemma-2-2b"
        GEMMA_2_9B = "gemma-2-9b"
        GEMMA_2_27B = "gemma-2-27b"

    class GeminiApiModels(Enum):
        GEMINI_1_0_PRO_API = "gemini-1-0-pro-api"
        GEMINI_1_5_PRO_API = "gemini-1-5-pro-api"
        GEMINI_1_5_PRO_EXPERIMENTAL_API = "gemini-1-5-pro-experimental-api"
        GEMINI_1_5_FLASH_API = "gemini-1-5-flash-api"
        GEMMA_2_2B_API = "gemma-2-2b-api"
        GEMMA_2_9B_API = "gemma-2-9b-api"
        GEMMA_2_27B_API = "gemma-2-27b-api"

    class ClaudeRpaModels(Enum):
        CLAUDE_3_HAIKU = "Claude3Haiku"
        CLAUDE_3_OPUS = "Claude3Opus"
        CLAUDE_3_5_SONNET = "Claude35Sonnet"
    class ClaudeApiModels(Enum):

        CLAUDE_3_HAIKU_API = "Claude3Haiku-api"
        CLAUDE_3_OPUS_API = "Claude3Opus-api"
        CLAUDE_3_5_SONNET_API = "Claude35Sonnet-api"

    class PerplexityRpaModels(Enum):
        LLAMA_3_1_SONAR_LARGE_128K_ONLINE = "llama-3-1-sonar-large-128k-online"
        LLAMA_3_1_SONAR_SMALL_128K_ONLINE = "llama-3-1-sonar-small-128k-online"
        LLAMA_3_1_SONAR_LARGE_128K_CHAT = "llama-3-1-sonar-large-128k-chat"
        LLAMA_3_1_SONAR_SMALL_128K_CHAT = "llama-3-1-sonar-small-128k-chat"
        LLAMA_3_1_8B_INSTRUCT = "llama-3-1-8b-instruct"
        LLAMA_3_1_70B_INSTRUCT = "llama-3-1-70b-instruct"
        GEMMA_2_27B_IT = "gemma-2-27b-it"
        NEMOTRON_4_340B_INSTRUCT = "nemotron-4-340b-instruct"
        MIXTRAL_8X7B_INSTRUCT = "mixtral-8x7b-instruct"
    class PerplexityApiModels(Enum):

        LLAMA_3_1_SONAR_LARGE_128K_ONLINE_API = "llama-3-1-sonar-large-128k-online-api"
        LLAMA_3_1_SONAR_SMALL_128K_ONLINE_API = "llama-3-1-sonar-small-128k-online-api"
        LLAMA_3_1_SONAR_LARGE_128K_CHAT_API = "llama-3-1-sonar-large-128k-chat-api"
        LLAMA_3_1_SONAR_SMALL_128K_CHAT_API = "llama-3-1-sonar-small-128k-chat-api"
        LLAMA_3_1_8B_INSTRUCT_API = "llama-3-1-8b-instruct-api"
        LLAMA_3_1_70B_INSTRUCT_API = "llama-3-1-70b-instruct-api"
        GEMMA_2_27B_IT_API = "gemma-2-27b-it-api"
        NEMOTRON_4_340B_INSTRUCT_API = "nemotron-4-340b-instruct-api"
        MIXTRAL_8X7B_INSTRUCT_API = "mixtral-8x7b-instruct-api"

def convert_to_original_llm_model(model: Optional[LLMModel]) -> Optional[OriginalLLMModel]:
    if model is None:
        return None
    if isinstance(model, LLMModel.OpenAIRpaModels):
        return OriginalLLMModel.OpenAIRpaModels(model.value)
    if isinstance(model, LLMModel.OpenaiApiModels):
        return OriginalLLMModel.OpenaiApiModels(model.value)
    if isinstance(model, LLMModel.MistralRpaModels):
        return OriginalLLMModel.MistralRpaModels(model.value)
    if isinstance(model, LLMModel.MistralApiModels):
        return OriginalLLMModel.MistralApiModels(model.value)
    if isinstance(model, LLMModel.GroqRpaModels):
        return OriginalLLMModel.GroqRpaModels(model.value)
    if isinstance(model, LLMModel.GroqApiModels):
        return OriginalLLMModel.GroqApiModels(model.value)
    if isinstance(model, LLMModel.GeminiRpaModels):
        return OriginalLLMModel.GeminiRpaModels(model.value)
    if isinstance(model, LLMModel.GeminiApiModels):
        return OriginalLLMModel.GeminiApiModels(model.value)
    if isinstance(model, LLMModel.ClaudeRpaModels):
        return OriginalLLMModel.ClaudeRpaModels(model.value)
    if isinstance(model, LLMModel.ClaudeApiModels):
        return OriginalLLMModel.ClaudeApiModels(model.value)
    if isinstance(model, LLMModel.PerplexityRpaModels):
        return OriginalLLMModel.PerplexityRpaModels(model.value)
    if isinstance(model, LLMModel.PerplexityApiModels):
        return OriginalLLMModel.PerplexityApiModels(model.value)
    raise ValueError(f"Invalid LLMModel: {model}")