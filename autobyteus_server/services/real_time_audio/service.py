
import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from autobyteus.utils.singleton import SingletonMeta
import logging
import time
from datetime import datetime
import platform

logger = logging.getLogger(__name__)

class TranscriptionService(metaclass=SingletonMeta):
    def __init__(self):
        if hasattr(self, '_initialized') and self._initialized:
            return
        
        # Initialize device and dtype
        try:
            self.device, self.torch_dtype = self._setup_device_and_dtype()
        except EnvironmentError as e:
            logger.error(f"Service could not be initialized: {e}")
            return
        
        model_id = "openai/whisper-large-v3-turbo"  # Using the large turbo model

        try:
            self.model = AutoModelForSpeechSeq2Seq.from_pretrained(
                model_id,
                torch_dtype=self.torch_dtype,
                low_cpu_mem_usage=True,
                use_safetensors=True,
            )
            self.model.to(self.device)
            self.model.eval()  # Set model to evaluation mode
            
            self.processor = AutoProcessor.from_pretrained(model_id)
            
            # Configure pipeline device
            device_arg = self._get_pipeline_device()
            
            self.pipe = pipeline(
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
            raise

    def _setup_device_and_dtype(self):
        """
        Determine the appropriate device and dtype based on system capabilities.
        Returns tuple of (device, dtype) or raises an error if neither CUDA nor MPS is available.
        """
        # Check for CUDA first
        if torch.cuda.is_available():
            logger.info("CUDA is available - using GPU")
            return "cuda:0", torch.float16
        
        # Check for MPS (Apple Silicon) support
        elif (
            hasattr(torch.backends, "mps")
            and torch.backends.mps.is_available()
            and platform.system() == "Darwin"
        ):
            logger.info("MPS is available - using Apple Silicon GPU")
            return "mps", torch.float32  # MPS currently works best with float32
        
        # Raise an error if only CPU is available
        else:
            error_message = "No suitable GPU detected. Service requires CUDA or MPS."
            logger.error(error_message)
            raise EnvironmentError(error_message)

    def _get_pipeline_device(self):
        """
        Convert device string to appropriate pipeline device argument
        """
        if self.device == "cuda:0":
            return 0
        elif self.device == "mps":
            return "mps"
        else:
            # Should not reach here, as we prevent CPU-only initialization
            return -1

    def transcribe(self, audio_data: bytes) -> str:
        """
        Transcribe audio bytes to text using the initialized pipeline.
        
        Parameters:
            audio_data (bytes): The audio data to transcribe. Must be in a recognizable format such as WAV, MP3, or other supported byte formats.
        
        Returns:
            str: The transcribed text from the audio data.
        
        Logs:
            - Start time of the transcription process.
            - Duration of the pipeline execution.
            - Total time taken for the transcription.
            - Length of the transcribed text.
            - The transcribed text itself.
            - Errors encountered during transcription.
        
        Notes:
            - If audio data is captured from a microphone, ensure that the recording uses the same sampling rate as specified in this class (self.sampling_rate).
            - This method is intended to be called from a dedicated thread per session, so additional synchronization is not required.
        """
        if not hasattr(self, '_initialized') or not self._initialized:
            logger.error(f"Attempted transcription with uninitialized service.")
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
            if self.device == "cuda:0":
                torch.cuda.empty_cache()
