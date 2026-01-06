# Implementation Plan: Windows Executable Containerization

## Objective
Generate a standalone Windows executable (`.exe`) for `point_picker.py` using GitHub Actions to cross-compile from a macOS development environment.

## Phase 1: Configuration & Prerequisites

### 1. Verify Dependencies
- [x] Check `requirements.txt` for `pandas` and `numpy`. (Verified)

### 2. Create PyInstaller Spec File
Create `point_picker.spec` in the root directory to define build settings.
*Note: While PyInstaller usually generates this, creating it manually allows us to version control build settings like console visibility and file bundles.*

**Draft Content for `point_picker.spec`:**
```python
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['point_picker.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=[],
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
    name='AutoPointPicker',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
```

## Phase 2: Automation (GitHub Actions)

### 3. Create Workflow File
Create `.github/workflows/build_windows.yml`.

**Draft Content:**
- **Trigger:** Push to `main` or manual dispatch.
- **OS:** `windows-latest`.
- **Steps:**
    1. Checkout code.
    2. Set up Python 3.11 (stable).
    3. Install dependencies (`pip install -r requirements.txt`).
    4. Install PyInstaller (`pip install pyinstaller`).
    5. Run Build: `pyinstaller point_picker.spec --clean`.
    6. Upload Artifact: Upload `dist/AutoPointPicker.exe`.

## Phase 3: Execution & Verification

### 4. Deploy & Test
1. Commit and push `point_picker.spec` and `.github/workflows/build_windows.yml`.
2. Monitor the "Actions" tab in GitHub.
3. Download the resulting artifact.
4. (Optional) User verifies the `.exe` on a Windows machine.
