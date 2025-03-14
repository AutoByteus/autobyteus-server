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
        # Required directories - using same structure as autobyteus_rpa_llm_server
        required_dirs = [
            "logs",
            "download",
            "alembic",
            "alembic/versions",
            "playwright/driver",
            "mistral_common/data",
            "anthropic",
            "anthropic/data",
            "autobyteus_llm_client/certificates",
            "autobyteus_server/workflow/steps"  # Base directory for step prompts
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

def copy_downloads(destination_dir):
    """
    Copy download directory to the destination directory if it exists.
    
    Args:
        destination_dir (str): The destination directory.
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        # Source download directory
        source_download = "download"
        
        if not os.path.exists(source_download):
            logger.warning(f"Download directory not found at {source_download}, creating empty directory.")
            return True
            
        # Destination download directory
        dest_download = os.path.join(destination_dir, "download")
        
        # Copy download directory
        logger.info(f"Copying downloads from {source_download} to {dest_download}...")
        shutil.copytree(source_download, dest_download, dirs_exist_ok=True)
        
        logger.info("Downloads copied successfully.")
        return True
    except Exception as e:
        logger.error(f"Error copying downloads: {str(e)}")
        return False

def find_playwright_driver():
    """
    Locate the Playwright driver folder in the Python environment.
    Returns the path to the driver folder or None if not found.
    """
    try:
        # Get site-packages directories
        site_packages = site.getsitepackages()
        for sp in site_packages:
            driver_path = os.path.join(sp, "playwright", "driver")
            if os.path.exists(driver_path):
                logger.info(f"Found Playwright driver folder: {driver_path}")
                return driver_path
        logger.warning("Playwright driver folder not found in site-packages.")
        return None
    except Exception as e:
        logger.warning(f"Error locating Playwright driver folder: {str(e)}")
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
        driver_path = find_playwright_driver()
        if not driver_path:
            logger.warning("Cannot copy playwright.sh: Source folder not found.")
            return True  # Continue build even if this fails

        # Define source and destination paths
        source_script = os.path.join(driver_path, "playwright.sh")
        if not os.path.exists(source_script):
            logger.warning(f"playwright.sh not found in {driver_path}")
            return True  # Continue build even if this fails

        # Define destination path
        dest_driver_path = os.path.join(destination_dir, "playwright", "driver")
        os.makedirs(dest_driver_path, exist_ok=True)
        dest_script = os.path.join(dest_driver_path, "playwright.sh")

        # Copy only the script file
        logger.info(f"Copying playwright.sh from {source_script} to {dest_script}...")
        shutil.copy2(source_script, dest_script)
        # Make it executable
        os.chmod(dest_script, 0o755)
        logger.info("playwright.sh copied successfully.")
        return True
    except Exception as e:
        logger.warning(f"Error copying playwright.sh: {str(e)}")
        return True  # Continue build even if this fails

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

def find_autobyteus_llm_client_certificates():
    """
    Locate the certificates directory in the autobyteus_llm_client package.
    Returns the path to the certificates directory or None if not found.
    """
    try:
        # Get site-packages directories
        site_packages = site.getsitepackages()
        for sp in site_packages:
            cert_path = os.path.join(sp, "autobyteus_llm_client", "certificates")
            if os.path.exists(cert_path):
                # Verify that cert.pem exists in the directory
                cert_file = os.path.join(cert_path, "cert.pem")
                if os.path.exists(cert_file):
                    logger.info(f"Found autobyteus_llm_client certificates directory: {cert_path}")
                    return cert_path
                else:
                    logger.warning(f"autobyteus_llm_client certificates directory found but cert.pem is missing: {cert_path}")
            
        logger.error("certificates directory not found in autobyteus_llm_client package.")
        return None
    except Exception as e:
        logger.error(f"Error locating autobyteus_llm_client certificates directory: {str(e)}")
        return None

def copy_autobyteus_llm_client_certificates(destination_dir):
    """
    Copy the certificates directory from autobyteus_llm_client package to the specified destination directory.
    Args:
        destination_dir (str): The destination directory.
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        cert_path = find_autobyteus_llm_client_certificates()
        if not cert_path:
            logger.error("Cannot copy autobyteus_llm_client certificates: Directory not found.")
            return False

        # Define destination path
        dest_cert_path = os.path.join(destination_dir, "autobyteus_llm_client", "certificates")
        os.makedirs(os.path.dirname(dest_cert_path), exist_ok=True)

        # Copy the directory
        logger.info(f"Copying autobyteus_llm_client certificates from {cert_path} to {dest_cert_path}...")
        shutil.copytree(cert_path, dest_cert_path, dirs_exist_ok=True)
        logger.info("autobyteus_llm_client certificates copied successfully.")
        return True
    except Exception as e:
        logger.error(f"Error copying autobyteus_llm_client certificates: {str(e)}")
        return False

def find_workflow_step_prompts():
    """
    Locate all workflow step prompt directories in the autobyteus_server package.
    Returns a list of tuples with (source_path, relative_target_path).
    """
    step_prompts = []
    try:
        # Start from the current directory and search for the autobyteus_server module
        server_dir = "autobyteus_server"
        if not os.path.exists(server_dir):
            logger.warning(f"autobyteus_server directory not found at {server_dir}")
            return step_prompts
            
        # Path to the workflow steps directory
        steps_dir = os.path.join(server_dir, "workflow", "steps")
        if not os.path.exists(steps_dir):
            logger.warning(f"Workflow steps directory not found at {steps_dir}")
            return step_prompts
        
        # Walk through the steps directory and find all prompt folders
        for root, dirs, files in os.walk(steps_dir):
            if "prompt" in dirs:
                prompt_dir = os.path.join(root, "prompt")
                # Calculate the relative path for the target
                rel_path = os.path.relpath(prompt_dir, start=server_dir)
                target_path = os.path.join("autobyteus_server", rel_path)
                step_prompts.append((prompt_dir, target_path))
                logger.info(f"Found workflow step prompt directory: {prompt_dir} -> {target_path}")
        
        if not step_prompts:
            logger.warning("No workflow step prompt directories found.")
        else:
            logger.info(f"Found {len(step_prompts)} workflow step prompt directories.")
        
        return step_prompts
    except Exception as e:
        logger.error(f"Error locating workflow step prompt directories: {str(e)}")
        return step_prompts

def copy_workflow_step_prompts(destination_dir):
    """
    Copy all workflow step prompt directories to the specified destination directory.
    Args:
        destination_dir (str): The destination directory.
    Returns:
        bool: True if successful, False otherwise.
    """
    try:
        step_prompts = find_workflow_step_prompts()
        if not step_prompts:
            logger.error("Cannot copy workflow step prompts: No prompt directories found.")
            return False

        success = True
        for source_path, target_path in step_prompts:
            # Define destination path
            dest_prompt_path = os.path.join(destination_dir, target_path)
            
            # Ensure destination directory exists
            os.makedirs(os.path.dirname(dest_prompt_path), exist_ok=True)
            
            # Copy the directory
            logger.info(f"Copying workflow step prompts from {source_path} to {dest_prompt_path}...")
            try:
                shutil.copytree(source_path, dest_prompt_path, dirs_exist_ok=True)
                logger.info(f"Workflow step prompts copied successfully for {target_path}.")
            except Exception as e:
                logger.error(f"Error copying workflow step prompts for {target_path}: {str(e)}")
                success = False
        
        return success
    except Exception as e:
        logger.error(f"Error copying workflow step prompts: {str(e)}")
        return False

# Main function that executes the copy operations
def main():
    """
    Main function to copy all required dependencies.
    """
    if len(sys.argv) < 3:
        logger.error("Usage: python copy_dependencies_standalone.py <destination_dir> <version>")
        return 1
        
    destination_dir = sys.argv[1]
    version = sys.argv[2]
    
    logger.info(f"Copying dependencies to {destination_dir} for AutoByteus Server v{version}...")
    
    # Create required directories
    if not create_required_directories(destination_dir):
        logger.error("Failed to create required directories.")
        return 1
        
    # Create required files
    if not create_required_files(destination_dir, version):
        logger.error("Failed to create required files.")
        return 1
        
    # Copy Alembic files
    if not copy_alembic_files(destination_dir):
        logger.error("Failed to copy Alembic files.")
        return 1
        
    # Copy download directory
    if not copy_downloads(destination_dir):
        logger.error("Failed to copy download directory.")
        return 1
        
    # Copy Playwright script
    copy_playwright_script(destination_dir)
    # Don't check return value - continue build even if Playwright is not found
        
    # Copy mistral_common data
    if not copy_mistral_data(destination_dir):
        logger.error("Failed to copy mistral_common data.")
        return 1
        
    # Copy Anthropic tokenizer
    if not copy_anthropic_tokenizer(destination_dir):
        logger.error("Failed to copy Anthropic tokenizer.")
        return 1
        
    # Copy autobyteus_llm_client certificates
    if not copy_autobyteus_llm_client_certificates(destination_dir):
        logger.error("Failed to copy autobyteus_llm_client certificates.")
        return 1
        
    # Copy workflow step prompts
    if not copy_workflow_step_prompts(destination_dir):
        logger.error("Failed to copy workflow step prompts.")
        return 1
        
    logger.info(f"Successfully copied all dependencies to {destination_dir}.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
