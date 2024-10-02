import strawberry

@strawberry.input
class ContextFilePathInput:
    path: str
    type: str
