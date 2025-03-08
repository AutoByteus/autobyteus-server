import logging
import time
from datetime import datetime
import platform
import os
from autobyteus.utils.singleton import SingletonMeta
from autobyteus_server.services.real_time_audio import is_transcription_enabled

logger = logging.getLogger(__name__)

class TranscriptionService(metaclass=SingletonMeta):
    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        self._initialized = False
        self.is_enabled = False
        
        # Check if transcription is enabled via environment variable
        if not is_transcription_enabled():
            logger.info("Real-time transcription is disabled via environment variables")
            return
            
        logger.info("Real-time transcription is enabled. Attempting to initialize...")
        
        # Conditionally import heavy dependencies only when the feature is enabled
        try:
            import torch
            import webrtcvad
            from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
            # Store module references for later use
            self.torch = torch
            self.webrtcvad = webrtcvad
            self.transformers_modules = {
                'AutoModelForSpeechSeq2Seq': AutoModelForSpeechSeq2Seq,
                'AutoProcessor': AutoProcessor,
                'pipeline': pipeline
            }
        except ImportError as e:
            logger.warning(f"Required dependencies not installed: {e}. Real-time transcription will be disabled.")
            logger.info("To enable real-time transcription, install packages: torch, transformers, webrtcvad")
            return
        
        # Initialize device and dtype
        try:
            self.device, self.torch_dtype = self._setup_device_and_dtype()
            if self.device is None or self.torch_dtype is None:
                logger.warning("No GPU detected. TranscriptionService will be disabled.")
                return
            self.is_enabled = True
        except Exception as e:
            logger.error(f"Service could not be initialized: {e}")
            return
        
        if not self.is_enabled:
            return

        model_id = "openai/whisper-large-v3-turbo"  # Using the large turbo model

        try:
            # Access modules from stored references
            self.model = self.transformers_modules['AutoModelForSpeechSeq2Seq'].from_pretrained(
                model_id,
                torch_dtype=self.torch_dtype,
                low_cpu_mem_usage=True,
                use_safetensors=True,
            )
            self.model.to(self.device)
            self.model.eval()  # Set model to evaluation mode
            
            self.processor = self.transformers_modules['AutoProcessor'].from_pretrained(model_id)
            
            # Configure pipeline device
            device_arg = self._get_pipeline_device()
            
            self.pipe = self.transformers_modules['pipeline'](
                "automatic-speech-recognition",
                model=self.model,
                tokenizer=self.processor.tokenizer,
                feature_extractor=self.processor.feature_extractor,
                torch_dtype=self.torch_dtype,
                device=device_arg,
            )
            self.sampling_rate = 16000
            self._initialized = True
            logger.info(f"TranscriptionService initialized successfully using device: {self.device}, dtype: {self.torch_dtype}")
        except Exception as e:
            logger.error(f"Failed to initialize TranscriptionService: {e}")
            self.is_enabled = False
            raise

        # Initialize VAD (aggressiveness mode 2 is a middle ground)
        self.vad = self.webrtcvad.Vad(2)

    def _setup_device_and_dtype(self):
        """
        Determine the appropriate device and dtype based on system capabilities.
        Returns tuple of (device, dtype) or (None, None) if no supported GPU is available.
        This method only supports CUDA or MPS on Apple Silicon (arm64).
        """
        # Check for CUDA first
        if self.torch.cuda.is_available():
            logger.info("CUDA is available - using GPU")
            return "cuda:0", self.torch.float16
        
        # Check for MPS on Apple Silicon (M1/M2) only
        elif (
            hasattr(self.torch.backends, "mps")
            and self.torch.backends.mps.is_available()
            and platform.system() == "Darwin"
            and platform.machine() == "arm64"
        ):
            logger.info("MPS is available and running on Apple Silicon - using MPS")
            return "mps", self.torch.float32  # MPS currently works best with float32
        
        # Return None if no supported GPU is available
        logger.warning("No supported GPU (CUDA or supported MPS) detected. TranscriptionService will be disabled.")
        return None, None

    def _get_pipeline_device(self):
        """
        Convert device string to appropriate pipeline device argument.
        """
        if self.device == "cuda:0":
            return 0
        elif self.device == "mps":
            return "mps"
        return -1

    def _contains_voice(self, audio_data: bytes) -> bool:
        """
        Detect if the audio data contains voice by analyzing the raw PCM using WebRTC VAD.
        Returns True if speech is detected, False otherwise.
        """
        if not self.is_enabled:
            return False
            
        # WebRTC VAD requires 16-bit, 16000Hz, mono PCM frames of 10, 20, or 30 ms.
        # We'll break the audio_data into 30ms frames and check for voice.
        frame_duration_ms = 30
        bytes_per_sample = 2  # 16-bit audio
        frame_size = int(self.sampling_rate * (frame_duration_ms / 1000.0) * bytes_per_sample)

        # Iterate over frames; if any frame is detected as speech, return True
        idx = 0
        while idx + frame_size <= len(audio_data):
            frame = audio_data[idx:idx + frame_size]
            if self.vad.is_speech(frame, self.sampling_rate):
                return True
            idx += frame_size

        return False

    def transcribe(self, audio_data: bytes) -> str:
        """
        Transcribe audio bytes to text using the initialized pipeline.
        Returns empty string if service is disabled or if no voice is detected.
        
        Parameters:
            audio_data (bytes): The audio data to transcribe.
        
        Returns:
            str: The transcribed text from the audio data, or empty string if service is disabled.
        """
        if not self.is_enabled:
            logger.warning("Transcription attempted but service is disabled (not configured or no GPU available)")
            return ""
            
        if not self._initialized:
            logger.error("Attempted transcription with uninitialized service")
            return ""

        # Check for voice activity. If no speech detected, skip transcription.
        if not self._contains_voice(audio_data):
            logger.info("Skipping transcription: no voice detected in chunk.")
            return ""
        
        start_time = time.perf_counter()
        start_datetime = datetime.now().isoformat()
        logger.info(f"Starting transcription at: {start_datetime}")
        
        try:
            # Time the pipeline execution specifically
            pipeline_start = time.perf_counter()
            transcription = self.pipe(audio_data)
            pipeline_duration = time.perf_counter() - pipeline_start
            
            transcription_text = transcription.get("text", "").strip()
            
            # Calculate total duration
            total_duration = time.perf_counter() - start_time
            
            # Log timing information and transcribed text
            logger.info(
                f"Transcription completed - "
                f"Start time: {start_datetime}, "
                f"Pipeline execution: {pipeline_duration:.3f}s, "
                f"Total time: {total_duration:.3f}s, "
                f"Result length: {len(transcription_text)} chars, "
                f"Transcribed text: {transcription_text}"
            )
            
            return transcription_text
        except Exception as e:
            error_duration = time.perf_counter() - start_time
            logger.error(
                f"Error in transcription after {error_duration:.3f}s: {e}"
            )
            raise
        finally:
            # Clear GPU cache if using CUDA
            if self.device == "cuda:0" and hasattr(self, 'torch') and hasattr(self.torch, 'cuda'):
                self.torch.cuda.empty_cache()
