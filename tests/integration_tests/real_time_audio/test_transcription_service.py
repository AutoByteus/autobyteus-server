import pytest
import threading
import queue
import pyaudio
import wave
import io
from autobyteus_server.real_time_audio.service import TranscriptionService
import time
import os

class Producer(threading.Thread):
    def __init__(self, audio_queue, chunk_duration, total_duration):
        super().__init__()
        self.audio_queue = audio_queue
        self.chunk_duration = chunk_duration
        self.total_duration = total_duration
        self.exception = None

    def run(self):
        try:
            CHUNK = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 16000

            p = pyaudio.PyAudio()
            stream = p.open(format=FORMAT,
                          channels=CHANNELS,
                          rate=RATE,
                          input=True,
                          frames_per_buffer=CHUNK)
            print(f"Audio stream opened for recording.")

            try:
                for _ in range(self.total_duration // self.chunk_duration):
                    frames = []
                    num_chunks = int(RATE / CHUNK * self.chunk_duration)
                    for _ in range(num_chunks):
                        data = stream.read(CHUNK)
                        frames.append(data)
                    
                    buffer = io.BytesIO()
                    with wave.open(buffer, 'wb') as wf:
                        wf.setnchannels(CHANNELS)
                        wf.setsampwidth(p.get_sample_size(FORMAT))
                        wf.setframerate(RATE)
                        wf.writeframes(b''.join(frames))
                    
                    audio_bytes = buffer.getvalue()
                    self.audio_queue.put(audio_bytes)
                    print("Audio chunk added to queue.")
            finally:
                stream.stop_stream()
                stream.close()
                p.terminate()
                print("Audio stream closed.")
                self.audio_queue.put(None)  # Signal end of production
        except Exception as e:
            self.exception = e
            self.audio_queue.put(None)  # Ensure consumer exits

class Consumer(threading.Thread):
    def __init__(self, audio_queue, transcription_service):
        super().__init__()
        self.audio_queue = audio_queue
        self.transcription_service = transcription_service
        self.transcriptions = []
        self.exception = None

    def run(self):
        try:
            while True:
                audio_chunk = self.audio_queue.get()
                if audio_chunk is None:
                    break
                
                try:
                    self.transcription_service.sampling_rate = 16000
                    transcription = self.transcription_service.transcribe(audio_chunk)
                    
                    print(f"Transcription: {transcription}")
                    self.transcriptions.append(transcription)
                except Exception as e:
                    print(f"Transcription failed: {e}")
                finally:
                    self.audio_queue.task_done()
        except Exception as e:
            self.exception = e

@pytest.fixture
def transcription_service():
    return TranscriptionService()

@pytest.mark.asyncio
async def test_real_time_transcription(transcription_service):
    total_duration = 30  # Total recording duration in seconds
    chunk_duration = 10  # Duration of each audio chunk in seconds
    audio_queue = queue.Queue(maxsize=3)  # Limit queue size to prevent memory issues

    # Create and start the threads
    producer = Producer(audio_queue, chunk_duration, total_duration)
    consumer = Consumer(audio_queue, transcription_service)

    producer.start()
    consumer.start()

    # Wait for both threads to complete
    producer.join()
    consumer.join()

    # Check for exceptions in threads
    if producer.exception:
        raise producer.exception
    if consumer.exception:
        raise consumer.exception

    # Verify results
    assert len(consumer.transcriptions) == total_duration // chunk_duration
    for transcription in consumer.transcriptions:
        assert isinstance(transcription, str)
        assert transcription.strip() != ""  # Ensure transcription is not empty

@pytest.mark.asyncio
async def test_file_transcription(transcription_service):
    """
    Test transcription of an audio file from a specified path.
    
    Args:
        transcription_service: The TranscriptionService instance
    """
    audio_file_path = "/home/ryan-ai/miniHDD/Learning/chatgpt/autobyteus_org_workspace/autobyteus-server/audio_chunks/chunk_3.wav"
    
    # Verify file exists
    assert os.path.exists(audio_file_path), f"Audio file not found at: {audio_file_path}"
    
    try:
        # Read the audio file
        with open(audio_file_path, 'rb') as audio_file:
            audio_data = audio_file.read()
        
        # Perform transcription
        transcription_service.sampling_rate = 16000
        transcription = transcription_service.transcribe(audio_data)
        
        # Verify transcription
        assert isinstance(transcription, str), "Transcription should be a string"
        assert transcription.strip() != "", "Transcription should not be empty"
        
        print(f"Successfully transcribed file. Transcription: {transcription}")
        
    except Exception as e:
        pytest.fail(f"Transcription failed with error: {str(e)}")