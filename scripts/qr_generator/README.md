# QR Code Generator for Student Attendance

Generate QR codes for students with automatic organization by Sheet/Group/Section.

## Features

- ✅ Supports Excel (.xlsx, .xls) and CSV files
- ✅ Handles Arabic text in names
- ✅ Automatic directory organization (Sheet/Group/Section)
- ✅ QR codes contain "Name - ID" format
- ✅ Visual footer with name and ID

## Directory Structure

```
qr_generator/
├── generate_qr.py          # Main script
├── requirements.txt        # Dependencies
├── input/                  # Place your files here
│   ├── AI.xlsx
│   ├── AS-B7.xlsx
│   └── Logic_sheet.csv
└── output/                 # Generated QR codes
    ├── AI/
    │   ├── Tab1/           # First tab in Excel file
    │   │   ├── A1/
    │   │   │   ├── 20210001.png
    │   │   │   └── 20210002.png
    │   │   ├── A2/
    │   │   └── B1/
    │   └── Tab2/           # Second tab in Excel file
    │       └── ...
    └── AS-B7/
        └── ...
```

## File Format

Your Excel/CSV files must have these columns:

| ID       | Name          | Section |
|----------|---------------|---------|
| 20210001 | Ahmed Mohamed | A1      |
| 20210002 | Sara Ali      | A2      |
| 20210003 | أحمد محمد     | B1      |

**Required Columns:**
- `ID` or `Student_ID` - Student identifier
- `Name` - Student name (supports Arabic)
- `Section` - Section code (e.g., A1, A2, B1)

**Note:** CSV files should be saved with UTF-8 encoding for Arabic support.

## Installation

```bash
pip install -r requirements.txt
```

## Usage

### Basic Usage

```bash
python generate_qr.py <sheet_name>
```

### Examples

```bash
# Generate QR codes for AI.xlsx
python generate_qr.py AI

# Generate QR codes for AS-B7.xlsx
python generate_qr.py AS-B7

# Generate QR codes for Logic_sheet.csv
python generate_qr.py Logic_sheet
```

**Note:** Don't include the file extension - the script will find it automatically.

## Output Organization

QR codes are automatically organized in this hierarchy:

```
output/
└── SheetName/          # Name of your input file (without extension)
    └── TabName/        # Name of the tab/sheet (for Excel files with multiple tabs)
        └── Section/    # Section code (A1, A2, B1, etc.)
            └── ID.png  # QR code file named by student ID
```

### Example

For a student with:
- Sheet: `AI`
- Tab: `Section A`
- Section: `A5`
- ID: `20210001`

The QR code will be saved to:
```
output/AI/Section A/A5/20210001.png
```

### Multi-Tab Excel Files

If your Excel file has multiple tabs (e.g., "Section A", "Section B"), the script will:
1. Automatically detect all tabs
2. Process each tab separately
3. Organize output by tab name

Example output structure:
```
output/AI/
├── Section A/
│   ├── A1/
│   ├── A2/
│   └── B1/
└── Section B/
    ├── A1/
    └── B1/
```

## QR Code Content

Each QR code contains:
```
Name - ID
```

Example:
```
Ahmed Mohamed - 20210001
```

The frontend app will parse this and display the name in the scanned list.

## Troubleshooting

### "File not found in input directory"
- Make sure your file is in the `input/` directory
- Check the file name matches what you're typing
- Don't include the file extension in the command

### "Missing required column"
- Ensure your file has `ID` (or `Student_ID`), `Name`, and `Section` columns
- Column names are case-sensitive

### "Error reading file"
- For CSV files: Save with UTF-8 encoding
- For Excel files: Make sure the file isn't password-protected
- Install openpyxl: `pip install openpyxl`

### Arabic text not displaying correctly
- Install fonts that support Arabic (DejaVu, Liberation, Noto)
- For CSV files: Ensure UTF-8 encoding

## Requirements

- Python 3.7+
- pandas
- qrcode
- Pillow
- openpyxl (for Excel support)

See `requirements.txt` for specific versions.
