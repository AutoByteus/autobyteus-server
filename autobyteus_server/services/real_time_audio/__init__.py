import os
import logging

logger = logging.getLogger(__name__)

def is_transcription_enabled():
    """
    Check if real-time transcription is enabled via environment variables.
    
    Returns:
        bool: True if real-time transcription is enabled, False otherwise
    """
    return os.environ.get('ENABLE_REAL_TIME_TRANSCRIPTION', 'false').lower() == 'true'
