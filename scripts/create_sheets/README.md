# Attendance Sheet Generator

Creates attendance sheets for specific sections by filtering students from the input Excel file.

## Usage

```bash
python create_attendance_sheet.py <sheet_name> <section1> <section2> ...
```

## Examples

Generate attendance sheet for section A1 from sampleInput.xlsx:
```bash
python create_attendance_sheet.py sampleInput A1
```

Generate attendance sheet for multiple sections from AI-Students.xlsx:
```bash
python create_attendance_sheet.py AI-Students A1 A2 B1
```

Generate attendance sheet for all sections in a group from AS-Students.xlsx:
```bash
python create_attendance_sheet.py AS-Students A1 A2 A3 A4
```

## Input

- **Location**: `input/<sheet_name>.xlsx`
- **Format**: Excel file with multiple sheets (Group A, Group B, etc.)
- **Required columns**: ID, Name, Section

## Output

- **Location**: `output/attendance_<sections>.xlsx`
- **Format**: Matches `sampleOutput.xlsx` exactly
  - Headers: ID, Name, Section, Week 1-10
  - Blue header background (#0F45A8)
  - White header text
  - Frozen first row
  - Proper column widths

## Examples

```bash
# Single section from sampleInput.xlsx
python create_attendance_sheet.py sampleInput A1
# Output: output/attendance_A1.xlsx

# Multiple sections from AI-Students.xlsx
python create_attendance_sheet.py AI-Students A1 A2 B1
# Output: output/attendance_A1_A2_B1.xlsx
```

## Requirements

```bash
pip install pandas openpyxl
```

## Notes

- Section codes are case-sensitive (use A1, not a1)
- Students are automatically sorted by Section, then by ID
- The script searches all sheets in the input file
- Empty week columns are ready for attendance marking
