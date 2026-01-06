# Auto Point Picker - Implementation Plan

## Executive Summary

This document outlines the implementation plan for a Python script that transforms survey/detection data from `Final_Report.csv` into two separate coordinate files: `Auto Picked Top.csv` and `Auto Picked Bottom.csv`. The transformation involves extracting relevant columns, converting data types, swapping coordinate order (X,Y → Y,X), and handling detection status.

---

## 1. Architecture Overview

### 1.1 Design Philosophy
- **Single Responsibility**: One script, one purpose - transform and split coordinate data
- **Minimal Dependencies**: Use pandas for robust CSV handling and vectorized operations
- **Fail-Fast**: Validate input early, provide clear error messages
- **Idempotent**: Running the script multiple times produces identical results

### 1.2 Data Flow
```
Final_Report.csv
       │
       ▼
┌──────────────────┐
│  Read & Validate │
│    Input CSV     │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  Transform Data  │
│  - UPN: float→int│
│  - Swap X↔Y      │
│  - Handle zeros  │
└────────┬─────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌───────┐
│ Top   │ │Bottom │
│ CSV   │ │ CSV   │
└───────┘ └───────┘
```

---

## 2. Implementation Modules

### 2.1 Module Structure
```
auto_point_picker/
├── point_picker.py      # Main script (single file implementation)
└── (input/output CSVs)  # Data files in same directory
```

Given the simplicity of this task, a single-file implementation is appropriate. No need for over-engineering with multiple modules.

---

## 3. Detailed Implementation Steps

### Step 1: Input Handling

**Objective**: Read and validate the input CSV file

**Implementation Details**:
1. Use `pandas.read_csv()` with explicit dtype handling
2. Validate required columns exist:
   - `UPN`
   - `Detected`
   - `Top_X`, `Top_Y`, `Top_Z`
   - `Bot_X`, `Bot_Y`, `Bot_Z`
3. Log row count for verification

**Error Handling**:
- FileNotFoundError → Clear message pointing to expected location
- Missing columns → List which columns are absent
- Empty file → Informative error message

**Validation Criteria**:
- All 7 required columns present
- File is not empty
- Data types can be coerced correctly

---

### Step 2: Data Type Conversion

**Objective**: Convert UPN from float to integer format

**Implementation Details**:
1. Cast `UPN` column: `df['UPN'].astype(int)`
2. This handles the `30306.0` → `30306` conversion

**Edge Case Considerations**:
- NaN values in UPN column → Must handle before int conversion
- Already integer values → Should work transparently
- Negative UPNs → Allow (no business rule against them stated)

**Critical Note**: The `astype(int)` call will fail if NaN values exist. Must either:
- Drop rows with NaN UPN (data quality issue)
- Fill with sentinel value (not recommended)
- Raise descriptive error

---

### Step 3: Coordinate Extraction with Order Swap

**Objective**: Extract coordinates in Y, X, Z order (not X, Y, Z)

**Implementation Details**:

For Top coordinates:
```
Source columns: Top_X, Top_Y, Top_Z
Output order:   Top_Y, Top_X, Top_Z  (Y first!)
```

For Bottom coordinates:
```
Source columns: Bot_X, Bot_Y, Bot_Z
Output order:   Bot_Y, Bot_X, Bot_Z  (Y first!)
```

**Critical**: This coordinate swap is essential for downstream system compatibility. The research explicitly flags this as a key requirement.

---

### Step 4: Detection Status Handling

**Objective**: Set coordinates to 0 for non-detected points

**Implementation Details**:
1. Identify rows where `Detected == False`
2. For these rows, set all coordinate values to `0`
3. Preserve `0` as integer (not `0.0`) for cleaner output

**Logic Matrix**:
| Detected | Top Coords | Bot Coords |
|----------|------------|------------|
| True     | Actual     | Actual     |
| False    | 0, 0, 0    | 0, 0, 0    |

**Implementation Approach** (two options):

Option A - Conditional Assignment:
- Create output DataFrames
- Use `np.where()` or pandas conditional to set values

Option B - Boolean Masking:
- Create mask for non-detected rows
- Apply mask to set zeros in batch

Recommend Option A for clarity and maintainability.

---

### Step 5: Output Formatting

**Objective**: Write two CSV files with correct format

**Output File 1**: `Auto Picked Top.csv`
- Columns: `UPN`, `Top_Y`, `Top_X`, `Top_Z`
- Note: Column headers should match this exact naming

**Output File 2**: `Auto Picked Bottom.csv`
- Columns: `UPN`, `Bot_Y`, `Bot_X`, `Bot_Z`

**Formatting Requirements**:
1. No index column in output (`index=False`)
2. Preserve floating point precision for detected points
3. Zero values as `0` not `0.0`
4. Spaces in filenames are intentional and required

