from PyInstaller.utils.hooks import collect_data_files, collect_submodules

# Collect all submodules
hiddenimports = collect_submodules('mistral_common')

# Collect all data files
datas = collect_data_files('mistral_common', include_py_files=True)
