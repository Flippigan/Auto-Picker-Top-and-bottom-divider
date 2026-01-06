# Windows EXE Build Process: Debrief & Guide

## 1. The High-Level Goal
We successfully turned your Python script (`point_picker.py`) into a standalone Windows application (`TopAndBottomSplitter.exe`). This means a user on Windows can just double-click the file to run it—no Python installation, no command line, and no dependency setup required.

## 2. How It Works (The "Magic")
Since you use a Mac, you cannot build a Windows `.exe` directly on your laptop. We utilized **GitHub Actions** to solve this.

### The Concept: "Continuous Integration" (CI)
We set up a robot in the cloud that watches your repository.
1.  **The Trigger:** Every time you `git push` changes to the `main` branch, the robot wakes up.
2.  **The Environment:** GitHub creates a fresh, temporary **Windows Virtual Machine** just for you.
3.  **The Action:** This virtual machine downloads your code, installs Python, installs your libraries (`pandas`, `numpy`), and runs the build command.
4.  **The Result:** It uploads the finished `.exe` file back to GitHub for you to download.

## 3. Answering Your Key Question
**"Will this happen every time I push to this repo now?"**

**YES.**
Currently, the configuration file `.github/workflows/build_windows.yml` is set to trigger on **any push to the `main` branch**.

```yaml
on:
  push:
    branches: [ "main", "master" ]
```

### Is this bad?
*   **Pros:** You always have an up-to-date `.exe` that matches your latest code. You catch bugs early (if the build fails, you know you broke something).
*   **Cons:** It uses "GitHub Actions Minutes" (you get 2,000 free minutes/month on a free account, which is plenty for this).

### How to Change This
If you don't want it running every time, you can modify `.github/workflows/build_windows.yml`:
*   **Option A (Manual Only):** Change `on: push` to `on: workflow_dispatch`. This means it only runs when you click a "Run" button in the Actions tab.
*   **Option B (Tags Only):** Change it to only run when you tag a release (e.g., `v1.0`).

## 4. Key Files Explained
You now have three files that control this entire process.

1.  **`.github/workflows/build_windows.yml` (The Instructions)**
    *   This is the script the GitHub robot reads. It says: "Get a Windows computer, install Python 3.x, install requirements.txt, run PyInstaller, and save the output."
    
2.  **`point_picker.spec` (The Blueprint)**
    *   This file tells **PyInstaller** specifically how to build your app.
    *   It defines the name (`TopAndBottomSplitter`), that it should be a single file (`onefile`), and that it needs a console window (`console=True`).
    
3.  **`requirements.txt` (The Ingredients)**
    *   The build server uses this to know which libraries to package inside the `.exe`. If you add a new library (like `scipy` or `openpyxl`), you **must** add it here, or the build will fail.

## 5. How to Get Your File
1.  Go to your repository on GitHub.
2.  Click the **Actions** tab.
3.  Click on the latest run (e.g., "Build Windows EXE").
4.  Scroll down to **Artifacts**.
5.  Download **TopAndBottomSplitter-Windows**.

## 6. Maintenance & Future Proofing
*   **Adding Libraries:** If you `pip install` something new locally, run `pip freeze > requirements.txt` and push that change. The next build will automatically include it.
*   **Changing the Icon:** You can add an `.ico` file to the repo and update `point_picker.spec` (e.g., `icon='my_icon.ico'`) to give your app a custom logo.
*   **Renaming:** If you want to rename the app again, you edit `point_picker.spec` (the `name=` part) and the workflow file (the `path=` part).

## 7. Summary
You have built a professional-grade "Release Pipeline." You develop on your Mac, push to the cloud, and GitHub handles the complex work of compiling for Windows automatically.
