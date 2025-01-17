import asyncio
import queue
import threading
import time
import uuid
import logging
from datetime import datetime
from typing import Dict, NamedTuple

from fastapi import WebSocket

from autobyteus_server.services.real_time_audio.service import TranscriptionService

logger = logging.getLogger(__name__)

# Audio parameters - must match frontend MediaRecorder settings
CHANNELS = 1
SAMPLE_WIDTH = 2  # 16-bit audio
SAMPLE_RATE = 16000

class TranscriptionRequest(NamedTuple):
    """Structure for holding transcription request data"""
    session_id: str
    audio_data: bytes
    timestamp: float


class TranscriptionWorker(threading.Thread):
    """Single worker thread that processes all transcription requests sequentially"""
    def __init__(self, transcription_service: TranscriptionService, loop: asyncio.AbstractEventLoop):
        super().__init__()
        self.transcription_service = transcription_service
        self.request_queue = queue.Queue(maxsize=100)
        self.result_queues: Dict[str, asyncio.Queue] = {}
        self.running = True
        self.loop = loop

    def run(self):
        """Process transcription requests sequentially"""
        while self.running:
            try:
                try:
                    request = self.request_queue.get(timeout=0.5)
                except queue.Empty:
                    continue

                if request is None:  # Shutdown signal
                    break

                try:
                    transcription = self.transcription_service.transcribe(request.audio_data)
                    
                    if request.session_id in self.result_queues:
                        result_queue = self.result_queues[request.session_id]
                        asyncio.run_coroutine_threadsafe(
                            result_queue.put({
                                "type": "transcription",
                                "text": transcription,
                                "timestamp": request.timestamp
                            }),
                            self.loop
                        )
                except Exception as e:
                    logger.error(f"Error processing transcription: {e}")

            except Exception as e:
                logger.error(f"Error in transcription worker: {e}")

    def stop(self):
        """Signal the thread to stop"""
        self.running = False
        self.request_queue.put(None)


class TranscriptionHandler:
    def __init__(self):
        self.transcription_service = TranscriptionService()
        self.active_connections: Dict[str, WebSocket] = {}
        self.output_queues: Dict[str, asyncio.Queue] = {}
        
        try:
            self.loop = asyncio.get_event_loop()
            if self.loop.is_closed():
                self.loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self.loop)
        except RuntimeError:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)
        
        self.worker = TranscriptionWorker(self.transcription_service, self.loop)
        self.worker.start()
        
    async def connect(self, websocket: WebSocket, workspace_id: str, step_id: str) -> str:
        """Initialize WebSocket connection"""
        await websocket.accept()

        session_id = str(uuid.uuid4())
        self.active_connections[session_id] = websocket

        self.output_queues[session_id] = asyncio.Queue(maxsize=100)
        self.worker.result_queues[session_id] = self.output_queues[session_id]

        asyncio.create_task(self._receive_audio(websocket, session_id, workspace_id, step_id))
        asyncio.create_task(self._send_results(websocket, session_id))

        await websocket.send_json({
            "type": "session_init",
            "session_id": session_id
        })

        logger.info(f"Session {session_id} connected.")
        return session_id

    async def _receive_audio(self, websocket: WebSocket, session_id: str, workspace_id: str, step_id: str):
        """Receive audio chunks from websocket and process them"""
        try:
            while True:
                audio_data = await websocket.receive_bytes()
                current_timestamp = time.time()
                
                try:
                    request = TranscriptionRequest(
                        session_id=session_id,
                        audio_data=audio_data,
                        timestamp=current_timestamp
                    )
                    
                    try:
                        self.worker.request_queue.put_nowait(request)
                    except queue.Full:
                        logger.warning(f"Request queue full for {session_id}, dropping chunk.")
                        await websocket.send_json({
                            "type": "warning",
                            "message": "Audio chunk dropped - processing backlog."
                        })
                        
                except Exception as e:
                    logger.error(f"Error processing audio chunk: {e}")
                    await websocket.send_json({
                        "type": "warning",
                        "message": "Error processing audio chunk."
                    })
                        
        except Exception as e:
            logger.error(f"Error receiving audio for session {session_id}: {e}")
            await self.disconnect(session_id)

    async def _send_results(self, websocket: WebSocket, session_id: str):
        """Send transcription results back through WebSocket"""
        try:
            while True:
                result = await self.output_queues[session_id].get()
                # If the transcription result is empty, the chunk may have been silent.
                if not result.get("text"):
                    logger.debug(f"Session {session_id}: received empty transcription result (likely silent).")
                await websocket.send_json(result)
        except Exception as e:
            logger.error(f"Error sending results for session {session_id}: {e}")
            await self.disconnect(session_id)

    async def disconnect(self, session_id: str):
        """Clean up all resources for a session"""
        try:
            if session_id in self.worker.result_queues:
                del self.worker.result_queues[session_id]

            if session_id in self.output_queues:
                del self.output_queues[session_id]

            if session_id in self.active_connections:
                await self.active_connections[session_id].close()
                del self.active_connections[session_id]

        except Exception as e:
            logger.error(f"Error during disconnect cleanup for session {session_id}: {e}")
        finally:
            logger.info(f"Session {session_id} disconnected and cleaned up.")

    async def shutdown(self):
        """Shutdown the handler and worker threads"""
        try:
            self.worker.stop()
            self.worker.join(timeout=5.0)
            if self.worker.is_alive():
                logger.warning("Transcription worker thread did not stop gracefully")
        except Exception as e:
            logger.error(f"Error during worker shutdown: {e}")


transcription_handler = TranscriptionHandler()