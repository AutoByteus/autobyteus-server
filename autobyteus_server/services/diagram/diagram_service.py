from abc import ABC, abstractmethod
import subprocess
import tempfile
import os
from typing import Optional
from autobyteus_server.config import config
from autobyteus.utils.singleton import ABCSingletonMeta

class DiagramService(metaclass=ABCSingletonMeta):
    """Abstract base class for diagram generation services."""
    
    @abstractmethod
    def generate_diagram(self, content: str) -> bytes:
        """Generate a diagram from the given content."""
        pass

class PlantUMLService(DiagramService):
    """PlantUML implementation of diagram service."""
    
    def __init__(self, plantuml_jar_path: Optional[str] = None):
        """Initialize the PlantUML service.
        
        Args:
            plantuml_jar_path: Optional path to plantuml.jar. If not provided,
                              will use the path from config.
        """
        self.plantuml_jar_path = plantuml_jar_path or config.get('PLANTUML_JAR_PATH')
        if not os.path.exists(self.plantuml_jar_path):
            raise FileNotFoundError(
                f"plantuml.jar not found at {self.plantuml_jar_path}. "
                f"Please place it in the resources directory: {config.get('RESOURCES_DIR')}"
            )

    def generate_diagram(self, content: str) -> bytes:
        """Generate a diagram using PlantUML.
        
        Args:
            content: PlantUML diagram content as string
            
        Returns:
            bytes: Generated diagram as PNG image data
            
        Raises:
            RuntimeError: If diagram generation fails
        """
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.puml') as uml_file:
                uml_file.write(content.encode('utf-8'))
                uml_file_path = uml_file.name

            # PlantUML generates output file by replacing the input extension with .png
            output_file_path = uml_file_path[:-5] + '.png'  # remove .puml and add .png

            command = ['java', '-jar', self.plantuml_jar_path, uml_file_path]
            subprocess.check_call(command)

            with open(output_file_path, 'rb') as image_file:
                image_data = image_file.read()

            return image_data

        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Diagram generation failed: {str(e)}")
        finally:
            # Clean up temporary files
            if 'uml_file_path' in locals():
                os.remove(uml_file_path)
            if 'output_file_path' in locals() and os.path.exists(output_file_path):
                os.remove(output_file_path)

# Create singleton instance
plantuml_service = PlantUMLService()