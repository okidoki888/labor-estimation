# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller спецификация для приложения «Расчёт трудоёмкости разработки ПС»
"""

import sys
from pathlib import Path

block_cipher = None

# Путь к проекту
project_path = Path(SPECPATH)

a = Analysis(
    ['main.py'],
    pathex=[str(project_path)],
    binaries=[],
    datas=[
        ('app/resources', 'app/resources'),
    ],
    hiddenimports=[
        'PySide6.QtWidgets',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'matplotlib',
        'matplotlib.backends.backend_qtagg',
        'openpyxl',
        'docx',
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

if sys.platform == 'darwin':
    # macOS: onedir + .app bundle (рекомендуется PyInstaller)
    exe = EXE(
        pyz,
        a.scripts,
        [],
        exclude_binaries=True,
        name='LabLaborEstimation',
        debug=False,
        bootloader_ignore_signals=False,
        strip=False,
        upx=True,
        console=False,
        argv_emulation=False,
        target_arch=None,
        codesign_identity=None,
        entitlements_file=None,
    )
    coll = COLLECT(
        exe,
        a.binaries,
        a.zipfiles,
        a.datas,
        strip=False,
        upx=True,
        upx_exclude=[],
        name='LabLaborEstimation',
    )
    app = BUNDLE(
        coll,
        name='LabLaborEstimation.app',
        icon=None,
        bundle_identifier='ru.sut.lablorestimation',
    )
else:
    # Windows и Linux: onefile (один исполняемый файл)
    exe = EXE(
        pyz,
        a.scripts,
        a.binaries,
        a.zipfiles,
        a.datas,
        [],
        name='LabLaborEstimation',
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
    )
