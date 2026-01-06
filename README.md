# Top and Bottom Splitter

A Python automation tool designed to process survey detection reports. It reads a `Final_Report.csv` file and generates specialized coordinate files for top and bottom points, ensuring correct data formatting and coordinate ordering for downstream systems.

## Features

- **Automated Processing:** Instantly transforms raw survey data into usable coordinate files.
- **Coordinate Reordering:** Automatically swaps coordinates from (X, Y, Z) to the required (Y, X, Z) format.
- **Data Cleaning:** 
  - Converts Unique Point Numbers (UPN) to integers.
  - Standardizes non-detected points to `0` (instead of `0.0`).
  - Preserves full precision for detected points.
- **Verification:** Validates input data integrity before processing.

## Prerequisites

- Python 3.8 or higher
- `pandas` library

## Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd "Auto Point Picker"
   ```

2. **Set up a virtual environment (recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt # Install the libraries from the list
   ```

   

## Usage

### Basic Usage
Place your `Final_Report.csv` in the project directory and run:

```bash
python point_picker.py
```

This will generate `Auto Picked Top.csv` and `Auto Picked Bottom.csv` in the same directory.

### Advanced Usage

You can specify custom input files and output directories:

```bash
# Specify a different input file
python point_picker.py --input /path/to/my_data.csv

# Specify a custom output directory
python point_picker.py --output-dir /path/to/results/

# Combine options
python point_picker.py -i data/report.csv -o output/
```

## File Formats

### Input: `Final_Report.csv`
Must contain the following columns:
- `UPN` (Unique Point Number)
- `Detected` (Boolean: True/False)
- `Top_X`, `Top_Y`, `Top_Z`
- `Bot_X`, `Bot_Y`, `Bot_Z`

### Output Files

**1. `Auto Picked Top.csv`**
- Columns: `UPN`, `Top_Y`, `Top_X`, `Top_Z`
- Format: Y coordinate comes before X.

**2. `Auto Picked Bottom.csv`**
- Columns: `UPN`, `Bot_Y`, `Bot_X`, `Bot_Z`
- Format: Y coordinate comes before X.

**Note:** For points where `Detected` is `False`, all coordinates will be set to `0`.

## Building for Windows

This project includes configuration to build a standalone `.exe` file for Windows users, eliminating the need to install Python.

### Automated Build (GitHub Actions)
Every push to the `main` branch automatically triggers a build.
1. Go to the "Actions" tab in the GitHub repository.
2. Click on the latest workflow run.
3. Download the `AutoPointPicker-Windows` artifact.

### Manual Build (Windows Only)
If you are on a Windows machine:
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```
2. Run the build command:
   ```bash
   pyinstaller point_picker.spec
   ```
3. The executable will be in the `dist/` folder.