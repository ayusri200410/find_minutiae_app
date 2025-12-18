# -*- mode: python ; coding: utf-8 -*-
import os, cv2
from PyInstaller.utils.hooks import collect_submodules

hiddenimports = []
hiddenimports += collect_submodules('tensorflow')
hiddenimports += collect_submodules('tensorflow.keras')
hiddenimports += collect_submodules('keras_applications')
hiddenimports += collect_submodules('keras_preprocessing')
hiddenimports += collect_submodules('cv2')
hiddenimports += collect_submodules('PIL')

cv2_dir = os.path.dirname(cv2.__file__)

datas = [
    ('models', 'models'),
    ('assets', 'assets'),
    ('components', 'components'),
    ('pages', 'pages'),
    ('images_for_models', 'images_for_models'),
    (os.path.join(cv2_dir, 'config.py'), 'cv2'),
    (os.path.join(cv2_dir, 'config-3.py'), 'cv2'),
]

a = Analysis(
    ['main.py'],
    pathex=[os.getcwd()],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='FindMinutiaeApp',
    console=True,   # SEMENTARA TRUE UNTUK DEBUG
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    name='FindMinutiaeApp'
)
