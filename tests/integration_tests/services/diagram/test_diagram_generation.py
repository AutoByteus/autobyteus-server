import pytest
import os
from pathlib import Path
from autobyteus_server.services.diagram.diagram_service import PlantUMLService
from autobyteus_server.config.app_config_provider import app_config_provider

@pytest.fixture(scope="session")
def test_output_dir():
    """
    Create and return the test output directory for generated diagrams.
    """
    output_dir = Path(__file__).parent.parent.parent / "test_outputs" / "diagrams"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

@pytest.fixture(scope="session")
def setup_plantuml():
    """
    Ensure that the PlantUML jar exists before running tests.
    The expected jar path is obtained from the application's download directory.
    If the jar is missing, the tests will be skipped.
    
    Returns:
        An instance of PlantUMLService initialized with the expected jar path.
    """
    plantuml_jar_path = app_config_provider.config.get_download_dir() / "plantuml.jar"
    if not plantuml_jar_path.exists():
        pytest.skip(f"plantuml.jar not found in expected directory: {plantuml_jar_path}")
    return PlantUMLService(plantuml_jar_path=str(plantuml_jar_path))

@pytest.mark.integration
def test_sequence_diagram_generation(setup_plantuml, test_output_dir):
    """
    Test generating a simple sequence diagram using PlantUMLService.
    The generated diagram should be a valid PNG image.
    """
    plantuml_service = setup_plantuml
    content = """
    @startuml
    Alice -> Bob: Hello
    Bob --> Alice: Hi there
    @enduml
    """
    result = plantuml_service.generate_diagram(content)
    
    # Save the diagram for visual inspection
    output_path = test_output_dir / "sequence_diagram.png"
    with open(output_path, 'wb') as f:
        f.write(result)
    
    # Check for PNG file signature and minimal file length
    assert result.startswith(b'\x89PNG'), "The generated file does not start with PNG magic number"
    assert len(result) > 100, "The generated image data is unexpectedly small"
    print(f"\nSequence diagram saved to: {output_path}")

@pytest.mark.integration
def test_class_diagram_generation(setup_plantuml, test_output_dir):
    """
    Test generating a class diagram using PlantUMLService.
    The generated diagram should be a valid PNG image.
    """
    plantuml_service = setup_plantuml
    content = """
    @startuml
    class User {
        +username: string
        +email: string
        +login()
    }
    
    class Account {
        +balance: decimal
        +deposit()
        +withdraw()
    }
    
    User --> Account: has
    @enduml
    """
    result = plantuml_service.generate_diagram(content)
    
    # Save the diagram for visual inspection
    output_path = test_output_dir / "class_diagram.png"
    with open(output_path, 'wb') as f:
        f.write(result)
    
    # Validate the output as a PNG image
    assert result.startswith(b'\x89PNG'), "The generated file does not start with PNG magic number"
    assert len(result) > 100, "The generated image data is unexpectedly small"
    print(f"\nClass diagram saved to: {output_path}")

@pytest.mark.integration
def test_complex_sequence_diagram(setup_plantuml, test_output_dir):
    """
    Test generating a more complex sequence diagram using PlantUMLService.
    The generated diagram should be a valid PNG image.
    """
    plantuml_service = setup_plantuml
    content = """
    @startuml
    participant User
    participant Frontend
    participant API
    participant Database
    
    User -> Frontend: Submit Form
    activate Frontend
    Frontend -> API: POST /data
    activate API
    API -> Database: Save Data
    activate Database
    Database --> API: Confirm Save
    deactivate Database
    API --> Frontend: Success Response
    deactivate API
    Frontend --> User: Show Success
    deactivate Frontend
    @enduml
    """
    result = plantuml_service.generate_diagram(content)
    
    # Save the diagram for visual inspection
    output_path = test_output_dir / "complex_sequence_diagram.png"
    with open(output_path, 'wb') as f:
        f.write(result)
    
    # Validate that the result is a PNG image and has sufficient content size
    assert result.startswith(b'\x89PNG'), "The generated file does not start with PNG magic number"
    assert len(result) > 100, "The generated image data is unexpectedly small"
    print(f"\nComplex sequence diagram saved to: {output_path}")

@pytest.mark.integration
def test_invalid_diagram_content(setup_plantuml):
    """
    Test handling of invalid diagram content.
    The PlantUMLService should raise a RuntimeError when invalid content is provided.
    """
    plantuml_service = setup_plantuml
    content = "@startuml\ninvalid content\n@enduml"
    with pytest.raises(RuntimeError):
        plantuml_service.generate_diagram(content)
