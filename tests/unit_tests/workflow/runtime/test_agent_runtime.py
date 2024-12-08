import pytest
import asyncio
import threading
import time
from unittest.mock import Mock, patch
from autobyteus_server.workflow.runtime.agent_runtime import AgentRuntime

async def dummy_coroutine():
    """Helper coroutine for testing"""
    await asyncio.sleep(0.1)
    return "test_result"

async def failing_coroutine():
    """Helper coroutine that raises an exception"""
    await asyncio.sleep(0.1)
    raise ValueError("Test error")

def test_singleton_pattern(cleanup_agent_runtime):
    """Test that AgentRuntime follows the singleton pattern"""
    runtime1 = AgentRuntime()
    runtime2 = AgentRuntime()
    assert runtime1 is runtime2

def test_initialization(cleanup_agent_runtime):
    """Test that runtime is properly initialized"""
    runtime = AgentRuntime()
    assert isinstance(runtime._thread, threading.Thread)
    assert runtime._thread.is_alive()
    assert runtime._loop is not None

def test_execute_coroutine_success(cleanup_agent_runtime):
    """Test successful execution of a coroutine"""
    runtime = AgentRuntime()
    future = runtime.execute_coroutine(dummy_coroutine())
    result = future.result(timeout=1.0)
    assert result == "test_result"

def test_execute_coroutine_failure(cleanup_agent_runtime):
    """Test handling of failing coroutine"""
    runtime = AgentRuntime()
    future = runtime.execute_coroutine(failing_coroutine())
    with pytest.raises(ValueError, match="Test error"):
        future.result(timeout=1.0)

def test_execute_coroutine_without_initialization(cleanup_agent_runtime):
    """Test error handling when runtime is not initialized"""
    runtime = AgentRuntime()
    runtime._loop = None
    with pytest.raises(RuntimeError, match="Runtime environment not initialized"):
        runtime.execute_coroutine(dummy_coroutine())

def test_shutdown(cleanup_agent_runtime):
    """Test runtime shutdown behavior"""
    runtime = AgentRuntime()
    initial_thread = runtime._thread
    assert initial_thread.is_alive()
    
    runtime.shutdown()
    initial_thread.join(timeout=1.0)
    assert not initial_thread.is_alive()

@pytest.mark.asyncio
async def test_multiple_coroutines(cleanup_agent_runtime):
    """Test execution of multiple coroutines"""
    runtime = AgentRuntime()
    futures = [
        runtime.execute_coroutine(dummy_coroutine())
        for _ in range(3)
    ]
    results = [future.result(timeout=1.0) for future in futures]
    assert all(result == "test_result" for result in results)

def test_thread_safety(cleanup_agent_runtime):
    """Test thread safety of runtime operations"""
    runtime = AgentRuntime()
    results = []
    
    def worker():
        future = runtime.execute_coroutine(dummy_coroutine())
        results.append(future.result(timeout=1.0))
        
    threads = [threading.Thread(target=worker) for _ in range(5)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
        
    assert len(results) == 5
    assert all(result == "test_result" for result in results)

def test_ensure_runtime_idempotency(cleanup_agent_runtime):
    """Test that _ensure_runtime is idempotent"""
    runtime = AgentRuntime()
    initial_thread = runtime._thread
    initial_loop = runtime._loop
    
    runtime._ensure_runtime()
    assert runtime._thread is initial_thread
    assert runtime._loop is initial_loop

@pytest.mark.parametrize("shutdown_timeout", [0.1, 0.5, 1.0])
def test_shutdown_with_different_timeouts(cleanup_agent_runtime, shutdown_timeout):
    """Test shutdown behavior with different timeout values"""
    runtime = AgentRuntime()
    runtime.shutdown()
    start_time = time.time()
    runtime._thread.join(timeout=shutdown_timeout)
    elapsed_time = time.time() - start_time
    assert elapsed_time < shutdown_timeout + 0.1  # Allow small overhead
