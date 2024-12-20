import strawberry

@strawberry.type
class StepResponse:
    conversation_id: str
    message_chunk: str
    is_complete: bool