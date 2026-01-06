#!/usr/bin/env python3
"""
Top and Bottom Splitter - Transform survey/detection data into coordinate files.

Reads Final_Report.csv and generates two output files:
- Auto Picked Top.csv (UPN, Top_Y, Top_X, Top_Z)
- Auto Picked Bottom.csv (UPN, Bot_Y, Bot_X, Bot_Z)

Key transformations:
- UPN: float -> int
- Coordinates: X,Y,Z -> Y,X,Z order
- Non-detected points: all coordinates set to 0
"""

import argparse
import sys
import threading
from pathlib import Path

import pandas as pd

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, scrolledtext
    GUI_AVAILABLE = True
except ImportError:
    GUI_AVAILABLE = False


class RedirectText:
    """Redirects stdout/stderr to a tkinter Text widget."""
    def __init__(self, text_widget):
        self.output = text_widget

    def write(self, string):
        if not GUI_AVAILABLE:
            return
        self.output.insert(tk.END, string)
        self.output.see(tk.END)

    def flush(self):
        pass


# Required columns in the input file
REQUIRED_COLUMNS = [
    'UPN',
    'Detected',
    'Top_X', 'Top_Y', 'Top_Z',
    'Bot_X', 'Bot_Y', 'Bot_Z'
]


def validate_input(df: pd.DataFrame, filepath: Path) -> None:
    """Validate the input DataFrame has required columns and data."""
    if df.empty:
        raise ValueError(f"Input file is empty: {filepath}")

    missing_cols = [col for col in REQUIRED_COLUMNS if col not in df.columns]
    if missing_cols:
        raise ValueError(
            f"Missing required columns: {', '.join(missing_cols)}\n"
            f"Found columns: {', '.join(df.columns)}"
        )

    # Check for NaN values in UPN column
    nan_upn_rows = df[df['UPN'].isna()].index.tolist()
    if nan_upn_rows:
        raise ValueError(
            f"NaN values found in UPN column at rows: {nan_upn_rows[:10]}"
            f"{'...' if len(nan_upn_rows) > 10 else ''}"
        )


def format_coordinate(value: float, detected: bool) -> str:
    """Format coordinate value, returning '0' for non-detected points."""
    if not detected:
        return '0'
    # Preserve full precision for detected points
    # Remove unnecessary trailing zeros while keeping precision
    formatted = f"{value:.15g}"
    return formatted


def process_report(input_path: Path, output_dir: Path) -> dict:
    """
    Process Final_Report.csv and generate output files.

    Args:
        input_path: Path to Final_Report.csv
        output_dir: Directory for output files

    Returns:
        dict with processing statistics
    """
    # Step 1: Read input
    print(f"Reading input file: {input_path}")
    df = pd.read_csv(input_path)

    # Validate input
    validate_input(df, input_path)
    print(f"Input validated: {len(df)} rows, {len(df.columns)} columns")

    # Step 2: Convert UPN to integer
    df['UPN'] = df['UPN'].astype(int)

    # Filter out rows where Top_Z or Bot_Z is zero
    initial_count = len(df)
    df = df[(df['Top_Z'] != 0) & (df['Bot_Z'] != 0)]
    removed_count = initial_count - len(df)
    if removed_count > 0:
        print(f"Removed {removed_count} rows containing zero values in Top_Z or Bot_Z columns.")

    # Step 3 & 4: Create output DataFrames with coordinate swap (Y, X, Z order)
    # and handle detection status

    # Process Top coordinates
    top_data = []
    for _, row in df.iterrows():
        detected = row['Detected']
        top_data.append({
            'UPN': row['UPN'],
            'Top_Y': format_coordinate(row['Top_Y'], detected),
            'Top_X': format_coordinate(row['Top_X'], detected),
            'Top_Z': format_coordinate(row['Top_Z'], detected)
        })
    top_df = pd.DataFrame(top_data)

    # Process Bottom coordinates
    bot_data = []
    for _, row in df.iterrows():
        detected = row['Detected']
        bot_data.append({
            'UPN': row['UPN'],
            'Bot_Y': format_coordinate(row['Bot_Y'], detected),
            'Bot_X': format_coordinate(row['Bot_X'], detected),
            'Bot_Z': format_coordinate(row['Bot_Z'], detected)
        })
    bot_df = pd.DataFrame(bot_data)

    # Step 5: Write output files
    top_output = output_dir / 'Auto Picked Top.csv'
    bot_output = output_dir / 'Auto Picked Bottom.csv'

    top_df.to_csv(top_output, index=False)
    print(f"Written: {top_output} ({len(top_df)} rows)")

    bot_df.to_csv(bot_output, index=False)
    print(f"Written: {bot_output} ({len(bot_df)} rows)")

    # Step 6: Verification
    stats = {
        'input_rows': len(df),
        'top_output_rows': len(top_df),
        'bot_output_rows': len(bot_df),
        'detected_count': df['Detected'].sum(),
        'non_detected_count': (~df['Detected']).sum()
    }

    # Log data quality warnings
    detected_but_zero = df[
        (df['Detected'] == True) &
        ((df['Top_X'] == 0) | (df['Top_Y'] == 0) | (df['Top_Z'] == 0))
    ]
    if not detected_but_zero.empty:
        print(f"Warning: {len(detected_but_zero)} rows have Detected=True but zero coordinates")

    non_detected_but_coords = df[
        (df['Detected'] == False) &
        ((df['Top_X'] != 0) | (df['Top_Y'] != 0) | (df['Top_Z'] != 0))
    ]
    if not non_detected_but_coords.empty:
        print(f"Warning: {len(non_detected_but_coords)} rows have Detected=False but non-zero coordinates")

    return stats


