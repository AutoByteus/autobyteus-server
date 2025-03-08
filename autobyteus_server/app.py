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
from autobyteus_server.utils.app_utils import get_application_root, is_packaged_environment

def validate_packaged_environment():
    """Validate that all required files and directories exist in packaged mode"""
    app_root = get_application_root()
    required_files = [
        '.env',
        'logging_config.ini',
        'alembic.ini'
    ]
    required_dirs = [
        'logs',
        'resources',
        'alembic'
    ]
    
    missing_files = [f for f in required_files if not (app_root / f).exists()]
    missing_dirs = [d for d in required_dirs if not (app_root / d).is_dir()]
    
    if missing_files or missing_dirs:
        logger.error("Missing required files or directories:")
        if missing_files:
            logger.error(f"Files: {missing_files}")
        if missing_dirs:
            logger.error(f"Directories: {missing_dirs}")
        sys.exit(1)

def load_environment():
    """Load environment variables with fallback for packaged mode"""
    env_path = get_application_root() / '.env'
    load_dotenv(dotenv_path=env_path)
    os.environ.setdefault('LOG_LEVEL', 'INFO')

# Configure environment
load_environment()

# Configure logging
configure_logger()
logger = logging.getLogger(__name__)

# Log application root information - this will run when the module is imported
app_root = get_application_root()
if is_packaged_environment():
    logger.info("=" * 60)
    logger.info("RUNNING IN PACKAGED MODE")
    logger.info(f"APPLICATION ROOT (EXECUTABLE PARENT PATH): {app_root}")
    logger.info("=" * 60)
    # Only validate environment when running in packaged mode at import time
    validate_packaged_environment()
    os.chdir(str(app_root))
else:
    logger.info("=" * 60)
    logger.info("RUNNING IN DEVELOPMENT MODE")
    logger.info(f"APPLICATION ROOT PATH: {app_root}")
    logger.info("=" * 60)

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
    # The app root logging is now at the module level, so we don't need to repeat it here
    # We'll just use uvicorn to run the app
    uvicorn.run(
        app,
        host=host,
        port=port,
        log_level="info"
    )

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='AutoByteus Server')
    parser.add_argument('--port', type=int, default=8000, help='Port to run the server on')
    parser.add_argument('--host', type=str, default='127.0.0.1', help='Host to run the server on')
    
    args = parser.parse_args()
    run_server(args.host, args.port)
