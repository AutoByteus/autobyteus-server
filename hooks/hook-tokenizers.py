from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all submodules
hiddenimports = collect_submodules('tokenizers')

# Collect all data files
datas = collect_data_files('tokenizers', include_py_files=True)
