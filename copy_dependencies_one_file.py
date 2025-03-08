import os
import sys
import site
import logging
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

def find_alembic_directory():
    """
    Locate the alembic directory in the current project.
    Returns the path to the alembic directory or None if not found.
    """
    try:
        # Check if alembic exists in the current directory
        alembic_path = "alembic"
        if os.path.exists(alembic_path) and os.path.isdir(alembic_path):
            logger.info(f"Found alembic directory: {alembic_path}")
            return alembic_path
        logger.warning("Alembic directory not found in the current project.")
        return None
    except Exception as e:
        logger.error(f"Error locating alembic directory: {str(e)}")
        return None

def find_resources_directory():
    """
    Locate the resources directory in the current project.
    Returns the path to the resources directory or None if not found.
    """
    try:
        # Check if resources exists in the current directory
        resources_path = "resources"
        if os.path.exists(resources_path) and os.path.isdir(resources_path):
            logger.info(f"Found resources directory: {resources_path}")
            return resources_path
        logger.warning("Resources directory not found in the current project.")
        return None
    except Exception as e:
        logger.error(f"Error locating resources directory: {str(e)}")
        return None

def find_certificates_directory():
    """
    Locate the certificates directory in the current project.
    Returns the path to the certificates directory or None if not found.
    """
    try:
        # Check if certificates exists in the current directory
        certificates_path = "certificates"
        if os.path.exists(certificates_path) and os.path.isdir(certificates_path):
            logger.info(f"Found certificates directory: {certificates_path}")
            return certificates_path
        logger.warning("Certificates directory not found in the current project.")
        return None
    except Exception as e:
        logger.error(f"Error locating certificates directory: {str(e)}")
        return None

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

def check_config_files():
    """
    Check for configuration files in the current directory.
    Returns a list of tuples containing (file path, inclusion flag).
    """
    config_files = []
    
    # Check for logging_config.ini
    if os.path.exists("logging_config.ini"):
        logger.info("Found logging_config.ini in current directory")
        config_files.append(("logging_config.ini", True))
    
    # Check for .env file
    if os.path.exists(".env"):
        logger.info("Found .env file in current directory")
        config_files.append((".env", True))
    
    # Check for alembic.ini file
    if os.path.exists("alembic.ini"):
        logger.info("Found alembic.ini in current directory")
        config_files.append(("alembic.ini", True))
    
    # Check for logs directory
    if os.path.exists("logs"):
        logger.info("Found logs directory in current directory")
        config_files.append(("logs", True))
    
    return config_files

def get_nuitka_include_arguments():
    """
    Generate Nuitka include arguments for specific dependency files.
    Returns a list of Nuitka include arguments.
    """
    include_args = []
    
    # Check for config files
    config_files = check_config_files()
    for file_path, should_include in config_files:
        if should_include:
            if os.path.isdir(file_path):
                include_args.append(f"--include-data-dir={file_path}={file_path}")
            else:
                include_args.append(f"--include-data-file={file_path}={file_path}")
    
    # Find alembic directory
    alembic_dir = find_alembic_directory()
    if alembic_dir:
        include_args.append(f"--include-data-dir={alembic_dir}={alembic_dir}")
    
    # Find resources directory
    resources_dir = find_resources_directory()
    if resources_dir:
        include_args.append(f"--include-data-dir={resources_dir}={resources_dir}")
    
    # Find certificates directory
    certificates_dir = find_certificates_directory()
    if certificates_dir:
        include_args.append(f"--include-data-dir={certificates_dir}={certificates_dir}")
    
    # Find playwright.sh script
    playwright_script = find_playwright_script()
    if playwright_script:
        # For the playwright.sh script, we want to include it at the correct relative path
        # The structure should be: playwright/driver/playwright.sh
        include_args.append(f"--include-data-file={playwright_script}=playwright/driver/playwright.sh")
    
    # Find mistral_common data folder
    mistral_data_path = find_mistral_data()
    if mistral_data_path:
        # Use --include-data-dir for the entire mistral_common data directory
        # The target directory will be mistral_common/data
        include_args.append(f"--include-data-dir={mistral_data_path}=mistral_common/data")
    
    # Find Anthropic tokenizer.json
    tokenizer_path = find_anthropic_tokenizer()
    if tokenizer_path:
        # Calculate the relative path for the tokenizer
        if "data" in tokenizer_path:
            rel_path = "anthropic/data/tokenizer.json"
        else:
            rel_path = "anthropic/tokenizer.json"
        include_args.append(f"--include-data-file={tokenizer_path}={rel_path}")
    
    return include_args

def output_include_args(output_file=None):
    """
    Output Nuitka include arguments either to a file or stdout.
    Args:
        output_file (str, optional): Path to write the include arguments to.
    """
    include_args = get_nuitka_include_arguments()
    
    if output_file:
        with open(output_file, 'w') as f:
            for arg in include_args:
                f.write(f"{arg}\n")
        logger.info(f"Nuitka include arguments written to {output_file}")
    else:
        # Output in a format that can be easily consumed by bash scripts
        print("NUITKA_DEPENDENCY_ARGS=" + json.dumps(include_args))

def main():
    if len(sys.argv) == 1:
        # If no arguments provided, output to stdout
        output_include_args()
    elif len(sys.argv) == 2:
        # If one argument provided, treat it as an output file
        output_include_args(sys.argv[1])
    else:
        logger.error("Usage: python copy_dependencies_one_file.py [output_file]")
        sys.exit(1)

if __name__ == "__main__":
    main()
