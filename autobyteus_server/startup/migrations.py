import logging
from pathlib import Path
from alembic import command
from alembic.config import Config as AlembicConfig
from autobyteus_server.config import app_config_provider

logger = logging.getLogger(__name__)

def get_alembic_config():
    """Get Alembic configuration"""
    alembic_cfg = AlembicConfig()
    config = app_config_provider.config
    app_root = config.get_app_root_dir()
    
    # Set the script location
    alembic_cfg.set_main_option('script_location', str(app_root / 'alembic'))
    
    # Get database configuration
    db_type = config.get('DB_TYPE', 'sqlite')
    
    if db_type == 'sqlite':
        # Get the SQLite database path from config
        db_path = config.get('DB_NAME')
        if not db_path:
            # If DB_NAME is not set, use default path from db_dir
            db_dir = config.get_db_dir()
            db_path = str(db_dir / 'production.db')
            
        # Ensure the database directory exists
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        
        # Set the SQLite URL
        db_url = f"sqlite:///{db_path}"
        logger.info(f"Using SQLite database at: {db_path}")
    else:
        # Handle other database types if needed
        raise ValueError(f"Unsupported database type: {db_type}")
    
    # Set the SQLAlchemy URL in Alembic config
    alembic_cfg.set_main_option('sqlalchemy.url', db_url)
    return alembic_cfg

def run_migrations():
    """Run database migrations"""
    try:
        logger.info("Running database migrations...")
        alembic_cfg = get_alembic_config()
        command.upgrade(alembic_cfg, "head")
        logger.info("Database migrations completed successfully")
    except Exception as e:
        logger.error(f"Error running database migrations: {str(e)}")
        raise
