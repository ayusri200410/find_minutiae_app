# -*- mode: python ; coding: utf-8 -*-

import os
import cv2
from PyInstaller.utils.hooks import collect_submodules

project_dir = os.path.abspath('.')

# --- Hidden imports ---
hiddenimports = []
hiddenimports += collect_submodules('tensorflow')
hiddenimports += collect_submodules('tensorflow.keras')
hiddenimports += collect_submodules('keras_applications')
hiddenimports += collect_submodules('keras_preprocessing')
hiddenimports += collect_submodules('cv2')
hiddenimports += collect_submodules('PIL')


# --- OpenCV config fix ---
cv2_dir = os.path.dirname(cv2.__file__)
datas = [
    (os.path.join(cv2_dir, 'config.py'), 'cv2'),
    (os.path.join(cv2_dir, 'config-3.py'), 'cv2'),
]

# --- Project assets ---
datas += [
    ('assets', 'assets'),
    ('components', 'components'),
    ('pages', 'pages'),
    ('models', 'models'),
    ('images_for_models', 'images_for_models'),
    ('data_kasus', 'data_kasus'),
]

block_cipher = None

a = Analysis(
    ['main.py'],
    pathex=[project_dir],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FindMinutiaeApp',
    console=False,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='FindMinutiaeApp'
)
