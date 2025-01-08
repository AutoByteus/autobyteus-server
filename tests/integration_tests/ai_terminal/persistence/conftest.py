
import pytest

@pytest.fixture
def sample_conversation_data():
    """
    Provides sample conversation data for AI Terminal tests.
    """
    return {
        "conversation_id": "test-conversation-id",
        "role": "user",
        "message": "Hello from AI Terminal!"
    }
