# -*- mode: python ; coding: utf-8 -*-
from PyInstaller.utils.hooks import collect_data_files, collect_submodules
import os
from pathlib import Path

block_cipher = None

# Ensure the logs directory exists
if not os.path.exists('logs'):
    os.makedirs('logs')

# Ensure the resources directory exists
if not os.path.exists('resources'):
    os.makedirs('resources')

def collect_step_prompts():
    """Collect all prompt files from steps directory maintaining the nested structure"""
    base_path = Path('autobyteus_server/workflow/steps')
    prompt_files = []
    
    if base_path.exists():
        for root, _, files in os.walk(str(base_path)):
            for file in files:
                if file.endswith('.prompt'):
                    source_path = os.path.join(root, file)
                    rel_path = os.path.relpath(root, start='.')
                    prompt_files.append((source_path, rel_path))
                    
    return prompt_files

# Collect tokenizer data files
mistral_datas = collect_data_files('mistral_common', include_py_files=True)
anthropic_datas = collect_data_files('anthropic', include_py_files=True)

# Add brui-core data files with explicit config.toml inclusion
brui_core_datas = collect_data_files('brui_core', include_py_files=True)
brui_core_datas.extend(collect_data_files('brui_core', includes=['**/config.toml']))

hidden_imports = [
    # Uvicorn imports
    'uvicorn.logging',
    'uvicorn.loops.auto',
    'uvicorn.protocols.http.auto',
    'uvicorn.protocols.websockets.auto',
    'uvicorn.lifespan.on',
    
    # Application imports
    'autobyteus_server.loader',
    
    # LLM-related imports
    'mistral_common',
    'mistral_common.tokens.tokenizers.mistral',
    'anthropic',
    'tiktoken',
    'tokenizers',
    
    # Add missing hidden import
    'tiktoken_ext.openai_public',
    
    # Force include brui-core
    'brui_core',
    'brui_core.ui_integrator',
    'pyperclip',
    'pytest_playwright',
    'playwright',
    'playwright.async_api',
    'playwright.sync_api',
    'pytest_playwright.pytest_playwright',
    'toml',
    'pytest_asyncio',
    'colorama',
    'Pillow'
]

# Combine all data files
base_datas = [
    ('logging_config.ini', '.'),
    ('alembic.ini', '.'),
    ('alembic', 'alembic'),
    ('.env', '.'),
    ('resources', 'resources'),
    ('logs', 'logs'),
]

datas = (
    base_datas + 
    collect_data_files('autobyteus_server') + 
    collect_step_prompts() + 
    mistral_datas + 
    anthropic_datas +
    brui_core_datas
)

a = Analysis(
    ['autobyteus_server/cli.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=hidden_imports,
    hookspath=['hooks'],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='autobyteus-server',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
