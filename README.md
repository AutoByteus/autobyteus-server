# AutoByteus Server

A FastAPI-based server with GraphQL and REST endpoints.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Virtual environment tool (e.g., venv, conda)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd autobyteus-server
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Environment Setup

Create a `.env` file in the root directory with your configuration:

```env
# Add your environment variables here
DEBUG=True
LOG_LEVEL=INFO
# Add other configuration variables as needed
```

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

After starting the server, access the API documentation at:
- OpenAPI (Swagger): `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### GraphQL Endpoint
The GraphQL endpoint is available at:
```
http://localhost:8000/graphql
```

### WebSocket Endpoint
WebSocket connections for GraphQL subscriptions are available at:
```
ws://localhost:8000/graphql
```

### REST Endpoints
File upload and other REST endpoints are available under:
```
http://localhost:8000/rest
```

## Project Structure

- `autobyteus_server/`: Main package directory
  - `api/`: API endpoints and routing
    - `graphql/`: GraphQL schema and resolvers
    - `rest/`: REST endpoints
  - `config/`: Configuration files
  - `app.py`: Main application entry point

## Development

### Code Style
The project follows PEP 8 guidelines. Run linting with:
```bash
flake8 autobyteus_server
```

### Running Tests
```bash
pytest
```

## Logging

Logs are configured in `config/logging_config.py`. By default, logs are written to both console and file outputs.