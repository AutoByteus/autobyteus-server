import os
import sys
import site
import shutil
import logging

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def create_required_files(destination_dir, version):
    """
    Create necessary files in the specified destination directory if they don't exist.
    
    Args:
        destination_dir (str): The destination directory.
        version (str): The version of the application.
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Required files with default content
        required_files = {
            '.env': f"# Environment variables for AutoByteus Server v{version}\n# Replace with your actual values\n",
            'logging_config.ini': "[loggers]\nkeys=root\n\n[handlers]\nkeys=consoleHandler,fileHandler\n\n[formatters]\nkeys=simpleFormatter\n\n[logger_root]\nlevel=INFO\nhandlers=consoleHandler,fileHandler\nqualname=root\npropagete=0\n\n[handler_consoleHandler]\nclass=StreamHandler\nlevel=INFO\nformatter=simpleFormatter\nargs=(sys.stdout,)\n\n[handler_fileHandler]\nclass=handlers.RotatingFileHandler\nlevel=INFO\nformatter=simpleFormatter\nargs=('logs/autobyteus-server.log', 'a', 10485760, 5)\n\n[formatter_simpleFormatter]\nformat=%(asctime)s - %(name)s - %(levelname)s - %(message)s\ndatefmt=%Y-%m-%d %H:%M:%S\n",
            'alembic.ini': "# A generic, single database configuration.\n\n[alembic]\nscript_location = alembic\n\n# Generic configurations\nfile_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d%%(second).2d_%%(slug)s\nprepend_sys_path = .\n\n# Connection string for SQLAlchemy\nsqlalchemy.url = sqlite:///autobyteus.db\n\n# Logging configuration\nloggers = alembic\n\n[logger_alembic]\nlevel = INFO\nhandlers =\nqualname = alembic\n",
            'version.txt': f"AutoByteus Server v{version}\nBuild date: {os.popen('date').read().strip()}\n"
        }
        
        for filename, content in required_files.items():
            file_path = os.path.join(destination_dir, filename)
            
            # Check if file already exists
            if os.path.exists(file_path):
                logger.info(f"{filename} already exists in the destination directory.")
                continue
                
            # Create file with default content
            logger.info(f"Creating {filename} at {file_path}...")
            with open(file_path, 'w') as f:
                f.write(content)
            
        logger.info("Required files created successfully.")
        return True
    except Exception as e:
        logger.error(f"Error creating required files: {str(e)}")
        return False

def create_required_directories(destination_dir):
    """
    Create required directories in the specified destination directory if they don't exist.
    
    Args:
        destination_dir (str): The destination directory.
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Required directories
        required_dirs = [
            "logs",
            "resources",
            "alembic",
            "alembic/versions",
            "playwright/driver",
            "mistral_common/data",
            "anthropic",
            "anthropic/data"
        ]
        
        for directory in required_dirs:
            dir_path = os.path.join(destination_dir, directory)
            
            # Create directory if it doesn't exist
            if not os.path.exists(dir_path):
                logger.info(f"Creating directory at {dir_path}...")
                os.makedirs(dir_path, exist_ok=True)
                
        logger.info("Required directories created successfully.")
        return True
    except Exception as e:
        logger.error(f"Error creating required directories: {str(e)}")
        return False

