import asyncio
import logging
from queue import Queue, Empty
from typing import Optional, List
from autobyteus.agent.async_agent import AsyncAgent
from autobyteus.conversation.user_message import UserMessage
from autobyteus.llm.base_llm import BaseLLM
from autobyteus.events.event_types import EventType
from autobyteus_server.workflow.runtime.exceptions import StreamClosedError
from autobyteus_server.workflow.types.step_response import StepResponseData

logger = logging.getLogger(__name__)

class StreamingConversation:
    """
    A streaming conversation that manages its own agent and message flow.
    Handles the lifecycle of a single conversation and its associated agent.
    """
    def __init__(self, 
                 workspace_id: str, 
                 step_id: str, 
                 conversation_id: str,
                 step_name: str,
                 llm: BaseLLM,
                 initial_message: UserMessage,
                 tools: List = None):
        self.workspace_id = workspace_id
        self.step_id = step_id
        self.conversation_id = conversation_id
        self.is_active = True
        self._response_queue = Queue()
        
        # Create and initialize agent
        self._agent = AsyncAgent(
            role=step_name,
            llm=llm,
            tools=tools or [],
            use_xml_parser=True,
            initial_user_message=initial_message
        )
        self._agent.subscribe(EventType.ASSISTANT_RESPONSE, self._on_assistant_response, self._agent.agent_id)

    def _on_assistant_response(self, *args, **kwargs):
        """Handles responses from the agent."""
        response = kwargs.get('response')
        is_complete = kwargs.get('is_complete', False)
        
        logger.debug(f"Received assistant response: {response}, is_complete: {is_complete}")
        
        if response:
            response_data = StepResponseData(
                message=response,
                is_complete=is_complete
            )
            self.put_response(response_data)

    def put_response(self, response: StepResponseData) -> None:
        """Puts a response into the queue for streaming."""
        if self.is_active:
            self._response_queue.put(response)

    def get_response(self) -> Optional[StepResponseData]:
        """Gets the next response from the queue."""
        try:
            return self._response_queue.get(timeout=0.1)
        except Empty:
            return None

    async def send_message(self, message: str) -> None:
        """Sends a message to the conversation's agent."""
        if not self.is_active:
            raise StreamClosedError("Cannot send message to inactive conversation")
            
        user_message = UserMessage(content=message)
        await self._agent.receive_user_message(user_message)

    async def start(self) -> None:
        """Starts the conversation's agent."""
        if not self.is_active:
            raise StreamClosedError("Cannot start inactive conversation")
            
        logger.info(f"Starting conversation {self.conversation_id}")
        self._agent.start()

    async def stop(self) -> None:
        """Stops the conversation's agent."""
        if not self.is_active:
            return
            
        logger.info(f"Stopping conversation {self.conversation_id}")
        self._agent.stop()
        self.close()

    def close(self) -> None:
        """Closes the streaming conversation."""
        if not self.is_active:
            return
            
        logger.info(f"Closing conversation {self.conversation_id}")
        self.is_active = False
        self._response_queue.put(None)  # Signal end of stream

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
                
                if chunk.is_complete:
                    break
                    
            except Exception as e:
                raise StreamClosedError(f"Stream operation failed: {str(e)}") from e