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

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from autobyteus_server.api.graphql.schema import schema
from strawberry.fastapi import GraphQLRouter
from strawberry.subscriptions import GRAPHQL_TRANSPORT_WS_PROTOCOL, GRAPHQL_WS_PROTOCOL
from autobyteus_server.api.rest.upload_file import router as upload_file_router
from autobyteus_server.config.logging_config import configure_logger

# Configure logging
configure_logger()

# Create FastAPI app
app = FastAPI()

# Allow all origins for CORS
# Note: This can pose security risks if not managed properly.
# Ensure that your application has appropriate security measures in place.
origins = "*"

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,  # Must be False when using "*" for allow_origins
    allow_methods=["*"],
    allow_headers=["*"],
)

# Set up GraphQL router
graphql_router = GraphQLRouter(schema, subscription_protocols=[
    GRAPHQL_WS_PROTOCOL,
    GRAPHQL_TRANSPORT_WS_PROTOCOL,
])
app.include_router(graphql_router, prefix="/graphql")

# Include REST router for file uploads
app.include_router(upload_file_router, prefix="/rest")

# The 'app' variable is now available for uvicorn to use when starting the server