def copy_alembic_files(destination_dir):
    """
    Copy alembic files to the destination directory if they exist.
    
    Args:
        destination_dir (str): The destination directory.
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Source alembic directory - adjust path as needed
        source_alembic = "alembic"
        
        if not os.path.exists(source_alembic):
            logger.warning(f"Alembic directory not found at {source_alembic}, creating empty structure.")
            return True
            
        # Destination alembic directory
        dest_alembic = os.path.join(destination_dir, "alembic")
        
        # Copy alembic directory
        logger.info(f"Copying alembic files from {source_alembic} to {dest_alembic}...")
        shutil.copytree(source_alembic, dest_alembic, dirs_exist_ok=True)
        
        logger.info("Alembic files copied successfully.")
        return True
    except Exception as e:
        logger.error(f"Error copying alembic files: {str(e)}")
        return False

def copy_resources(destination_dir):
    """
    Copy resources directory to the destination directory if it exists.
    
    Args:
        destination_dir (str): The destination directory.
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Source resources directory
        source_resources = "resources"
        
        if not os.path.exists(source_resources):
            logger.warning(f"Resources directory not found at {source_resources}, creating empty directory.")
            return True
            
        # Destination resources directory
        dest_resources = os.path.join(destination_dir, "resources")
        
        # Copy resources directory
        logger.info(f"Copying resources from {source_resources} to {dest_resources}...")
        shutil.copytree(source_resources, dest_resources, dirs_exist_ok=True)
        
        logger.info("Resources copied successfully.")
        return True
    except Exception as e:
        logger.error(f"Error copying resources: {str(e)}")
        return False

def find_playwright_script():
    """
    Locate only the playwright.sh script in the Playwright driver folder.
    Returns the path to the playwright.sh file or None if not found.
    """
    try:
        # Get site-packages directories
        site_packages = site.getsitepackages()
        for sp in site_packages:
            script_path = os.path.join(sp, "playwright", "driver", "playwright.sh")
            if os.path.exists(script_path):
                logger.info(f"Found playwright.sh script: {script_path}")
                # Make sure it's executable
                os.chmod(script_path, 0o755)
                return script_path
        logger.error("playwright.sh script not found in playwright driver folder.")
        return None
    except Exception as e:
        logger.error(f"Error locating playwright.sh script: {str(e)}")
        return None

def copy_playwright_script(destination_dir):
    """
    Copy only the playwright.sh file to the specified destination directory.
    Args:
        destination_dir (str): The destination directory.
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        script_path = find_playwright_script()
        if not script_path:
            logger.error("Cannot copy playwright.sh: Source file not found.")
            return False

        # Define destination path
        dest_driver_path = os.path.join(destination_dir, "playwright", "driver")
        os.makedirs(dest_driver_path, exist_ok=True)
        dest_script = os.path.join(dest_driver_path, "playwright.sh")

        # Copy only the script file
        logger.info(f"Copying playwright.sh from {script_path} to {dest_script}...")
        shutil.copy2(script_path, dest_script)
        # Make it executable
        os.chmod(dest_script, 0o755)
        logger.info("playwright.sh copied successfully.")
        return True
    except Exception as e:
        logger.error(f"Error copying playwright.sh: {str(e)}")
        return False

def find_mistral_data():
    """
    Locate the mistral_common data folder in the Python environment.
    Returns the path to the data folder or None if not found.
    """
    try:
        # Get site-packages directories
        site_packages = site.getsitepackages()
        for sp in site_packages:
            data_path = os.path.join(sp, "mistral_common", "data")
            if os.path.exists(data_path):
                logger.info(f"Found mistral_common data folder: {data_path}")
                return data_path
        logger.error("mistral_common data folder not found in site-packages.")
        return None
    except Exception as e:
        logger.error(f"Error locating mistral_common data folder: {str(e)}")
        return None

def copy_mistral_data(destination_dir):
    """
    Copy the mistral_common data folder to the specified destination directory.
    Args:
        destination_dir (str): The destination directory.
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        data_path = find_mistral_data()
        if not data_path:
            logger.error("Cannot copy mistral_common data: Source folder not found.")
            return False

        # Define destination path
        dest_data_path = os.path.join(destination_dir, "mistral_common", "data")
        os.makedirs(os.path.dirname(dest_data_path), exist_ok=True)

        # Copy the folder
        logger.info(f"Copying mistral_common data from {data_path} to {dest_data_path}...")
        shutil.copytree(data_path, dest_data_path, dirs_exist_ok=True)
        logger.info("mistral_common data copied successfully.")
        return True
    except Exception as e:
        logger.error(f"Error copying mistral_common data: {str(e)}")
        return False

