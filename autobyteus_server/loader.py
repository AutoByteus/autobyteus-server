"""
Loader module to help PyInstaller detect and package the FastAPI app correctly.
This module serves as a build-time helper to ensure all dependencies are properly detected
and bundled, particularly focusing on dynamically loaded components and plugin dependencies.
"""
# Core app reference
from autobyteus_server.app import app as _app

# Tokenizer and LLM dependencies
import mistral_common
from mistral_common.tokens.tokenizers.mistral import MistralTokenizer
from mistral_common.protocol.instruct.messages import UserMessage, AssistantMessage, SystemMessage
from mistral_common.protocol.instruct.request import ChatCompletionRequest
import anthropic
import tiktoken

# RPA and UI dependencies
import brui_core
from brui_core import ui_integrator
from autobyteus_rpa_llm.llm.factory.rpa_llm_factory import RPALLMFactory

# Tools
from autobyteus.tools.image_downloader import ImageDownloader
from autobyteus.tools.pdf_downloader import PDFDownloader
from autobyteus.tools.browser.standalone.google_search_ui import GoogleSearch

def get_app():
    """
    Helper function for PyInstaller to detect dependencies.
    Returns the FastAPI application instance without initializing it.
    """
    return _app