**Precision Handling**:
Based on the research examples, the output shows:
- High precision for Y coordinates (full precision)
- Slightly rounded X coordinates (~3 decimal places in examples)
- Variable precision for Z coordinates

Recommend: Do NOT explicitly round. Let pandas handle float → string conversion naturally. The minor differences in the examples may be artifacts of the original generation process.

---

### Step 6: Zero Formatting Challenge

**Objective**: Output `0` instead of `0.0` for non-detected points

**Problem**: Pandas will write `0.0` for float columns

**Solution Options**:

Option A - Mixed dtypes (Not Recommended):
- Convert to object dtype for mixed int/float
- Results in messy code and potential issues

Option B - Post-processing string conversion (Not Recommended):
- Convert to string and replace
- Fragile and hacky

Option C - Separate handling (Recommended):
- Create output DataFrames with detected points having float values
- For non-detected rows, explicitly set integer 0
- Use `to_csv` with `float_format` parameter or convert column-wise

Option D - Accept minor difference:
- Output `0.0` and document as known difference
- Most pragmatic if downstream system accepts both

**Recommended Approach**: Option C with the following technique:
1. Create separate DataFrames for detected and non-detected
2. Format non-detected with integer zeros
3. Concatenate and sort by original index
4. Write output

Actually, simpler approach: Convert the entire coordinate columns to strings with custom formatting that removes trailing `.0` from zeros.

---

## 4. Algorithm Pseudocode

```
FUNCTION process_final_report(input_path, output_dir):

    # Step 1: Read input
    df = read_csv(input_path)
    validate_columns(df, required=['UPN','Detected','Top_X','Top_Y','Top_Z','Bot_X','Bot_Y','Bot_Z'])

    # Step 2: Convert UPN
    df['UPN'] = df['UPN'].astype(int)

    # Step 3: Create output DataFrames
    # Note the column order: Y before X
    top_df = DataFrame({
        'UPN': df['UPN'],
        'Top_Y': df['Top_Y'],   # Y first
        'Top_X': df['Top_X'],   # X second
        'Top_Z': df['Top_Z']
    })

    bot_df = DataFrame({
        'UPN': df['UPN'],
        'Bot_Y': df['Bot_Y'],   # Y first
        'Bot_X': df['Bot_X'],   # X second
        'Bot_Z': df['Bot_Z']
    })

    # Step 4: Handle non-detected (coordinates already 0.0 in source)
    # The source data already has 0.0 for non-detected points
    # We just need to format them as 0 instead of 0.0

    # Step 5: Format and write output
    FOR each (output_df, filename) in [(top_df, 'Auto Picked Top.csv'),
                                        (bot_df, 'Auto Picked Bottom.csv')]:
        format_zeros(output_df)  # Convert 0.0 to 0
        write_csv(output_df, output_dir / filename, index=False)

    # Step 6: Validation
    verify_row_counts(input=df, top=top_df, bot=bot_df)

    RETURN success
```

---

## 5. Edge Cases & Error Handling

### 5.1 Input Validation Errors
| Condition | Action |
|-----------|--------|
| File not found | Raise FileNotFoundError with path |
| Missing columns | List missing columns in error message |
| Empty file | Raise ValueError("Input file is empty") |
| NaN in UPN | Raise ValueError with row numbers |

### 5.2 Data Quality Issues
| Condition | Action |
|-----------|--------|
| Detected=True but coords=0 | Log warning, process as-is |
| Detected=False but coords≠0 | Log warning, process as-is |
| Unexpected Detected values | Raise ValueError |
| Extremely large coordinates | Process as-is (valid survey data) |

### 5.3 Output Issues
| Condition | Action |
|-----------|--------|
| Output file exists | Overwrite (standard behavior) |
| Cannot write to directory | Raise PermissionError |
| Disk full | Let OS exception propagate |

---

## 6. Testing Strategy

### 6.1 Unit Tests
1. **UPN Conversion**: Verify `30306.0` → `30306`
2. **Column Ordering**: Verify Y, X, Z order in output
3. **Zero Handling**: Verify non-detected points show `0,0,0`
4. **Row Preservation**: Verify all rows present in output

### 6.2 Integration Tests
1. Process full `Final_Report.csv`
2. Compare output against known-good examples from research
3. Verify row counts match

### 6.3 Manual Validation Checklist
- [ ] Open output in Excel/text editor
- [ ] Spot-check detected point UPN against original
- [ ] Verify coordinate values match (with Y,X swap)
- [ ] Confirm non-detected points show `0,0,0`
- [ ] Count rows in output vs input

---

## 7. Configuration & Parameters

