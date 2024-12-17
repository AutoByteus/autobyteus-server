from fastapi import APIRouter, WebSocket
import logging
from .conversation_session import ConversationSession

logger = logging.getLogger(__name__)
conversation_router = APIRouter()

@conversation_router.websocket("/ws/conversation/{workspace_id}/{step_id}")
async def conversation_endpoint(websocket: WebSocket, workspace_id: str, step_id: str):
    """
    WebSocket endpoint for handling conversations.
    """
    session = ConversationSession(
        websocket=websocket,
        workspace_id=workspace_id,
        step_id=step_id
    )
    
    try:
        await session.handle_session()
    finally:
        await session.close()