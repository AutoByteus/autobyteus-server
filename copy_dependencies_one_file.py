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

def get_nuitka_include_arguments():
    """
    Generate Nuitka include arguments for essential data files only.
    Returns a list of Nuitka include arguments.
    """
    include_args = []
    
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
    
    # Find autobyteus_llm_client certificates directory
    llm_client_certs_path = find_autobyteus_llm_client_certificates()
    if llm_client_certs_path:
        # Include the entire certificates directory
        include_args.append(f"--include-data-dir={llm_client_certs_path}=autobyteus_llm_client/certificates")
    
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
