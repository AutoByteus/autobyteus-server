import json
import logging
import os
import platform
import sys
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

def normalize_path(path):
    """
    Normalize path for the current platform.
    
    Windows Git Bash has issues with paths, this function helps fix them.
    """
    # Convert to Path object for cross-platform handling
    path_obj = Path(path)
    
    # Get normalized path as string
    if platform.system() == "Windows":
        # On Windows, ensure forward slashes for Nuitka
        return str(path_obj).replace("\\", "/")
    else:
        # On Linux/macOS, use the path as is
        return str(path_obj)

# Find required data and config files
dependency_args = []

# Check for Playwright driver script
try:
    import playwright._impl._driver
    playwright_driver_dir = os.path.dirname(playwright._impl._driver.__file__)
    playwright_sh = os.path.join(playwright_driver_dir, "playwright.sh")
    
    if os.path.exists(playwright_sh):
        playwright_sh_path = normalize_path(playwright_sh)
        dependency_args.append(f"--include-data-file={playwright_sh_path}=playwright/_impl/_driver/playwright.sh")
        logging.info(f"Found playwright.sh: {playwright_sh_path}")
    else:
        logging.error(f"playwright.sh script not found in playwright driver folder.")
except ImportError:
    logging.warning("Playwright module not found, skipping playwright.sh inclusion.")

# Check for mistral_common data
try:
    import mistral_common
    mistral_data_dir = os.path.join(os.path.dirname(mistral_common.__file__), "data")
    
    if os.path.exists(mistral_data_dir) and os.path.isdir(mistral_data_dir):
        mistral_data_path = normalize_path(mistral_data_dir)
        dependency_args.append(f"--include-data-dir={mistral_data_path}=mistral_common/data")
        logging.info(f"Found mistral_common data folder: {mistral_data_path}")
    else:
        logging.warning("mistral_common data directory not found.")
except ImportError:
    logging.warning("mistral_common module not found, skipping data inclusion.")

# Check for Anthropic tokenizer
try:
    import anthropic
    anthropic_dir = os.path.dirname(anthropic.__file__)
    tokenizer_path = os.path.join(anthropic_dir, "tokenizer.json")
    
    if os.path.exists(tokenizer_path):
        tokenizer_path = normalize_path(tokenizer_path)
        dependency_args.append(f"--include-data-file={tokenizer_path}=anthropic/tokenizer.json")
        logging.info(f"Found Anthropic tokenizer.json: {tokenizer_path}")
    else:
        logging.warning("Anthropic tokenizer.json not found.")
except ImportError:
    logging.warning("Anthropic module not found, skipping tokenizer inclusion.")

# Check for autobyteus_llm_client certificates
try:
    import autobyteus_llm_client
    cert_dir = os.path.join(os.path.dirname(autobyteus_llm_client.__file__), "certificates")
    
    if os.path.exists(cert_dir) and os.path.isdir(cert_dir):
        cert_dir_path = normalize_path(cert_dir)
        dependency_args.append(f"--include-data-dir={cert_dir_path}=autobyteus_llm_client/certificates")
        logging.info(f"Found autobyteus_llm_client certificates directory: {cert_dir_path}")
    else:
        logging.warning("autobyteus_llm_client certificates directory not found.")
except ImportError:
    logging.warning("autobyteus_llm_client module not found, skipping certificates inclusion.")

# Find workflow step prompts in autobyteus_server
workflow_step_dirs = []
workflow_base_dir = os.path.join("autobyteus_server", "workflow", "steps")

if os.path.exists(workflow_base_dir):
    step_folders = os.listdir(workflow_base_dir)
    prompt_count = 0
    
    for step_folder in step_folders:
        prompt_dir = os.path.join(workflow_base_dir, step_folder, "prompt")
        
        if os.path.exists(prompt_dir) and os.path.isdir(prompt_dir):
            prompt_dir_path = normalize_path(prompt_dir)
            # For workflow step prompts, keep the full path structure
            include_path = f"autobyteus_server/workflow/steps/{step_folder}/prompt"
            dependency_args.append(f"--include-data-dir={prompt_dir_path}={include_path}")
            logging.info(f"Found workflow step prompt directory: {prompt_dir} -> {include_path}")
            prompt_count += 1
    
    logging.info(f"Found {prompt_count} workflow step prompt directories.")

# Output NUITKA_DEPENDENCY_ARGS that can be captured by the build script
print(f"NUITKA_DEPENDENCY_ARGS={json.dumps(dependency_args)}")
