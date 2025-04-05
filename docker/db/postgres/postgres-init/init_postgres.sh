#!/bin/bash
set -e

# Default values for local development (will be used if environment variables are not set)
DB_USER=${DB_USER:-"postgres"}
DB_PASSWORD=${DB_PASSWORD:-"password"}
DB_HOST=${DB_HOST:-"localhost"}
DB_PORT=${DB_PORT:-"5432"}
DB_NAME=${DB_NAME:-"autobyteus"}

# Log what's being used (helpful for debugging)
echo "Initializing PostgreSQL with:"
echo "  Host: $DB_HOST:$DB_PORT"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo "  Creating test database: test_db"

# Set password
export PGPASSWORD="$DB_PASSWORD"

# Create the test database
psql -v ON_ERROR_STOP=1 --username "$DB_USER" --host "$DB_HOST" --port "$DB_PORT" --dbname "$DB_NAME" <<-EOSQL
    DROP DATABASE IF EXISTS test_db;
    CREATE DATABASE test_db;
EOSQL

# Check if the operation was successful
if [ $? -eq 0 ]; then
    echo "✅ Test database successfully created"
else
    echo "❌ Failed to create test database"
    # Even if there's an error, continue to unset the password
fi

# Unset password for security
unset PGPASSWORD

echo "PostgreSQL initialization completed"
