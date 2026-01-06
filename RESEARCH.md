# Auto Point Picker - Research & Analysis

## Overview
The task is to create a script that transforms survey/detection data from a single comprehensive report into two separate files containing top and bottom point coordinates.

## Data Structure Analysis

### Input File: Final_Report.csv
**Columns:**
- `UPN` - Unique Point Number (float format: 30306.0, 44864.0, etc.)
- `Detected` - Boolean flag (True/False) indicating if the point was successfully detected
- `Pile_Height` - Height measurement between top and bottom points
- `Top_X`, `Top_Y`, `Top_Z` - Top point coordinates (X, Y, Z)
- `Bot_X`, `Bot_Y`, `Bot_Z` - Bottom point coordinates (X, Y, Z)
- Additional metadata columns (Lean_East_Deg, Lean_North_Deg, Tracker_Slope_Pct, etc.)

**Key Observations:**
- When `Detected=True`: All coordinate fields contain valid measurements
- When `Detected=False`: All numeric fields are 0.0
- Contains approximately 1,342+ rows (based on output file lengths)
- Coordinates use large numeric values (X: ~2261000, Y: ~365000, Z: ~890-903)

### Output File 1: Auto Picked Top.csv
**Columns:** `UPN, Top_Y, Top_X, Top_Z`

**Format Notes:**
- UPN is converted from float (30306.0) to integer (30306)
- **Coordinate order is Y, X, Z (not X, Y, Z)**
- Values appear to be rounded/formatted to fewer decimal places
- Rows with Detected=False show as: `UPN,0,0,0`

### Output File 2: Auto Picked Bottom.csv
**Columns:** `UPN, Bot_Y, Bot_X, Bot_Z`

**Format Notes:**
- Same UPN conversion (float to int)
- **Coordinate order is Y, X, Z (not X, Y, Z)**
- Values are rounded/formatted similarly to Top file
- Rows with Detected=False show as: `UPN,0,0,0`

## Transformation Logic

### Core Processing Steps:
1. **Read Input CSV**
   - Load Final_Report.csv using pandas or csv module
   - Parse all columns, paying attention to data types

2. **Filter/Process Each Row**
   - Check the `Detected` column
   - If `Detected == True`:
     - Extract Top coordinates: Top_X, Top_Y, Top_Z
     - Extract Bottom coordinates: Bot_X, Bot_Y, Bot_Z
   - If `Detected == False`:
     - Set all coordinates to 0

3. **Format UPN**
   - Convert from float (30306.0) to integer (30306)
   - Remove decimal point for cleaner output

4. **Handle Coordinate Order**
   - **CRITICAL:** Output format is Y, X, Z (not X, Y, Z)
   - This is an unusual convention but matches the example outputs exactly
   - Must swap X and Y when writing output

5. **Write Output Files**
   - Create Auto Picked Top.csv with columns: UPN, Top_Y, Top_X, Top_Z
   - Create Auto Picked Bottom.csv with columns: UPN, Bot_Y, Bot_X, Bot_Z
   - Maintain row order from input file
   - Include ALL rows (both detected and non-detected)

## Data Examples

### Example: Detected Point (UPN 30306)
**Input:**
```
UPN: 30306.0
Detected: True
Top_X: 2261441.747839
Top_Y: 365873.99755900004
Top_Z: 903.10699188
Bot_X: 2261441.73225
Bot_Y: 365873.982426
Bot_Z: 898.9435199999999
```

**Output Top:**
```
30306,365873.99755900004,2261441.748,903.1069919
(Format: UPN, Top_Y, Top_X, Top_Z)
```

**Output Bottom:**
```
30306,365873.9824,2261441.732,898.9435199999999
(Format: UPN, Bot_Y, Bot_X, Bot_Z)
```

### Example: Non-Detected Point (UPN 13132)
**Input:**
```
UPN: 13132.0
Detected: False
All coordinates: 0.0
```

**Output Top & Bottom:**
```
13132,0,0,0
```

## Technical Considerations

### Data Quality
- Some rows have very precise coordinates (10+ decimal places)
- Output appears to preserve most precision, with minor rounding
- Zero values must remain as exactly 0 (not 0.0)

### Performance
- Large file (~1,300+ rows, 17 columns)
- Should process efficiently using pandas for vectorized operations
- Alternative: csv module for row-by-row processing (more memory efficient)

### Edge Cases to Handle
1. **Missing or malformed data**: Ensure graceful handling of unexpected values
2. **Floating point precision**: Match output precision to examples
3. **Column order**: Critical to maintain Y, X, Z output order
4. **UPN format**: Must convert float to int cleanly

## Recommended Implementation Approach

### Option 1: Pandas (Recommended for Simplicity)
**Pros:**
- Clean, readable code
- Built-in CSV handling
- Easy column selection and renaming
- Vectorized operations for speed

**Cons:**
- Higher memory usage for large files
- Additional dependency

### Option 2: Native CSV Module
**Pros:**
- No external dependencies
- Lower memory footprint
- Row-by-row processing

**Cons:**
- More verbose code
- Manual data type handling

### Recommended: Pandas Implementation
```python
import pandas as pd

# Pseudocode outline:
1. df = pd.read_csv('Final_Report.csv')
2. df['UPN'] = df['UPN'].astype(int)
3. Create top_df with columns: UPN, Top_Y, Top_X, Top_Z
4. Create bot_df with columns: UPN, Bot_Y, Bot_X, Bot_Z
5. Apply conditional: if not Detected, set coords to 0
6. Write to CSV without index
```

## Validation Checklist
- [ ] UPN format: integers without decimal points
- [ ] Coordinate order: Y, X, Z (not X, Y, Z)
- [ ] Non-detected points: show as 0,0,0
- [ ] Row count matches input file
- [ ] Row order preserved from input
- [ ] All detected points have non-zero coordinates
- [ ] Precision/rounding matches example outputs

## Naming Convention
- Input: `Final_Report.csv`
- Output 1: `Auto Picked Top.csv`
- Output 2: `Auto Picked Bottom.csv`
- Note: Output files have spaces in names

## Summary
The "auto point picking" is essentially a data extraction and formatting task. The script filters based on the `Detected` flag and reformats the coordinate data into two separate files, one for top points and one for bottom points. The key technical detail is the coordinate order swap (Y before X) in the output format, which must be preserved for compatibility with downstream systems.
