# Attendance Sheet Generator

Creates attendance sheets for specific sections by filtering students from the input Excel file.

## Usage

```bash
python create_attendance_sheet.py <input_sheet> <output_name> <section1> <section2> ...
```

## Examples

Generate attendance sheet for section A1 from sampleInput.xlsx:
```bash
python create_attendance_sheet.py sampleInput "Attendance Sheet" A1
```

Generate attendance sheet for multiple sections from AI-Students.xlsx:
```bash
python create_attendance_sheet.py AI-Students "Logic Design" A1 A2 B1
```

Generate attendance sheet for all sections in a group from AS-Students.xlsx:
```bash
python create_attendance_sheet.py AS-Students "Data Structures" A1 A2 A3 A4
```

## Input

- **Location**: `input/<input_sheet>.xlsx`
- **Format**: Excel file with multiple sheets (Group A, Group B, etc.)
- **Required columns**: ID, Name, Section

## Output

- **Location**: `output/<output_name>.xlsx`
- **Format**: Matches `sampleOutput.xlsx` exactly
  - Headers: ID, Name, Section, Week 1-10, Total Attendance
  - Blue header background (#0F45A8)
  - White header text
  - Frozen first row
  - Proper column widths
  - Auto-calculated Total Attendance column
  - Alternating row colors (white and light gray)

## Examples

```bash
# Single section from sampleInput.xlsx
python create_attendance_sheet.py sampleInput "Attendance Sheet" A1
# Output: output/Attendance Sheet.xlsx

# Multiple sections from AI-Students.xlsx
python create_attendance_sheet.py AI-Students "Logic Design" A1 A2 B1
# Output: output/Logic Design.xlsx
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
- Total Attendance column automatically counts 'P', 'p', or '1' values
- Formula used: `=SUMPRODUCT((UPPER(D2:M2)="P")+(D2:M2="1"))`
  - Counts 'P' or 'p' (case-insensitive)
  - Counts '1' (numeric attendance marker)
  - Updates automatically when attendance is marked
