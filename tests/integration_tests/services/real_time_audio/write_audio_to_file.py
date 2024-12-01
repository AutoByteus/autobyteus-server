import wave
import io
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

# Audio parameters matching nuxt config
SAMPLE_RATE = 16000
CHANNELS = 1
SAMPLE_WIDTH = 2  # 16-bit audio

def load_audio_chunk(file_path: str) -> bytes:
    """Load an audio chunk file into memory."""
    try:
        with open(file_path, 'rb') as f:
            return f.read()
    except FileNotFoundError:
        logger.error(f"Audio file not found: {file_path}")
        raise
    except IOError as e:
        logger.error(f"Error reading audio file {file_path}: {str(e)}")
        raise

def write_audio_to_wav(audio_data: bytes, output_path: str) -> None:
    """Write audio data to a WAV file using configured parameters."""
    try:
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        
        with wave.open(output_path, 'wb') as wav_file:
            wav_file.setnchannels(CHANNELS)
            wav_file.setsampwidth(SAMPLE_WIDTH)
            wav_file.setframerate(SAMPLE_RATE)
            wav_file.writeframes(audio_data)
            
        logger.info(f"Successfully wrote audio to {output_path}")
    except IOError as e:
        logger.error(f"Error writing WAV file {output_path}: {str(e)}")
        raise

def process_audio_chunk(input_path: str, output_path: str) -> None:
    """Process audio chunk to WAV."""
    audio_data = load_audio_chunk(input_path)
    write_audio_to_wav(audio_data, output_path)

if __name__ == "__main__":
    try:
        process_audio_chunk(
            "/home/ryan-ai/miniHDD/Learning/chatgpt/autobyteus_org_workspace/autobyteus-server/audio_chunks/forth_chunk.webm",
            "/home/ryan-ai/miniHDD/Learning/chatgpt/autobyteus_org_workspace/autobyteus-server/audio_chunks/fourth_chunk.wav"
        )
    except Exception as e:
        logger.error(f"Failed to process audio chunk: {str(e)}")


