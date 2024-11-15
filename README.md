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
# Basic Configuration
DEBUG=True
LOG_LEVEL=INFO

# Database Configuration
PERSISTENCE_PROVIDER=sqlite  # Options: sqlite, postgresql, mongodb
DB_TYPE=sqlite              # Options: sqlite, postgresql, mongodb

# PostgreSQL specific configuration (required if using PostgreSQL)
# DB_HOST=localhost        # PostgreSQL host
# DB_PORT=5432            # PostgreSQL port
# DB_NAME=autobyteus      # PostgreSQL database name
# DB_USER=postgres        # PostgreSQL username
# DB_PASSWORD=password    # PostgreSQL password

# MongoDB specific configuration (required if using MongoDB)
# MONGO_HOST=localhost         # MongoDB host
# MONGO_PORT=27017            # MongoDB port
# MONGO_USERNAME=             # MongoDB username
# MONGO_PASSWORD=             # MongoDB password
# MONGO_DATABASE=test_database # MongoDB database name
# MONGO_REPLICA_SET=rs0       # MongoDB replica set name (required for transactions)

# Add other configuration variables as needed
```

## Database Setup

The project uses Alembic for database migrations. After configuring your database in the `.env` file:

1. Initialize the database:
```bash
alembic upgrade head
```

2. Create a new migration (when making model changes):
```bash
alembic revision --autogenerate -m "description of changes"
```

3. Apply pending migrations:
```bash
alembic upgrade head
```

4. Rollback last migration:
```bash
alembic downgrade -1
```

### Supported Database Types

1. SQLite (Default)
   - Set `PERSISTENCE_PROVIDER=sqlite` and `DB_TYPE=sqlite`
   - SQLite database file will be automatically created
   - Good for development and small deployments

2. PostgreSQL
   - Set `PERSISTENCE_PROVIDER=postgresql` and `DB_TYPE=postgresql`
   - Requires additional configuration:
     - DB_HOST
     - DB_PORT
     - DB_NAME
     - DB_USER
     - DB_PASSWORD
   - Recommended for production deployments

3. MongoDB
   - Set `PERSISTENCE_PROVIDER=mongodb` and `DB_TYPE=mongodb`
   - Requires additional configuration:
     - MONGO_HOST
     - MONGO_PORT
     - MONGO_USERNAME
     - MONGO_PASSWORD
     - MONGO_DATABASE
     - MONGO_REPLICA_SET
   - **Important**: MongoDB transactions require a replica set cluster setup
   - Setting up MongoDB Cluster:
     1. MongoDB must be configured as a replica set for transactions
     2. Default replica set name is 'rs0'
     3. Configure MongoDB cluster before running the application
   - Recommended for document-oriented data models

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