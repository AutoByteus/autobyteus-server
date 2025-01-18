from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all submodules
hiddenimports = collect_submodules('anthropic')

# Collect all data files
datas = collect_data_files('anthropic', include_py_files=True)

# Add tiktoken as a hidden import since anthropic uses it
hiddenimports.append('tiktoken')
