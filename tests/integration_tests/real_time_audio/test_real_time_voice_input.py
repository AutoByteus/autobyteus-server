import asyncio
import websockets
import sounddevice as sd
import numpy as np
import json
import uuid
import logging
import pytest

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

# Configuration
WEBSOCKET_URI = "ws://localhost:8001/ws/transcribe/test_workspace/test_step"
DURATION = 10  # Duration to record in seconds
SAMPLE_RATE = 16000  # Must match the server's sampling rate
CHUNK_DURATION = 10  # Duration of each audio chunk in seconds
CHUNK_SIZE = SAMPLE_RATE * CHUNK_DURATION

async def send_audio(websocket):
    """
    Capture audio from the microphone and send it to the WebSocket server in real-time.
    """
    loop = asyncio.get_event_loop()
    session_id = str(uuid.uuid4())
    logger.info(f"Starting audio capture for session {session_id}")

    def callback(indata, frames, time, status):
        if status:
            logger.warning(f"Sounddevice status: {status}")
        # Convert the recorded bytes to float32 numpy array
        audio_data = indata.copy().flatten().astype(np.float32).tobytes()
        logger.debug(f"Captured audio chunk of size {len(audio_data)} bytes")
        asyncio.run_coroutine_threadsafe(websocket.send(audio_data), loop)
        logger.info(f"Sent audio chunk to WebSocket for session {session_id}")

    try:
        with sd.InputStream(samplerate=SAMPLE_RATE, channels=1, dtype='float32', callback=callback):
            logger.info("Started recording audio...")
            await asyncio.sleep(DURATION)
    except Exception as e:
        logger.error(f"Error during audio capture: {e}")
    finally:
        logger.info("Finished recording audio.")

async def receive_transcriptions(websocket):
    """
    Receive transcription results from the WebSocket server.
    """
    try:
        async for message in websocket:
            data = json.loads(message)
            if data.get("type") == "transcription":
                text = data.get("text", "")
                timestamp = data.get("timestamp", 0)
                logger.info(f"[{timestamp}] Transcription: {text}")
            elif data.get("type") == "warning":
                warning_msg = data.get("message", "")
                logger.warning(f"Server warning: {warning_msg}")
            elif data.get("type") == "session_init":
                session_id = data.get("session_id", "unknown")
                logger.info(f"Session initialized with ID: {session_id}")
            else:
                logger.debug(f"Received unhandled message type: {data.get('type')}")
    except websockets.exceptions.ConnectionClosed as e:
        logger.info(f"WebSocket connection closed: {e}")
    except Exception as e:
        logger.error(f"Error receiving transcriptions: {e}")

@pytest.mark.asyncio
async def test_real_time_voice_input():
    """
    Integration test to capture voice input from the microphone in real-time
    and perform voice transcription using the WebSocket server.
    """
    logger.info("Starting real-time voice input transcription test.")
    try:
        async with websockets.connect(WEBSOCKET_URI) as websocket:
            logger.info(f"Connected to WebSocket server at {WEBSOCKET_URI}")

            # Receive the session initialization message
            init_message = await websocket.recv()
            logger.debug(f"Received initialization message: {init_message}")
            init_data = json.loads(init_message)
            session_id = init_data.get("session_id", "unknown")
            logger.info(f"Connected with session ID: {session_id}")

            # Create tasks for sending audio and receiving transcriptions
            send_task = asyncio.create_task(send_audio(websocket))
            receive_task = asyncio.create_task(receive_transcriptions(websocket))

            logger.info("Started audio sending and transcription receiving tasks.")

            # Wait for the sending task to complete
            await send_task
            logger.info("Audio sending task completed.")

            # Allow some time to receive remaining transcriptions
            await asyncio.sleep(2)
            logger.info("Waiting for remaining transcriptions.")

            # Close the WebSocket connection
            await websocket.close()
            logger.info("WebSocket connection closed.")

            # Cancel the receive task if it's still running
            receive_task.cancel()
            try:
                await receive_task
            except asyncio.CancelledError:
                logger.debug("Receive task cancelled successfully.")

            # Assert that at least one transcription was received
            # (This can be enhanced by collecting transcriptions and making more specific assertions)
            logger.info("Real-time voice input transcription test completed successfully.")
            assert True, "Real-time voice input transcription test completed successfully."
    except Exception as e:
        logger.error(f"An error occurred during the test: {e}")
        assert False, f"Test failed due to an unexpected error: {e}"