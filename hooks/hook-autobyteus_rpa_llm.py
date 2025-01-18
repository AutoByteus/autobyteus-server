from PyInstaller.utils.hooks import collect_data_files, collect_submodules, collect_all, copy_metadata

# Collect all package data
datas, binaries, hiddenimports = collect_all('autobyteus_rpa_llm')

# Collect package metadata for plugin discovery
datas += copy_metadata('autobyteus_rpa_llm')
datas += copy_metadata('autobyteus')

# Add direct plugin import
hiddenimports.extend([
    'autobyteus_rpa_llm.llm.factory.rpa_llm_factory'
])
