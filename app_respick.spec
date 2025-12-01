# -*- mode: python ; coding: utf-8 -*-


a = Analysis(
    ['app_respick.py'],
    pathex=[],
    binaries=[],
    datas=[('img/respick_dcdc.svg', 'img'), ('icons/respick_splash.png', 'icons')],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='app_respick',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['icons/icon.icns'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='app_respick',
)
app = BUNDLE(
    coll,
    name='app_respick.app',
    icon='icons/icon.icns',
    bundle_identifier=None,
)
