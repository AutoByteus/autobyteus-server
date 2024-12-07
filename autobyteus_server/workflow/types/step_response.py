from dataclasses import dataclass

@dataclass
class StepResponseData:
    """
    Data class representing a step response with streaming state.
    
    Attributes:
        message (str): The response message content
        is_complete (bool): Indicates if this is the final complete response (True) 
                          or a streaming chunk (False)
    """
    message: str
    is_complete: bool