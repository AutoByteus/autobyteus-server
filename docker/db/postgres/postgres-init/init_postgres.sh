#!/bin/bash
set -e

# Set password
export PGPASSWORD="$DB_PASSWORD"

# Create the test database
psql -v ON_ERROR_STOP=1 --username "$DB_USER" --host "$DB_HOST" --port "$DB_PORT" --dbname "$DB_NAME" <<-EOSQL
    DROP DATABASE IF EXISTS test_db;
    CREATE DATABASE test_db;
EOSQL

# Unset password for security
unset PGPASSWORD