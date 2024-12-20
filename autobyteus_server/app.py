
"""
app.py: The main entry point for the AutoByteus server application.

This script initializes the FastAPI server with GraphQL endpoints
using the Strawberry GraphQL library.

To start the server, run the following command from the project root:
    uvicorn autobyteus_server.app:app --host 0.0.0.0 --port 8001

For development with auto-reload:
    uvicorn autobyteus_server.app:app --host 0.0.0.0 --port 8000 --reload

Note: Adjust the host and port as needed for your environment.
"""


import sys
from pathlib import Path

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from autobyteus_server.api.graphql.schema import schema
from strawberry.fastapi import GraphQLRouter
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL
from autobyteus_server.api.rest import router as rest_router
from autobyteus_server.config.logging_config import configure_logger
from autobyteus_server.api.websocket.real_time_audio_router import transcription_router

# Configure logging
configure_logger()

# Create FastAPI app
app = FastAPI()

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
graphql_router = GraphQLRouter(schema, subscription_protocols=[
    GRAPHQL_WS_PROTOCOL,
    GRAPHQL_TRANSPORT_WS_PROTOCOL,
])
app.include_router(graphql_router, prefix="/graphql")

# Include REST routers
app.include_router(rest_router, prefix="/rest")
app.include_router(transcription_router)