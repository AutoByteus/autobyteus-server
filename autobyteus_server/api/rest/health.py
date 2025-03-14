"""
Health check endpoint for the server.
"""
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    """
    Simple health check endpoint that returns a 200 OK response.
    This is used by the client to determine if the server is ready.
    """
    return {"status": "ok", "message": "Server is running"}
