"""
app.py: The main entry point for the AutoByteus server application.
"""
import sys
import os
import argparse
from pathlib import Path
from contextlib import asynccontextmanager
import logging
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from strawberry.fastapi import GraphQLRouter
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL
from autobyteus_server.config import app_config_provider
from autobyteus_server.config.app_config import AppConfigError
from autobyteus_server.startup import run_migrations

# Set up minimal logging before config is initialized
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Parse command line arguments early to set up data directory
parser = argparse.ArgumentParser(description='AutoByteus Server')
parser.add_argument('--port', type=int, default=8000, help='Port to run the server on')
parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to run the server on')
parser.add_argument('--data-dir', type=str, help='Custom directory for all application data (configs, logs, database)')

# Parse known args to get the data directory without requiring all args
known_args, _ = parser.parse_known_args()

# Get AppConfig instance (automatically created if needed)
config = app_config_provider.config

# Set custom app data directory if specified
if known_args.data_dir:
    try:
        config.set_custom_app_data_dir(known_args.data_dir)
    except (FileNotFoundError, NotADirectoryError, RuntimeError) as e:
        logger.error(f"Error setting custom app data directory: {e}")
        sys.exit(1)

# Perform full initialization
# This will configure logging and load environment variables
try:
    config.initialize()
except AppConfigError as e:
    logger.error(f"Failed to initialize AppConfig: {e}")
    sys.exit(1)
except Exception as e:
    logger.error(f"Unexpected error during initialization: {e}")
    sys.exit(1)

from autobyteus_server.api.graphql.schema import schema
from autobyteus_server.api.rest import router as rest_router
from autobyteus_server.api.websocket.real_time_audio_router import transcription_router

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
app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
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

# Include all routers
app.include_router(graphql_router, prefix="/graphql")
app.include_router(rest_router, prefix="/rest")
app.include_router(transcription_router)

def run_server(host: str, port: int):
    """Run the FastAPI server"""
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )

if __name__ == '__main__':
    # We've already parsed the arguments for --data-dir earlier,
    # now we need to parse all arguments again for the server
    args = parser.parse_args()
    run_server(args.host, args.port)
