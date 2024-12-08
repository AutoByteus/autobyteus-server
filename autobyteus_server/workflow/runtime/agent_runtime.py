import logging
import asyncio
import threading
from typing import Optional
from autobyteus.utils.singleton import SingletonMeta

logger = logging.getLogger(__name__)

class AgentRuntime(metaclass=SingletonMeta):
    """
    Provides a dedicated runtime environment with a shared event loop for agent operations.
    Manages the execution context where agents run their asynchronous operations.
    """
    def __init__(self):
        self._loop: Optional[asyncio.AbstractEventLoop] = None
        self._thread: Optional[threading.Thread] = None
        self._ready_event = threading.Event()
        self._ensure_runtime()
        if not self._ready_event.wait(timeout=5.0):  # Wait up to 5 seconds for initialization
            raise RuntimeError("Runtime initialization timeout")

    def _ensure_runtime(self):
        """Ensures the runtime environment is initialized with its own event loop."""
        if self._thread is None:
            def run_event_loop():
                self._loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._loop)
                self._ready_event.set()  # Signal that the loop is ready
                self._loop.run_forever()

            self._thread = threading.Thread(target=run_event_loop, daemon=True)
            self._thread.start()

    def execute_coroutine(self, coro):
        """Execute a coroutine in the runtime's event loop."""
        if not self._loop:
            raise RuntimeError("Runtime environment not initialized")
        return asyncio.run_coroutine_threadsafe(coro, self._loop)

    def shutdown(self):
        """Shutdown the runtime environment."""
        if self._loop:
            self._loop.call_soon_threadsafe(self._loop.stop)
        if self._thread:
            self._thread.join(timeout=1.0)
        self._ready_event.clear()