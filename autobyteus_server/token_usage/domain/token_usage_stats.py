from dataclasses import dataclass

@dataclass
class TokenUsageStats:
    """
    Domain model representing aggregated token usage statistics for an LLM model.
    """
    prompt_tokens: int = 0
    assistant_tokens: int = 0
    prompt_token_cost: float = 0.0
    assistant_token_cost: float = 0.0
    total_cost: float = 0.0
