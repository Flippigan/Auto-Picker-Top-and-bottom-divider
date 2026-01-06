# Windows Executable (EXE) Guide

## Overview
This document explains the "Containerization" feature which converts your Python script (`point_picker.py`) into a standalone Windows application (`AutoPointPicker.exe`).

## What is happening?
Normally, to run your script, a user needs:
1.  Python installed on their computer.
2.  All dependencies installed (`pandas`, `numpy`, etc.).
3.  Knowledge of how to run terminal commands.

We are creating a **"frozen"** executable. This bundles your script, the Python interpreter (the engine), and all required libraries into a single file. This allows any Windows user to run the tool immediately, even on a fresh computer with nothing installed.

## The Tool: PyInstaller
We use a standard industry tool called **PyInstaller**.
-   **Analysis:** It reads your code to find every library you use (like `pandas`).
-   **Bundling:** It copies those libraries and a mini-Python runtime into a package.
-   **Bootloader:** It adds a small Windows program that launches this internal environment when you double-click the `.exe`.

## The Challenge: Cross-Compilation
Since you are working on **macOS**, you cannot directly build a Windows `.exe` on your laptop. PyInstaller only builds for the operating system it is running on.

## The Solution: GitHub Actions
We have set up an automated "Build Pipeline" to handle this for you.

1.  **Trigger:** Whenever you push code to GitHub (`git push`), the pipeline wakes up.
2.  **Virtual Machine:** GitHub creates a temporary, fresh **Windows** virtual machine in the cloud.
3.  **Installation:** It installs Python and your dependencies (`requirements.txt`) on that Windows machine.
4.  **Build:** It runs PyInstaller using the configuration in `point_picker.spec`.
5.  **Delivery:** It saves the resulting `AutoPointPicker.exe` as an **Artifact**.

## How to Download Your EXE
1.  Go to your repository on **GitHub.com**.
2.  Click the **Actions** tab at the top.
3.  Click on the most recent "Build Windows EXE" run in the list.
4.  Scroll down to the **Artifacts** section.
5.  Click **AutoPointPicker-Windows** to download a zip file containing your `.exe`.

## Files We Added
-   `point_picker.spec`: The configuration file telling PyInstaller how to build the app (name, console settings, etc.).
-   `.github/workflows/build_windows.yml`: The instruction manual for the GitHub robot explaining how to build the app on Windows.