### 7.1 Configurable Elements
| Parameter | Default | Description |
|-----------|---------|-------------|
| `input_file` | `Final_Report.csv` | Input filename |
| `output_dir` | `.` (current dir) | Output directory |
| `top_output` | `Auto Picked Top.csv` | Top output filename |
| `bot_output` | `Auto Picked Bottom.csv` | Bottom output filename |

### 7.2 Command Line Interface
Recommend simple CLI:
```bash
python point_picker.py                          # Use defaults
python point_picker.py --input path/to/file.csv # Custom input
python point_picker.py --output-dir /output/    # Custom output location
```

Use `argparse` for CLI parsing.

---

## 8. Performance Considerations

### 8.1 Expected Performance
- ~1,300 rows: Trivial for pandas (<1 second)
- Memory: ~1-2 MB for DataFrame in memory
- No optimization needed for this data size

### 8.2 Scalability Notes
If future files are significantly larger (100K+ rows):
- Consider chunked reading with `chunksize` parameter
- Process in batches and append to output
- For current requirements: not necessary

---

## 9. Dependencies

### 9.1 Required
- **Python**: 3.8+ (for modern type hints, f-strings)
- **pandas**: 1.0+ (core data handling)

### 9.2 Optional
- **argparse**: Standard library (CLI)
- **pathlib**: Standard library (file paths)

### 9.3 Installation
```bash
pip install pandas
```

Or with requirements.txt:
```
pandas>=1.0.0
```

---

## 10. Deliverables

1. **`point_picker.py`**: Main script with all functionality
2. **Output files**: Generated when script runs
   - `Auto Picked Top.csv`
   - `Auto Picked Bottom.csv`

---

## 11. Success Criteria

The implementation is complete when:

1. ✅ Script reads `Final_Report.csv` without errors
2. ✅ UPN values are integers (no decimal points)
3. ✅ Output columns are in Y, X, Z order
4. ✅ Non-detected points show `0,0,0` (not `0.0,0.0,0.0`)
5. ✅ Output row count matches input row count
6. ✅ Detected point coordinates match source (with precision)
7. ✅ Output filenames are exactly `Auto Picked Top.csv` and `Auto Picked Bottom.csv`
8. ✅ Script handles missing file gracefully with clear error
9. ✅ Script runs in <5 seconds for expected data size

---

## 12. Open Questions / Assumptions

### Assumptions Made:
1. **Input file is always in same directory as script** (can be made configurable)
2. **Output files should be in same directory** (can be made configurable)
3. **Overwriting existing output files is acceptable**
4. **Boolean 'Detected' column uses Python True/False** (not 'TRUE'/'FALSE' strings)
5. **All coordinate values are valid floats** (no text/special values)

### Questions for Stakeholder (if needed):
1. Should the script log its progress to console or be silent?
2. Is there a preferred precision for coordinate output?
3. Should output files be overwritten without confirmation?
4. Are there any header row variations in input files?

---

## 13. Implementation Sequence

### Phase 1: Core Implementation
1. Create basic script structure with imports
2. Implement CSV reading with validation
3. Implement UPN conversion
4. Implement coordinate extraction with Y,X swap
5. Implement output writing

### Phase 2: Refinement
6. Add zero formatting (0 vs 0.0)
7. Add error handling for all edge cases
8. Add CLI argument parsing

### Phase 3: Validation
9. Test with actual Final_Report.csv
10. Compare outputs against research examples
11. Manual verification of edge cases

---

## Appendix A: Column Mapping Reference

### Input → Output Mapping

**Top Output File**:
| Output Column | Source Column | Transformation |
|---------------|---------------|----------------|
| UPN | UPN | float → int |
| Top_Y | Top_Y | direct (position 1) |
| Top_X | Top_X | direct (position 2) |
| Top_Z | Top_Z | direct (position 3) |

**Bottom Output File**:
| Output Column | Source Column | Transformation |
|---------------|---------------|----------------|
| UPN | UPN | float → int |
| Bot_Y | Bot_Y | direct (position 1) |
| Bot_X | Bot_X | direct (position 2) |
| Bot_Z | Bot_Z | direct (position 3) |

---

## Appendix B: Sample Data Reference

### Detected Point (from Research)
```
Input:  UPN=30306.0, Top_X=2261441.747839, Top_Y=365873.99755900004, Top_Z=903.10699188
Output: 30306,365873.99755900004,2261441.748,903.1069919
        (UPN, Top_Y, Top_X, Top_Z)
```

### Non-Detected Point (from Research)
```
Input:  UPN=13132.0, Detected=False, all coords=0.0
Output: 13132,0,0,0
```

---

*Plan Version: 1.0*
*Created: Based on RESEARCH.md analysis*