def run_gui():
    """Launch the Tkinter GUI."""
    root = tk.Tk()
    root.title("Top and Bottom Splitter")
    root.geometry("600x400")

    # State variables
    input_path_var = tk.StringVar(value="No file selected")
    selected_file_path = None

    def browse_file():
        nonlocal selected_file_path
        filename = filedialog.askopenfilename(
            title="Select Input CSV",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")]
        )
        if filename:
            selected_file_path = Path(filename)
            input_path_var.set(selected_file_path.name)
            log_area.insert(tk.END, f"Selected: {selected_file_path}\n")

    def start_processing():
        if not selected_file_path:
            messagebox.showwarning("Warning", "Please select an input file first.")
            return

        # Disable buttons during processing
        btn_process.config(state=tk.DISABLED)
        btn_browse.config(state=tk.DISABLED)
        log_area.insert(tk.END, "-" * 40 + "\n")
        log_area.insert(tk.END, "Starting processing...\n")

        def task():
            try:
                # Redirect stdout/stderr
                old_stdout = sys.stdout
                old_stderr = sys.stderr
                sys.stdout = RedirectText(log_area)
                sys.stderr = RedirectText(log_area)

                output_dir = selected_file_path.parent
                stats = process_report(selected_file_path, output_dir)

                sys.stdout = old_stdout
                sys.stderr = old_stderr

                root.after(0, lambda: messagebox.showinfo(
                    "Success", 
                    f"Processing Complete!\n\n"
                    f"Top Output: {stats['top_output_rows']} rows\n"
                    f"Bottom Output: {stats['bot_output_rows']} rows\n\n"
                    f"Files saved in: {output_dir}"
                ))

            except Exception as e:
                sys.stdout = old_stdout
                sys.stderr = old_stderr
                root.after(0, lambda: messagebox.showerror("Error", str(e)))
            finally:
                root.after(0, lambda: btn_process.config(state=tk.NORMAL))
                root.after(0, lambda: btn_browse.config(state=tk.NORMAL))

        threading.Thread(target=task, daemon=True).start()

    # GUI Layout
    frame_top = tk.Frame(root, padx=10, pady=10)
    frame_top.pack(fill=tk.X)

    tk.Label(frame_top, text="Input File:").pack(side=tk.LEFT)
    lbl_file = tk.Label(frame_top, textvariable=input_path_var, fg="blue", width=30, anchor="w")
    lbl_file.pack(side=tk.LEFT, padx=10)

    btn_browse = tk.Button(frame_top, text="Browse...", command=browse_file)
    btn_browse.pack(side=tk.LEFT)

    frame_mid = tk.Frame(root, padx=10, pady=5)
    frame_mid.pack(fill=tk.X)
    
    btn_process = tk.Button(frame_mid, text="Process File", command=start_processing, bg="#dddddd", height=2)
    btn_process.pack(fill=tk.X)

    frame_log = tk.Frame(root, padx=10, pady=10)
    frame_log.pack(fill=tk.BOTH, expand=True)

    tk.Label(frame_log, text="Log Output:").pack(anchor="w")
    log_area = scrolledtext.ScrolledText(frame_log, height=10)
    log_area.pack(fill=tk.BOTH, expand=True)

    root.mainloop()


def main():
    """Main entry point. Launches GUI if no args provided, else CLI."""
    # Check if arguments were provided (excluding script name)
    if len(sys.argv) == 1:
        if GUI_AVAILABLE:
            run_gui()
        else:
            print("Error: Tkinter not installed. GUI unavailable.", file=sys.stderr)
            print("Please provide command line arguments.", file=sys.stderr)
            print("Use --help for usage instructions.", file=sys.stderr)
            sys.exit(1)
        return

    parser = argparse.ArgumentParser(
        description='Transform Final_Report.csv into coordinate output files.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python point_picker.py                          # Use defaults
  python point_picker.py --input path/to/file.csv # Custom input
  python point_picker.py --output-dir /output/    # Custom output location
        """
    )

    parser.add_argument(
        '--input', '-i',
        type=Path,
        default=Path('Final_Report.csv'),
        help='Input CSV file (default: Final_Report.csv)'
    )

    parser.add_argument(
        '--output-dir', '-o',
        type=Path,
        default=Path('.'),
        help='Output directory (default: current directory)'
    )

    args = parser.parse_args()

    # Validate input file exists
    if not args.input.exists():
        print(f"Error: Input file not found: {args.input}", file=sys.stderr)
        print(f"Expected location: {args.input.absolute()}", file=sys.stderr)
        sys.exit(1)

    # Validate output directory
    if not args.output_dir.exists():
        print(f"Error: Output directory does not exist: {args.output_dir}", file=sys.stderr)
        sys.exit(1)

    try:
        stats = process_report(args.input, args.output_dir)
        print("\nProcessing complete!")
        print(f"  Input rows: {stats['input_rows']}")
        print(f"  Detected: {stats['detected_count']}")
        print(f"  Non-detected: {stats['non_detected_count']}")
        print(f"  Top output: {stats['top_output_rows']} rows")
        print(f"  Bottom output: {stats['bot_output_rows']} rows")

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
    except pd.errors.EmptyDataError:
        print(f"Error: Input file is empty or corrupted", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
