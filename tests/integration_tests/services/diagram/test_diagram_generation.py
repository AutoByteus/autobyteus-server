import pytest
import os
from pathlib import Path
from autobyteus_server.services.diagram.diagram_service import plantuml_service
from autobyteus_server.config import config

@pytest.fixture(scope="session")
def test_output_dir():
    """Create and return the test output directory."""
    output_dir = Path(__file__).parent.parent.parent / "test_outputs" / "diagrams"
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir

@pytest.fixture(scope="session")
def setup_plantuml():
    """Check if PlantUML jar exists before running tests."""
    if not config.ensure_resource_exists('plantuml.jar'):
        pytest.skip(f"plantuml.jar not found in resources directory: {config.get('RESOURCES_DIR')}")

@pytest.mark.integration
def test_sequence_diagram_generation(setup_plantuml, test_output_dir):
    """Test generating a sequence diagram."""
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
    
    assert result.startswith(b'\x89PNG')  # PNG magic number
    assert len(result) > 100  # Ensure we got actual image data
    print(f"\nSequence diagram saved to: {output_path}")

@pytest.mark.integration
def test_class_diagram_generation(setup_plantuml, test_output_dir):
    """Test generating a class diagram."""
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
    
    assert result.startswith(b'\x89PNG')  # PNG magic number
    assert len(result) > 100  # Ensure we got actual image data
    print(f"\nClass diagram saved to: {output_path}")

@pytest.mark.integration
def test_complex_sequence_diagram(setup_plantuml, test_output_dir):
    """Test generating a more complex sequence diagram."""
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
    
    assert result.startswith(b'\x89PNG')  # PNG magic number
    assert len(result) > 100  # Ensure we got actual image data
    print(f"\nComplex sequence diagram saved to: {output_path}")

@pytest.mark.integration
def test_invalid_diagram_content(setup_plantuml):
    """Test handling of invalid diagram content."""
    content = "@startuml\ninvalid content\n@enduml"
    with pytest.raises(RuntimeError):
        plantuml_service.generate_diagram(content)