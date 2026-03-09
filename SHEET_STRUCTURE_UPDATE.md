# Sheet Structure Update

## Overview

The attendance sheets now support a new structure with a Section column. The backend automatically detects and handles both old and new sheet formats.

## Sheet Formats

### Old Format (Backward Compatible)
```
| Column A | Column B | Column C | Column D | Column E | ...
|----------|----------|----------|----------|----------|
| ID       | Name     | Week 1   | Week 2   | Week 3   | ...
```

### New Format (Current)
```
| Column A | Column B | Column C | Column D | Column E | Column F | ...
|----------|----------|----------|----------|----------|----------|
| ID       | Name     | Section  | Week 1   | Week 2   | Week 3   | ...
```

## Backend Changes

### `sheets_service.py` - `get_headers()` Function

The function now automatically detects the sheet structure:

1. **Detection Logic**: Checks if Column C header is "Section" (case-insensitive)
2. **Old Format**: If Column C is NOT "Section", starts reading attendance columns from Column C
3. **New Format**: If Column C IS "Section", starts reading attendance columns from Column D

This ensures:
- ✓ Old sheets without Section column continue to work
- ✓ New sheets with Section column work correctly
- ✓ No manual configuration needed
- ✓ Automatic detection per sheet

## Frontend Compatibility

The frontend (scanner app) is not affected by this change because:
- QR codes only contain Student ID (no section information)
- Backend only needs ID to find the student row
- Section column is only used for organization in the sheet

## Script Changes

### `create_attendance_sheet.py`

The attendance sheet generator now:
- Takes sheet name as first argument
- Reads from `input/<sheet_name>.xlsx`
- Filters students by section codes
- Creates sheets with the new format (ID, Name, Section, Week 1-10)

Usage:
```bash
python create_attendance_sheet.py sampleInput A1 A2
python create_attendance_sheet.py AI-Students A1 A2 B7
```

## Testing

The backend has been tested with both formats:
- Old format: Returns correct attendance columns (Week 1, Week 2, ...)
- New format: Returns correct attendance columns (Week 1, Week 2, ...), skipping Section

## Migration

No migration needed! The system automatically handles both formats:
1. Existing sheets without Section column continue to work
2. New sheets with Section column work immediately
3. You can have both formats in the same spreadsheet (different tabs)
