"""
app.py: The main entry point for the AutoByteus server application.
"""
import sys
import os
from pathlib import Path
from typing import Optional
from contextlib import asynccontextmanager
import asyncio
import platform

# Load environment variables from .env file
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from autobyteus_server.api.graphql.schema import schema
from strawberry.fastapi import GraphQLRouter
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL
from autobyteus_server.api.rest import router as rest_router
from autobyteus_server.config.logging_config import configure_logger
from autobyteus_server.api.websocket.real_time_audio_router import transcription_router
from autobyteus_server.startup import run_migrations
import logging

# Configure asyncio policy for subprocess support
if platform.system() != "Windows":
    policy = asyncio.DefaultEventLoopPolicy()
    asyncio.set_event_loop_policy(policy)
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    watcher = asyncio.SafeChildWatcher()
    watcher.attach_loop(loop)
    policy.set_child_watcher(watcher)

def get_application_root():
    """Get the application root directory, works in both development and packaged mode"""
    if getattr(sys, 'frozen', False):
        return Path(sys._MEIPASS)
    return Path(__file__).parent.parent

def load_environment():
    """Load environment variables with fallback for packaged mode"""
    env_path = get_application_root() / '.env'
    load_dotenv(dotenv_path=env_path)
    
    # Set default environment variables if not present
    os.environ.setdefault('LOG_LEVEL', 'INFO')

# Configure environment
load_environment()

# Configure logging
configure_logger()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for handling startup and shutdown events.
    """
    try:
        logger.info("Starting up AutoByteus server...")
        # Run database migrations
        run_migrations()
        logger.info("Startup complete")
        yield
    except Exception as e:
        logger.error(f"Error during startup: {str(e)}")
        raise
    finally:
        logger.info("Shutting down AutoByteus server...")
        logger.info("Shutdown complete")

# Create FastAPI app with lifespan
app = FastAPI(lifespan=lifespan)

# Allow all origins for CORS
origins = "*"

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up GraphQL router
graphql_router = GraphQLRouter(
    schema,
    subscription_protocols=[
        GRAPHQL_WS_PROTOCOL,
        GRAPHQL_TRANSPORT_WS_PROTOCOL,
    ]
)
app.include_router(graphql_router, prefix="/graphql")

# Include REST routers
app.include_router(rest_router, prefix="/rest")
app.include_router(transcription_router)