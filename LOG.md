# Auto Point Picker - Implementation Log

## Implementation Summary

**Date:** 2026-01-06
**Status:** Complete
**Script:** `point_picker.py`

---

## Progress Notes

### Phase 1: Core Implementation

1. **Created script structure with imports**
   - Used `pandas` for CSV handling and data manipulation
   - Used `argparse` for CLI interface
   - Used `pathlib` for cross-platform path handling

2. **Implemented CSV reading with validation**
   - Validates all 7 required columns exist: `UPN`, `Detected`, `Top_X`, `Top_Y`, `Top_Z`, `Bot_X`, `Bot_Y`, `Bot_Z`
   - Checks for empty files
   - Detects NaN values in UPN column before conversion

3. **Implemented UPN conversion**
   - Converts float UPN (e.g., `30306.0`) to integer (`30306`)
   - Uses `astype(int)` after NaN validation

4. **Implemented coordinate extraction with Y,X swap**
   - Output column order: `UPN`, `Y`, `X`, `Z` (not X,Y,Z)
   - Creates separate DataFrames for Top and Bottom coordinates

5. **Implemented detection status handling**
   - Non-detected points (`Detected=False`) output as `0,0,0`
   - Uses string formatting to ensure `0` not `0.0`

6. **Implemented zero formatting**
   - Custom `format_coordinate()` function returns `'0'` for non-detected points
   - Preserves full precision for detected points using `:.15g` format

7. **Added CLI argument parsing**
   - `--input` / `-i`: Custom input file path
   - `--output-dir` / `-o`: Custom output directory
   - Defaults work out of the box

---

## Roadblocks Encountered

### 1. Zero Formatting (0 vs 0.0)

**Problem:** Pandas writes `0.0` for float columns, but the output requires `0` for non-detected points.

**Solution:** Instead of relying on pandas dtypes, I implemented row-by-row processing with a `format_coordinate()` function that:
- Returns the string `'0'` for non-detected points
- Returns the full precision float as a string for detected points

This approach creates string columns in the output DataFrame, which write cleanly to CSV without the `.0` suffix.

### 2. Coordinate Order Swap

**Problem:** Input has X, Y, Z order but output requires Y, X, Z order.

**Solution:** When building the output DataFrames, explicitly select columns in Y, X, Z order:
```python
{
    'UPN': row['UPN'],
    'Top_Y': format_coordinate(row['Top_Y'], detected),  # Y first
    'Top_X': format_coordinate(row['Top_X'], detected),  # X second
    'Top_Z': format_coordinate(row['Top_Z'], detected)
}
```

### 3. NaN Handling in UPN

**Problem:** `astype(int)` fails if NaN values exist in the column.

**Solution:** Added pre-validation that checks for NaN values and raises a descriptive error with row numbers before attempting conversion.

### 4. Precision Preservation

**Problem:** How much precision to preserve for coordinate values?

**Solution:** Used Python's `:.15g` format specifier which:
- Preserves up to 15 significant digits
- Automatically removes trailing zeros
- Handles both large and small numbers appropriately

---

## Design Decisions

1. **Single-file implementation** - Given the simplicity of the task, all code is in one file (`point_picker.py`) rather than a package structure.

2. **Row-by-row processing** - While pandas vectorized operations are faster, row-by-row iteration was chosen for clarity and to handle the zero formatting requirement cleanly.

3. **String-based coordinate columns** - Output coordinates are stored as strings to ensure proper formatting (especially for zeros).

4. **Fail-fast validation** - All input validation happens at the start before any processing begins.

5. **Warning logs for data quality** - The script logs warnings (but doesn't fail) if:
   - Detected points have zero coordinates
   - Non-detected points have non-zero coordinates

---

## Usage

```bash
# Default usage (expects Final_Report.csv in current directory)
python point_picker.py

# Custom input file
python point_picker.py --input /path/to/Final_Report.csv

# Custom output directory
python point_picker.py --output-dir /path/to/output/

# Both custom
python point_picker.py -i input.csv -o /output/
```

---

## Output Files

| File | Columns |
|------|---------|
| `Auto Picked Top.csv` | `UPN`, `Top_Y`, `Top_X`, `Top_Z` |
| `Auto Picked Bottom.csv` | `UPN`, `Bot_Y`, `Bot_X`, `Bot_Z` |

---

## Testing Notes

**Test Run:** 2026-01-06

Successfully processed `Final_Report.csv`:
- Input: 1340 rows, 17 columns
- Detected points: 352
- Non-detected points: 988
- Output files generated: `Auto Picked Top.csv`, `Auto Picked Bottom.csv`

**Manual testing checklist:**
- [x] Run with actual `Final_Report.csv`
- [x] Verify UPN values are integers (e.g., `30306` not `30306.0`)
- [x] Verify coordinate order is Y, X, Z (columns: `Top_Y`, `Top_X`, `Top_Z`)
- [x] Verify non-detected points show `0,0,0` (e.g., UPN 13132, 13118)
- [x] Verify row counts match input (1340 rows in both outputs)
- [x] Compare sample detected points against expected values

**Sample Output Verification:**

Top file (first detected row):
```
UPN,Top_Y,Top_X,Top_Z
30306,365873.997559,2261441.747839,903.10699188
```

Bottom file (first detected row):
```
UPN,Bot_Y,Bot_X,Bot_Z
30306,365873.982426,2261441.73225,898.94352
```

Non-detected rows correctly show zeros:
```
13132,0,0,0
13118,0,0,0
```

---

## Dependencies

```
pandas>=1.0.0
```

Install with:
```bash
pip install pandas
```

---

## Files Created

- `point_picker.py` - Main implementation script
- `LOG.md` - This implementation log
