from logging.config import fileConfig
from repository_sqlalchemy import Base
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
import autobyteus_server.workflow.persistence.conversation.models as models
import autobyteus_server.prompt_engineering.models as models

from autobyteus_server.config import app_config_provider

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

def get_database_url():
    """Generate database URL based on configuration."""
    app_config = app_config_provider.config
    app_config.initialize()
    db_type = app_config.get('DB_TYPE', 'sqlite')
    
    if db_type == 'sqlite':
        return f"sqlite:///{app_config.get('DB_NAME')}"
    elif db_type == 'postgresql':
        host = app_config.get('DB_HOST', 'localhost')
        port = app_config.get('DB_PORT', '5432')
        user = app_config.get('DB_USER', 'postgres')
        password = app_config.get('DB_PASSWORD', '')
        db_name = app_config.get('DB_NAME', 'postgres')
        return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
    else:
        raise ValueError(f"Unsupported database type: {db_type}")

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode."""
    # Override sqlalchemy.url with our dynamic URL
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = get_database_url()
    
    connectable = engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
