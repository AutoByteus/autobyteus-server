import strawberry

@strawberry.type
class UsageStatistics:
    """
    GraphQL type representing usage statistics per LLM model.
    """
    llm_model: str
    prompt_tokens: int
    assistant_tokens: int
    prompt_cost: float
    assistant_cost: float
    total_cost: float
