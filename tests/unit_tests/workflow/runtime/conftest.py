import pytest
import asyncio
from autobyteus_server.workflow.runtime.agent_runtime import AgentRuntime

@pytest.fixture
def cleanup_agent_runtime():
    """Fixture to cleanup AgentRuntime between tests"""
    yield
    runtime = AgentRuntime()
    runtime.shutdown()
    # Reset the singleton instance
    AgentRuntime._instances = {}

@pytest.fixture
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def agent_runtime():
    """Fixture to provide a clean AgentRuntime instance"""
    runtime = AgentRuntime()
    yield runtime
    await asyncio.sleep(0.1)  # Allow pending tasks to complete
    runtime.shutdown()