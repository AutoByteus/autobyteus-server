import pytest
from typing import Any, Dict

@pytest.fixture
def sample_message_data() -> Dict[str, Any]:
    """
    Provides sample message data for testing.
    
    Returns:
        Dict containing test message data with conversation ID, role, and message content
    """
    return {
        "conversation_id": 1,  # Assuming an existing conversation ID for PostgreSQL
        "role": "user",
        "message": "Hello, World!"
    }