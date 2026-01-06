# Research: Windows Executable Containerization

## 1. Objective
Create a standalone Windows executable (`.exe`) for the `point_picker.py` application. This allows users on Windows to run the tool without installing Python or dependencies (`pandas`, `numpy`, etc.).

## 2. Current State & Constraints
- **Source Script:** `point_picker.py` (CLI-based).
- **Dependencies:** `pandas`, `numpy`, and standard libraries.
- **Current Environment:** macOS (Darwin).
- **Challenge:** PyInstaller (and similar tools) are **not cross-compilers**. Running PyInstaller on macOS generates a macOS executable (Mach-O), not a Windows `.exe`.

## 3. Recommended Approaches

### Approach A: GitHub Actions (Best for Automation)
Use a CI/CD pipeline to automatically build the `.exe` whenever code is pushed. This is the most robust solution as it uses a clean, native Windows environment provided by GitHub.

**Workflow:**
1. Push code to GitHub.
2. A `.github/workflows/build.yml` script triggers.
3. It spins up a `windows-latest` runner.
4. Installs Python, pip, and dependencies.
5. Runs PyInstaller.
6. Uploads the resulting `.exe` as a downloadable artifact.

**Pros:** No Windows machine required locally; reproducible builds; consistent environment.
**Cons:** Requires the code to be hosted on GitHub (or similar CI provider).

### Approach B: Manual Build on Windows (Simplest if Windows is available)
If you have access to a Windows machine or VM (Parallels, VMWare, VirtualBox):

1. Copy the project to the Windows machine.
2. Install Python.
3. Run: `pip install -r requirements.txt`.
4. Run: `pip install pyinstaller`.
5. Run: `pyinstaller --onefile point_picker.py`.

### Approach C: Docker + Wine (Complex/Fallback)
It is possible to use a Docker container running Linux + Wine to cross-compile for Windows.

**Pros:** Can run on macOS.
**Cons:** High complexity; `pandas` and `numpy` (C-extensions) can sometimes cause stability issues in Wine environments; large Docker image download.

## 4. Implementation Details (PyInstaller)

Regardless of *where* we run the build (Local Windows or GitHub Actions), **PyInstaller** is the tool of choice.

### Configuration
We should use a `.spec` file to define the build configuration.

**Key Flags:**
- `--onefile`: Bundles everything into a single `.exe` file (easier for distribution).
- `--name AutoPointPicker`: Sets the output name.
- `--console`: Keeps the command line window open (Crucial: this is a CLI tool).

### Estimated File Size
Due to `pandas` and `numpy`, the resulting `.exe` will likely be large (approx. 50MB - 100MB). This is normal as it includes the entire Python interpreter and the heavy data science libraries.

## 5. Next Steps Plan

1. **Create `point_picker.spec`**: Define the build settings locally.
2. **Create GitHub Action Workflow**: Set up `.github/workflows/build_windows.yml` to automate the build.
3. **Verify**: Push changes and download the artifact from GitHub Actions to test on a Windows machine.
