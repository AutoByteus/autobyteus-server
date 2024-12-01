from fastapi import APIRouter
from .upload_file import router as upload_file_router
from .plantuml import router as plantuml_router

router = APIRouter()

# Removed prefixes to avoid duplicating paths
router.include_router(upload_file_router)
router.include_router(plantuml_router)