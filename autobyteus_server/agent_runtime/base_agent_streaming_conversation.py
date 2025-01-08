
import asyncio
import logging
from abc import ABC, abstractmethod
from queue import Queue, Empty
from typing import Optional
from autobyteus.events.event_emitter import EventEmitter
from autobyteus.conversation.user_message import UserMessage
from autobyteus.llm.base_llm import BaseLLM

from autobyteus_server.agent_runtime.exceptions import StreamClosedError
from autobyteus_server.agent_runtime.agent_response import AgentResponseData


logger = logging.getLogger(__name__)

class BaseAgentStreamingConversation(EventEmitter, ABC):
    """
    A base class for streaming conversations using an agent.
    Provides generic mechanisms for response handling and iteration.
    """
    def __init__(self, llm: BaseLLM):
        super().__init__()
        self.llm = llm
        self.is_active: bool = True
        self._response_queue: Queue = Queue()
        self._agent = None

    def put_response(self, response: AgentResponseData) -> None:
        """Puts a response into the queue for streaming."""
        if self.is_active:
            self._response_queue.put(response)

    def get_response(self) -> Optional[AgentResponseData]:
        """Gets the next response from the queue."""
        try:
            return self._response_queue.get(timeout=1)
        except Empty:
            return None

    async def start(self) -> None:
        """Starts the conversation if it's active."""
        if not self.is_active:
            raise StreamClosedError("Cannot start inactive conversation")

        conversation_id = getattr(self, 'conversation_id', 'unknown')
        logger.info(f"Starting conversation {conversation_id}")
        if self._agent:
            self._agent.start()

    async def stop(self) -> None:
        """Stops the conversation if it's active."""
        if not self.is_active:
            return

        conversation_id = getattr(self, 'conversation_id', 'unknown')
        logger.info(f"Stopping conversation {conversation_id}")
        if self._agent:
            self._agent.stop()
        self.close()

    def close(self) -> None:
        """Closes the conversation and cleans up resources."""
        if not self.is_active:
            return

        conversation_id = getattr(self, 'conversation_id', 'unknown')
        logger.info(f"Closing conversation {conversation_id}")
        self.is_active = False
        self._response_queue.put(None)

    @abstractmethod
    async def send_message(self, message: UserMessage) -> None:
        """
        Abstract method for sending a message in the conversation.
        Must be implemented by child classes.
        
        Args:
            message (UserMessage): The message to be sent
            
        Raises:
            StreamClosedError: If the conversation is not active
        """
        pass

    async def __aiter__(self):
        """Makes the conversation iterable with async for."""
        if not self.is_active:
            raise StreamClosedError("Cannot iterate over a closed stream")
        while self.is_active:
            try:
                chunk = await asyncio.get_event_loop().run_in_executor(
                    None, self.get_response
                )
                if chunk is None:
                    continue
                yield chunk
            except Exception as e:
                raise StreamClosedError(f"Stream operation failed: {str(e)}") from e
