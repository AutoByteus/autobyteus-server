import pytest
import asyncio
from fastapi import WebSocket
from unittest.mock import AsyncMock, MagicMock, patch
from autobyteus_server.services.real_time_audio.handler import TranscriptionHandler, TranscriptionRequest
from autobyteus_server.services.real_time_audio.service import TranscriptionService

@pytest.fixture
def mock_websocket():
    websocket = AsyncMock(spec=WebSocket)
    websocket.receive_bytes = AsyncMock()
    websocket.send_json = AsyncMock()
    websocket.accept = AsyncMock()
    websocket.close = AsyncMock()
    return websocket

@pytest.fixture
def transcription_handler():
    handler = TranscriptionHandler()
    yield handler
    asyncio.run(handler.shutdown())

@pytest.fixture
def mock_transcription_service(monkeypatch):
    mock_service = MagicMock(spec=TranscriptionService)
    monkeypatch.setattr("autobyteus_server.real_time_audio.handler.TranscriptionService", lambda: mock_service)
    return mock_service

@pytest.fixture
def mock_transcription_worker(monkeypatch):
    mock_worker = MagicMock()
    mock_worker.request_queue = asyncio.Queue()
    mock_worker.result_queues = {}
    mock_worker.start = AsyncMock()
    mock_worker.stop = AsyncMock()
    mock_worker.join = AsyncMock()
    monkeypatch.setattr("autobyteus_server.real_time_audio.handler.TranscriptionWorker", lambda x: mock_worker)
    return mock_worker

@pytest.mark.asyncio
async def test_connect(transcription_handler, mock_websocket):
    workspace_id = "test_workspace"
    step_id = "test_step"
    
    session_id = await transcription_handler.connect(mock_websocket, workspace_id, step_id)
    
    mock_websocket.accept.assert_called_once()
    mock_websocket.send_json.assert_called_once_with({
        "type": "session_init",
        "session_id": session_id
    })
    assert session_id in transcription_handler.active_connections
    assert session_id in transcription_handler.output_queues
    assert session_id in transcription_handler.worker.result_queues
    assert isinstance(transcription_handler.audio_buffers[session_id], bytearray)

@pytest.mark.asyncio
async def test_disconnect(transcription_handler, mock_websocket):
    workspace_id = "test_workspace"
    step_id = "test_step"
    
    session_id = await transcription_handler.connect(mock_websocket, workspace_id, step_id)
    await transcription_handler.disconnect(session_id)
    
    mock_websocket.close.assert_called_once()
    assert session_id not in transcription_handler.active_connections
    assert session_id not in transcription_handler.output_queues
    assert session_id not in transcription_handler.worker.result_queues
    assert session_id not in transcription_handler.audio_buffers

@pytest.mark.asyncio
async def test_receive_audio(transcription_handler, mock_websocket, mock_transcription_worker):
    workspace_id = "test_workspace"
    step_id = "test_step"
    session_id = await transcription_handler.connect(mock_websocket, workspace_id, step_id)
    
    audio_data = b'test_audio_data'
    mock_websocket.receive_bytes.side_effect = [audio_data, Exception("WebSocket disconnected")]
    
    # Allow the receive_audio coroutine to run
    receive_task = asyncio.create_task(
        transcription_handler._receive_audio(mock_websocket, session_id, workspace_id, step_id)
    )
    
    await asyncio.sleep(0.1)  # Let the coroutine process
    
    # Check that audio_data was added to the buffer
    assert transcription_handler.audio_buffers[session_id] == bytearray(audio_data)
    
    # Since chunk_size is 4096, the buffer is not yet full, so no transcription request should be made
    assert transcription_handler.worker.request_queue.qsize() == 0
    
    # Now send enough data to trigger transcription
    additional_data = b'a' * (transcription_handler.chunk_size - len(audio_data))
    mock_websocket.receive_bytes.side_effect = [additional_data, Exception("WebSocket disconnected")]
    
    await asyncio.sleep(0.1)  # Let the coroutine process
    
    # Now the buffer should have been cleared
    assert transcription_handler.audio_buffers[session_id] == bytearray()
    
    # And a transcription request should have been enqueued
    assert transcription_handler.worker.request_queue.qsize() == 1
    request = await transcription_handler.worker.request_queue.get()
    assert isinstance(request, TranscriptionRequest)
    assert request.session_id == session_id
    assert request.audio_data == audio_data + additional_data

@pytest.mark.asyncio
async def test_transcription_worker_response(transcription_handler, mock_websocket, mock_transcription_service, mock_transcription_worker):
    workspace_id = "test_workspace"
    step_id = "test_step"
    session_id = await transcription_handler.connect(mock_websocket, workspace_id, step_id)
    
    # Simulate a transcription result being put into the result_queue
    transcription_result = {
        "type": "transcription",
        "text": "Test transcription",
        "timestamp": 123.456
    }
    
    # Put the result into the worker's result_queue
    result_queue = transcription_handler.output_queues[session_id]
    await result_queue.put(transcription_result)
    
    # Allow the send_results coroutine to run
    send_task = asyncio.create_task(
        transcription_handler._send_results(mock_websocket, session_id)
    )
    
    await asyncio.sleep(0.1)  # Let the coroutine process
    
    mock_websocket.send_json.assert_called_with(transcription_result)
    
    send_task.cancel()  # Cleanup the task

@pytest.mark.asyncio
async def test_shutdown(transcription_handler, mock_transcription_worker):
    with patch.object(transcription_handler.worker, 'stop') as mock_stop, \
         patch.object(transcription_handler.worker, 'join') as mock_join:
        await transcription_handler.shutdown()
        mock_stop.assert_called_once()
        mock_join.assert_called_once_with(timeout=5.0)

# Additional tests can be added here as needed to cover more scenarios