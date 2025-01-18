from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_all, copy_metadata

# Collect all package data
datas, binaries, hiddenimports = collect_all('brui_core')

# Explicitly collect the config.toml file
additional_datas = collect_data_files(
    'brui_core',
    includes=['**/config.toml']
)
datas.extend(additional_datas)

# Collect package metadata for plugin discovery
datas += copy_metadata('brui_core')

# Force include all submodules
hiddenimports += collect_submodules('brui_core')

# Add all dependencies from setup.py as hidden imports
hiddenimports.extend([
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
    'Pillow',
])
