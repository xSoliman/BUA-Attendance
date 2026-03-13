# Past Week Warning Feature

## Overview
Added visual indicators and warnings when selecting past weeks to prevent accidental overwriting of attendance data.

## Features Implemented

### 1. Visual Indicators in Week Dropdown

The week selection dropdown now shows three types of weeks with different styling:

- **Current Week** (⭐): Blue, bold text
  - Example: "Week 5 ⭐ (Current Week)"
  - Color: `#2563eb` (blue)
  
- **Past Weeks** (⚠️): Red, italic text
  - Example: "Week 3 ⚠️ (Past Week)"
  - Color: `#dc2626` (red)
  - Indicates weeks that have already passed
  
- **Future Weeks**: Normal text
  - Example: "Week 7"
  - Default styling

### 2. Warning Dialog for Past Weeks

When a user selects a past week, they receive a confirmation dialog:

```
⚠️ WARNING: You selected "Week 3" which is a PAST WEEK.

Current week is: Week 5

If you continue:
• You will OVERWRITE any existing attendance data for this week
• Students already marked as present may be changed

Are you sure you want to continue?
```

**User Options:**
- **Cancel**: Selection is cleared, no changes made
- **OK**: User can proceed with the past week selection

### 3. Additional Toast Notification

After confirming a past week selection, a warning toast appears:
- Message: "⚠️ Past week selected: Week 3"
- Type: Warning (yellow/orange)
- Duration: 3 seconds

## Technical Implementation

### JavaScript Changes (`frontend/app.js`)

1. **Week Classification Logic**:
   ```javascript
   const weekNumber = weekMatch ? parseInt(weekMatch[1]) : null;
   const isCurrentWeek = weekNumber && currentWeek && weekNumber === currentWeek;
   const isPastWeek = weekNumber && currentWeek && weekNumber < currentWeek;
   ```

2. **Option Styling**:
   - Current week: Blue color, bold, star emoji
   - Past week: Red color, italic, warning emoji
   - Future week: Default styling

3. **Selection Validation**:
   - Detects when a past week is selected
   - Shows confirmation dialog
   - Clears selection if user cancels
   - Shows warning toast if user confirms

### CSS Changes (`frontend/styles.css`)

Added basic option styling (limited browser support):
```css
select option {
    padding: 8px;
}
```

Note: Most styling is handled via JavaScript due to limited CSS support for `<option>` elements across browsers.

## User Experience Flow

### Scenario 1: Selecting Current Week
1. User opens week dropdown
2. Sees "Week 5 ⭐ (Current Week)" in blue
3. Selects it
4. No warnings, proceeds normally

### Scenario 2: Selecting Past Week
1. User opens week dropdown
2. Sees "Week 3 ⚠️ (Past Week)" in red
3. Selects it
4. **Warning dialog appears**
5. User can cancel or confirm
6. If confirmed, warning toast appears
7. User can proceed with scanning

### Scenario 3: Selecting Future Week
1. User opens week dropdown
2. Sees "Week 7" in normal text
3. Selects it
4. No warnings, proceeds normally

## Benefits

1. **Prevents Accidental Data Loss**: Users are warned before overwriting existing attendance
2. **Visual Clarity**: Easy to identify which weeks are past, current, or future
3. **Informed Decisions**: Users understand the consequences of selecting past weeks
4. **Flexibility**: Still allows legitimate use cases (makeup sessions, corrections)

## Edge Cases Handled

1. **No Current Week**: If semester hasn't started or has ended, no week is marked as current
2. **Week Number Parsing**: Handles various formats like "Week 1", "week 5", etc.
3. **Non-Week Columns**: Columns without "Week X" format are treated as normal (no warnings)
4. **Multiple Confirmations**: If user has scanned students AND selects past week, they get both warnings

## Testing Checklist

- [x] Current week shows with star emoji and blue color
- [x] Past weeks show with warning emoji and red color
- [x] Future weeks show with normal styling
- [x] Warning dialog appears when selecting past week
- [x] User can cancel past week selection
- [x] User can confirm past week selection
- [x] Warning toast appears after confirmation
- [x] No warnings for current or future weeks
- [x] JavaScript syntax is valid
- [x] Works with existing session change warnings

## Future Enhancements

Potential improvements for future versions:

1. **Backend Validation**: Add server-side check to prevent past week submissions
2. **Audit Log**: Track when past weeks are modified and by whom
3. **Read-Only Mode**: Option to make past weeks read-only after a certain date
4. **Batch Edit Warning**: Special warning when submitting large batches to past weeks
5. **Color Customization**: Allow admins to customize warning colors
6. **Disable Past Weeks**: Option to completely disable past week selection

## Related Files

- `frontend/app.js` - Main logic for week selection and warnings
- `frontend/styles.css` - Visual styling for week options
- `frontend/scanner.html` - Week selection dropdown UI

## Version

- Feature Added: March 11, 2026
- Version: 1.1.0
