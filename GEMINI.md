# Auto Point Picker

## Project Overview

"Auto Point Picker" is a Python-based automation tool designed to process survey/detection data. Its primary function is to transform a comprehensive report (`Final_Report.csv`) into two specialized coordinate files (`Auto Picked Top.csv` and `Auto Picked Bottom.csv`).

The tool performs critical data transformations including:
*   **Type Conversion:** Converting Unique Point Numbers (UPN) from float to integer.
*   **Coordinate Reordering:** Swapping standard (X, Y, Z) coordinates to (Y, X, Z) format as required by downstream systems.
*   **Data Cleaning:** Handling non-detected points by standardizing their coordinates to integer `0` (instead of `0.0`).

## Architecture & Key Files

The project follows a simple, single-script architecture:

*   **`point_picker.py`**: The core application logic. It handles CSV reading, validation, transformation, and output generation.
*   **`Final_Report.csv`**: The source input file containing raw survey data.
*   **`Auto Picked Top.csv`** & **`Auto Picked Bottom.csv`**: The generated output files.
*   **`PLAN.md`**, **`RESEARCH.md`**, **`LOG.md`**: Project documentation covering requirements, research notes, and implementation history.

## Building and Running

The project is set up with a Python virtual environment (`venv`).

### Prerequisites
*   Python 3.8+
*   `pandas` library (installed in the virtual environment)

### Execution

To run the tool using the default input/output settings:

```bash
# Activate the virtual environment (if not already active)
source venv/bin/activate

# Run the script
python point_picker.py
```

### CLI Options

The script supports custom input and output paths:

```bash
# Specify a different input file
python point_picker.py --input path/to/data.csv

# Specify a different output directory
python point_picker.py --output-dir /path/to/output/
```

## Development Conventions

*   **Code Style:** Follows standard Python (PEP 8) conventions.
*   **Type Hinting:** Uses Python type hints for function arguments and return values.
*   **Error Handling:** Implements "fail-fast" validation. The script verifies input file integrity (required columns, data types) before processing.
*   **Data Integrity:** 
    *   Preserves full floating-point precision for detected points.
    *   Explicitly formats non-detected points as `0` to distinguish them from measured `0.0` values.
    *   Output files do not include an index column.
