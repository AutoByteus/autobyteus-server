from typing import Optional
from fastapi import WebSocket, WebSocketDisconnect
import logging
import asyncio
import json
import uuid
from enum import Enum
from autobyteus_server.workflow.types.base_step import BaseStep
from autobyteus_server.workflow.runtime.agent_streaming_conversation import AgentStreamingConversation
from autobyteus_server.workspaces.workspace_manager import WorkspaceManager

logger = logging.getLogger(__name__)

class SessionState(Enum):
    INITIALIZED = "initialized"
    STARTED = "started"
    CLOSED = "closed"

class MessageType(Enum):
    SESSION_INIT = "session_init"
    START_CONVERSATION = "start_conversation"
    CONTINUE_CONVERSATION = "continue_conversation"
    CLOSE_CONVERSATION = "close_conversation"
    CHUNK = "chunk"
    ERROR = "error"

class ConversationSession:
    def __init__(self, websocket: WebSocket, workspace_id: str, step_id: str):
        self.websocket = websocket
        self.workspace_id = workspace_id
        self.step_id = step_id
        self.workspace_manager = WorkspaceManager()
        self.step: Optional[BaseStep] = None
        self.session_id = str(uuid.uuid4())
        self.is_active = True
        self.internal_agent_conversation: Optional[AgentStreamingConversation] = None
        self.receiver_task = None
        self.streamer_task = None
        self.stream_event = asyncio.Event()
        self.state = SessionState.INITIALIZED
        self.llm_model: Optional[str] = None

    async def validate_session(self) -> tuple[bool, Optional[str]]:
        """
        Validates the workspace and step before starting the session.
        Returns (is_valid, error_message)
        """
        workspace = self.workspace_manager.get_workspace_by_id(self.workspace_id)
        if not workspace or not workspace.workflow:
            return False, f"Invalid workspace or workflow: {self.workspace_id}"

        step = workspace.workflow.get_step(self.step_id)
        if not isinstance(step, BaseStep):
            return False, f"Invalid step: {self.step_id}"

        self.step = step
        return True, None

    async def _send_session_init(self):
        """
        Sends initial session information to the client.
        """
        try:
            await self.websocket.send_json({
                "type": MessageType.SESSION_INIT.value,
                "session_id": self.session_id
            })
        except Exception as e:
            logger.error(f"Failed to send session initialization: {e}")
            raise

    async def handle_session(self):
        """
        Main session handler that manages the websocket lifecycle.
        """
        try:
            # Validate before accepting the connection
            is_valid, error_message = await self.validate_session()
            
            await self.websocket.accept()
            
            if not is_valid:
                await self.send_error(error_message)
                return
            
            await self._send_session_init()
            
            self.receiver_task = asyncio.create_task(self._message_receiver())
            self.streamer_task = asyncio.create_task(self._response_streamer())
            
            done, pending = await asyncio.wait(
                [self.receiver_task, self.streamer_task],
                return_when=asyncio.FIRST_COMPLETED
            )

            for task in pending:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
                
        except WebSocketDisconnect:
            logger.info(f"Client disconnected for session {self.session_id}")
        except Exception as e:
            logger.error(f"Error in conversation session: {e}")
            await self.send_error(f"Session error: {str(e)}")
        finally:
            await self.close()

    async def _message_receiver(self):
        """
        Task responsible for receiving and processing incoming messages.
        """
        try:
            while self.is_active:
                message = await self.websocket.receive_text()
                await self._process_message(message)
        except WebSocketDisconnect:
            logger.info(f"Receiver: Client disconnected for session {self.session_id}")
            raise
        except Exception as e:
            logger.error(f"Error in message receiver: {e}")
            await self.send_error(f"Receiver error: {str(e)}")
            raise

    async def _process_message(self, message: str):
        """
        Processes incoming messages according to the protocol.
        """
        try:
            data = json.loads(message)
            message_type = data.get("type")

            if message_type not in [e.value for e in MessageType]:
                await self.send_error(f"Invalid message type: {message_type}")
                return

            if message_type == MessageType.START_CONVERSATION.value:
                if self.state != SessionState.INITIALIZED:
                    await self.send_error("Cannot start conversation - invalid state")
                    return
                
                self.llm_model = data.get("llm_model")
                if not self.llm_model:
                    await self.send_error("llm_model is required for start_conversation")
                    return

                await self.start_conversation(
                    requirement=data.get("requirement", ""),
                    context_file_paths=data.get("context_file_paths", []),
                    llm_model=self.llm_model
                )
                self.state = SessionState.STARTED

            elif message_type == MessageType.CONTINUE_CONVERSATION.value:
                if self.state != SessionState.STARTED:
                    await self.send_error("Cannot continue conversation - invalid state")
                    return

                await self.continue_conversation(
                    requirement=data.get("requirement", ""),
                    context_file_paths=data.get("context_file_paths", [])
                )

            elif message_type == MessageType.CLOSE_CONVERSATION.value:
                if self.state != SessionState.STARTED:
                    await self.send_error("Cannot close conversation - invalid state")
                    return

                self.state = SessionState.CLOSED
                await self.close()

            else:
                await self.send_error(f"Unhandled message type: {message_type}")
                
        except json.JSONDecodeError:
            await self.send_error("Invalid message format")
        except Exception as e:
            await self.send_error(f"Error processing message: {str(e)}")
            raise

    async def _response_streamer(self):
        """
        Task responsible for streaming responses back to the client.
        Continues running until the session is explicitly closed or an error occurs.
        """
        try:
            while self.is_active:
                await self.stream_event.wait()
                
                if self.internal_agent_conversation:
                    try:
                        async for response_data in self.internal_agent_conversation:
                            if not self.is_active:
                                break
                            
                            if response_data:
                                message_chunk = response_data.get("messageChunk", "")
                                is_complete = response_data.get("isComplete", False)
                                
                                await self.websocket.send_json({
                                    "type": MessageType.CHUNK.value,
                                    "messageChunk": message_chunk,
                                    "isComplete": is_complete,
                                    "session_id": self.session_id
                                })

                                if is_complete:
                                    self.stream_event.clear()
                                    
                    except Exception as e:
                        logger.error(f"Error processing response stream: {e}")
                        await self.send_error(f"Stream processing error: {str(e)}")
                        break
                
                self.stream_event.clear()
                
        except asyncio.CancelledError:
            logger.info(f"Streamer: Streaming cancelled for session {self.session_id}")
            raise
        except Exception as e:
            logger.error(f"Error in response streamer: {e}")
            await self.send_error(f"Streamer error: {str(e)}")
            raise

    async def start_conversation(self, requirement: str, context_file_paths: list, llm_model: str):
        """
        Starts a new conversation and triggers streaming responses.
        """
        try:
            self.internal_agent_conversation = await self.step.start_conversation(
                requirement=requirement,
                context_file_paths=context_file_paths,
                llm_model=llm_model
            )
            
            if not self.internal_agent_conversation:
                raise ValueError("Failed to create agent conversation")
            
            self.stream_event.set()
            
        except Exception as e:
            logger.error(f"Error starting conversation: {e}")
            await self.send_error(f"Failed to start conversation: {str(e)}")
            raise

    async def continue_conversation(self, requirement: str, context_file_paths: list):
        """
        Continues an existing conversation and triggers streaming responses.
        """
        try:
            if not self.internal_agent_conversation:
                raise ValueError("No active conversation found")

            await self.step.continue_conversation(
                requirement=requirement,
                context_file_paths=context_file_paths,
                conversation_id=self.internal_agent_conversation.conversation_id
            )
            
            self.stream_event.set()
            
        except Exception as e:
            logger.error(f"Error continuing conversation: {e}")
            await self.send_error(f"Failed to continue conversation: {str(e)}")
            raise

    async def send_error(self, error_message: str):
        """
        Sends an error message to the client.
        """
        try:
            await self.websocket.send_json({
                "type": MessageType.ERROR.value,
                "error": error_message,
                "session_id": self.session_id
            })
        except Exception as e:
            logger.error(f"Failed to send error message: {e}")

    async def close(self):
        """
        Closes the session and cleans up resources.
        """
        self.is_active = False
        self.stream_event.set()  # Ensure streamer task can exit
        
        if self.receiver_task:
            self.receiver_task.cancel()
        if self.streamer_task:
            self.streamer_task.cancel()
            
        if self.internal_agent_conversation:
            conversation_id = self.internal_agent_conversation.conversation_id
            self.internal_agent_conversation = None
            await self.step.close_conversation(conversation_id)
            
        try:
            await self.websocket.close()
        except Exception as e:
            logger.error(f"Error closing websocket: {e}")