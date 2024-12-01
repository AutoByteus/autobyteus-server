from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
from autobyteus_server.services.diagram.diagram_service import PlantUMLService

router = APIRouter()
diagram_service = PlantUMLService()

class DiagramRequest(BaseModel):
    content: str

@router.post("/diagram")
async def create_diagram(request: DiagramRequest):
    try:
        image_data = diagram_service.generate_diagram(request.content)
        return Response(content=image_data, media_type="image/png")
    except FileNotFoundError as e:
        raise HTTPException(status_code=500, detail="plantuml.jar not found.")
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")