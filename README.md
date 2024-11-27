# AutoByteus Server

A FastAPI-based server with GraphQL and REST endpoints.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment tool (e.g., venv, conda)
- **Java Runtime Environment (JRE)**
- **PlantUML JAR file**

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd autobyteus-server
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Install Java Runtime Environment (JRE):**
   - **Ubuntu/Debian:**
     ```bash
     sudo apt-get install default-jre
     ```
   - **macOS (using Homebrew):**
     ```bash
     brew install openjdk
     ```
     After installation, you might need to add Java to your PATH:
     ```bash
     sudo ln -sfn $(brew --prefix openjdk)/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk.jdk
     ```
   - **Windows:**
     - Download and install Java from the [official website](https://www.java.com/en/download/).

5. **Download PlantUML JAR file:**
   ```bash
   curl -L -o plantuml.jar https://downloads.sourceforge.net/project/plantuml/plantuml.jar
   ```
   - Ensure that the `plantuml.jar` file is placed in the root directory of the `autobyteus-server` project.
   - Alternatively, you can download it manually from the [PlantUML website](https://plantuml.com/download).

## Environment Setup

Create a `.env` file in the root directory with your configuration:

```env
# Basic Configuration
DEBUG=True
LOG_LEVEL=INFO

# Database Configuration
PERSISTENCE_PROVIDER=sqlite  # Options: sqlite, postgresql, mongodb
DB_TYPE=sqlite              # Options: sqlite, postgresql, mongodb

# Add other configuration variables as needed
```

## Database Setup

[... existing database setup instructions remain unchanged ...]

## Running the Server

### Development Mode
```bash
uvicorn autobyteus_server.app:app --host 0.0.0.0 --port 8000 --reload
```

### Production Mode
```bash
uvicorn autobyteus_server.app:app --host 0.0.0.0 --port 8000
```

## API Documentation

[... existing API documentation instructions remain unchanged ...]

## Additional Configuration for PlantUML

The application uses PlantUML to render diagrams from `plantuml` code blocks within Markdown files.

- **Ensure Java is installed:** PlantUML requires Java to run.
- **Place `plantuml.jar` in the correct location:** The default path is the root directory of the `autobyteus-server` project.
  - If you place `plantuml.jar` in a different directory, update the `plantuml_jar_path` variable in `autobyteus_server/api/rest/plantuml.py` accordingly.
- **Verify Java and PlantUML installation:**
  ```bash
  java -jar plantuml.jar -version
  ```
  This should display the PlantUML version information if everything is set up correctly.

## Project Structure

[... existing project structure information remains unchanged ...]

## Development

[... existing development instructions remain unchanged ...]

## Logging

[... existing logging instructions remain unchanged ...]