def find_anthropic_tokenizer():
    """
    Locate the Anthropic tokenizer.json file in the Python environment.
    Returns the path to the tokenizer.json file or None if not found.
    """
    try:
        # Get site-packages directories
        site_packages = site.getsitepackages()
        for sp in site_packages:
            tokenizer_path = os.path.join(sp, "anthropic", "tokenizer.json")
            if os.path.exists(tokenizer_path):
                logger.info(f"Found Anthropic tokenizer.json: {tokenizer_path}")
                return tokenizer_path
            
            # Also check in an alternative location - sometimes it might be in a different folder
            tokenizer_path = os.path.join(sp, "anthropic", "data", "tokenizer.json")
            if os.path.exists(tokenizer_path):
                logger.info(f"Found Anthropic tokenizer.json in data subfolder: {tokenizer_path}")
                return tokenizer_path
        
        logger.error("Anthropic tokenizer.json not found in site-packages.")
        return None
    except Exception as e:
        logger.error(f"Error locating Anthropic tokenizer.json: {str(e)}")
        return None

def copy_anthropic_tokenizer(destination_dir):
    """
    Copy the Anthropic tokenizer.json file to the specified destination directory.
    Args:
        destination_dir (str): The destination directory.
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        tokenizer_path = find_anthropic_tokenizer()
        if not tokenizer_path:
            logger.error("Cannot copy tokenizer.json: File not found.")
            return False

        # Determine the destination path based on the source path
        if "data" in tokenizer_path:
            # If the source has a data subfolder, maintain that structure
            dest_tokenizer_path = os.path.join(destination_dir, "anthropic", "data", "tokenizer.json")
        else:
            # Otherwise put it directly in the anthropic folder
            dest_tokenizer_path = os.path.join(destination_dir, "anthropic", "tokenizer.json")
            
        # Ensure destination directory exists
        os.makedirs(os.path.dirname(dest_tokenizer_path), exist_ok=True)

        # Copy the file
        logger.info(f"Copying tokenizer.json from {tokenizer_path} to {dest_tokenizer_path}...")
        shutil.copy2(tokenizer_path, dest_tokenizer_path)
        logger.info("Anthropic tokenizer.json copied successfully.")
        return True
    except Exception as e:
        logger.error(f"Error copying Anthropic tokenizer.json: {str(e)}")
        return False

def main():
    if len(sys.argv) < 2:
        logger.error("Usage: python copy_dependencies_standalone.py <output_dir> [version]")
        sys.exit(1)

    output_dir = sys.argv[1]
    version = sys.argv[2] if len(sys.argv) > 2 else "1.0"
    
    # The app.dist directory is where we need to copy the dependencies
    destination_dir = os.path.join(output_dir, "app.dist")
    
    if not os.path.exists(destination_dir):
        logger.error(f"Destination directory {destination_dir} does not exist. Make sure Nuitka build has completed.")
        sys.exit(1)
    
    logger.info(f"Preparing files for AutoByteus Server v{version}...")
    
    # Create required files
    if not create_required_files(destination_dir, version):
        logger.warning("Failed to create all required files, but continuing build...")
    
    # Create required directories
    if not create_required_directories(destination_dir):
        logger.warning("Failed to create all required directories, but continuing build...")
    
    # Copy alembic files if they exist
    if not copy_alembic_files(destination_dir):
        logger.warning("Failed to copy alembic files, but continuing build...")
    
    # Copy resources if they exist
    if not copy_resources(destination_dir):
        logger.warning("Failed to copy resources, but continuing build...")
    
    # Copy the playwright.sh script
    if not copy_playwright_script(destination_dir):
        logger.warning("Failed to copy playwright.sh, but continuing build...")
        
    # Copy the mistral_common data folder
    if not copy_mistral_data(destination_dir):
        logger.warning("Failed to copy mistral_common data folder, but continuing build...")
    
    # Copy the Anthropic tokenizer.json file
    if not copy_anthropic_tokenizer(destination_dir):
        logger.warning("Failed to copy Anthropic tokenizer.json, but continuing build...")
    
    logger.info(f"All required files and directories prepared successfully for v{version}.")

if __name__ == "__main__":
    main()
