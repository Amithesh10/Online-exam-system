# exam_portal.spec
# Build: pyinstaller exam_portal.spec --clean

import os

# Use absolute path for icon to ensure PyInstaller finds it
PROJECT_DIR = os.path.dirname(os.path.abspath(SPEC))
ICON_PATH = os.path.join(PROJECT_DIR, 'exam_icon.ico')

block_cipher = None

a = Analysis(
    ['app.py'],
    pathex=[PROJECT_DIR],
    binaries=[],
    datas=[
        ('templates',      'templates'),
        ('questions.json', '.'),
        ('users.json',     '.'),
    ],
    hiddenimports=[
        'flask',
        'jinja2',
        'werkzeug',
        'werkzeug.serving',
        'werkzeug.debug',
        'webview',
        'webview.platforms.winforms',
        'clr',
        'threading',
        'multiprocessing',
        'subprocess',
        'tempfile',
        'shutil',
        're',
        'encodings',
        'encodings.utf_8',
        'encodings.cp1252',
    ],
    hookspath=[],
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
    name='ExamPortal',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='C:\Amithesh\My works\PycharmProjects\python-project\exam_icon.ico',
)
