# -*- mode: python ; coding: utf-8 -*-
import os
from PyInstaller.utils.hooks import collect_data_files

# Define the root directory for relative paths
root_dir = os.path.abspath(os.path.join(os.path.dirname('__file__'), '..'))

# Get the latest version from version file or use a default version
version_file = os.path.join(root_dir, 'build', 'version_info.txt')
if os.path.exists(version_file):
    with open(version_file, 'r') as f:
        version_data = f.read().strip()
else:
    # Create a default version info if the file doesn't exist
    version_data = """
    VSVersionInfo(
      ffi=FixedFileInfo(
        filevers=(1, 0, 0, 0),
        prodvers=(1, 0, 0, 0),
        mask=0x3f,
        flags=0x0,
        OS=0x40004,
        fileType=0x1,
        subtype=0x0,
        date=(0, 0)
      ),
      kids=[
        StringFileInfo([
          StringTable(
            u'040904B0',
            [StringStruct(u'CompanyName', u''),
             StringStruct(u'FileDescription', u'TaskMover Window Management Tool'),
             StringStruct(u'FileVersion', u'1.0.0'),
             StringStruct(u'InternalName', u'TaskMover'),
             StringStruct(u'LegalCopyright', u''),
             StringStruct(u'OriginalFilename', u'TaskMover.exe'),
             StringStruct(u'ProductName', u'TaskMover'),
             StringStruct(u'ProductVersion', u'1.0.0')])
        ]),
        VarFileInfo([VarStruct(u'Translation', [1033, 1200])])
      ]
    )
    """
    # Write default version info
    os.makedirs(os.path.dirname(version_file), exist_ok=True)
    with open(version_file, 'w') as f:
        f.write(version_data)

# Define application data files to include
datas = []

# Add any config files or resources
settings_path = os.path.join(root_dir, 'settings.yml')
if os.path.exists(settings_path):
    datas.append((settings_path, '.'))

# Define the analysis phase
a = Analysis(
    [os.path.join(root_dir, 'taskmover', '__main__.py')],
    pathex=[root_dir],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'tkinter',
        'ttkbootstrap',
        'yaml',
        'colorlog',
        'taskmover',
        'taskmover.ui',
        'taskmover.ui.theme_manager',
        'taskmover.ui.input_components',
        'taskmover.ui.display_components',
        'taskmover.ui.layout_components',
        'taskmover.ui.navigation_components',
        'taskmover.ui.data_display_components',
        'taskmover.ui.dialog_components',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=['pytest', 'black', 'flake8', 'mypy'],
    noarchive=False,
    optimize=2,
)

# Create the pyz archive
pyz = PYZ(a.pure)

# Create the executable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='TaskMover',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=os.path.join(root_dir, 'build', 'icon.ico') if os.path.exists(os.path.join(root_dir, 'build', 'icon.ico')) else None,
    version=version_file if os.path.exists(version_file) else None,
)
