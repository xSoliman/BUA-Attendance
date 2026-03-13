# QR Generator Script Update - Summary

## Changes Made

Updated the QR generator script to use a simplified workflow with automatic organization.

## New Features

### 1. Input Directory Structure
- Script now reads from `input/` directory (beside the script)
- Just provide the sheet name, no need for full path
- Automatically detects file extension (.xlsx, .xls, .csv)

### 2. Section Column Support
- Now parses sheets with structure: `ID`, `Name`, `Section`
- Section is used for organization only (not included in QR code)
- QR code still contains: "Name - ID"

### 3. Hierarchical Output Organization
- Output organized as: `SheetName/Group/Section/`
- Group is automatically extracted from section (e.g., A1 → A, B5 → B)
- Example: `output/AI/A/A5/20210001.png`

## Usage

### Before (Old Way)
```bash
python generate_qr.py /path/to/file.xlsx
```

### After (New Way)
```bash
# Just provide the sheet name
python generate_qr.py AI
python generate_qr.py AS-B7
python generate_qr.py Logic_sheet
```

## Directory Structure

```
qr_generator/
├── generate_qr.py
├── requirements.txt
├── README.md
├── input/              # NEW: Place files here
│   ├── AI.xlsx
│   ├── AS-B7.xlsx
│   └── Logic_sheet.csv
└── output/             # NEW: Hierarchical organization
    ├── AI/
    │   ├── A/
    │   │   ├── A1/
    │   │   │   ├── 20210001.png
    │   │   │   └── 20210002.png
    │   │   └── A2/
    │   └── B/
    │       └── B1/
    └── AS-B7/
        └── ...
```

## File Format

Required columns in Excel/CSV:

| ID       | Name          | Section |
|----------|---------------|---------|
| 20210001 | Ahmed Mohamed | A1      |
| 20210002 | Sara Ali      | A2      |
| 20210003 | أحمد محمد     | B1      |

**Column Requirements:**
- `ID` or `Student_ID` - Student identifier
- `Name` - Student name (supports Arabic)
- `Section` - Section code for organization (e.g., A1, A2, B1)

## Output Organization Logic

### Group Extraction
The script automatically extracts the group letter from the section:
- `A1` → Group: `A`, Section: `A1`
- `A5` → Group: `A`, Section: `A5`
- `B1` → Group: `B`, Section: `B1`
- `B10` → Group: `B`, Section: `B10`

### Output Path
For a student with:
- Sheet: `AI`
- Section: `A5`
- ID: `20210001`

Output: `output/AI/A/A5/20210001.png`

## QR Code Content

QR codes still contain the same format:
```
Name - ID
```

Example:
```
Ahmed Mohamed - 20210001
```

The Section is NOT included in the QR code - it's only used for file organization.

## Key Improvements

1. **Simpler Usage**: Just type the sheet name, no paths needed
2. **Better Organization**: Automatic hierarchy by Sheet/Group/Section
3. **Section Support**: Handles the Section column for organization
4. **Auto-Detection**: Finds files automatically in input directory
5. **Clear Errors**: Better error messages with available files list
6. **Arabic Support**: Full UTF-8 support for Arabic names
7. **Flexible Columns**: Supports both `ID` and `Student_ID`

## Migration Steps

1. Create `input/` directory beside the script
2. Move your Excel/CSV files to `input/`
3. Ensure files have `ID`, `Name`, `Section` columns
4. Run with just the sheet name: `python generate_qr.py AI`

## Example Workflow

```bash
# 1. Place files in input directory
cp AI.xlsx input/
cp AS-B7.xlsx input/

# 2. Generate QR codes
python generate_qr.py AI
python generate_qr.py AS-B7

# 3. Find organized output
ls output/AI/A/A1/
# 20210001.png
# 20210002.png
```

## Files Modified
- `scripts/qr_generator/generate_qr.py` - Complete rewrite with new structure
- `scripts/qr_generator/requirements.txt` - Added openpyxl for Excel support
- `scripts/qr_generator/README.md` - NEW: Comprehensive documentation

## Status
✅ COMPLETE - QR generator now uses input directory with hierarchical output organization
