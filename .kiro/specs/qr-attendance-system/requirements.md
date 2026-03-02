# Requirements Document

## Introduction

The QR Attendance System is a web-based tool designed for University Teaching Assistants to automate student attendance tracking during lab sessions. The system scans student QR codes containing Student IDs and records attendance in a Google Sheet database. The application is optimized for mobile browsers and provides a stateless, configuration-driven approach where TAs can use their own Google Sheets without complex setup.

## Glossary

- **TA**: Teaching Assistant who operates the attendance system
- **Student_ID**: Unique identifier for each student, encoded in their QR code
- **Attendance_System**: The web application that scans QR codes and records attendance
- **Google_Sheet**: The spreadsheet file used as the database for student records
- **Course_Sheet**: A single tab/sheet within the Google_Sheet representing one course
- **Attendance_Column**: A column in the Course_Sheet representing a specific week (e.g., "Week 1", "Week 2")
- **Scanner_Interface**: The mobile-optimized UI component that displays camera feed and processes QR codes
- **Service_Account**: Google Cloud service account with credentials for accessing Google Sheets API
- **Spreadsheet_ID**: The unique identifier from the Google Sheet URL
- **Session**: A single attendance-taking period for a specific Course_Sheet and Attendance_Column
- **Scan_Cooldown**: A 30-second period during which duplicate scans of the same Student_ID are prevented

## Requirements

### Requirement 1: Google Sheets Integration

**User Story:** As a TA, I want to use my existing Google Sheet as the database, so that I can manage student data in a familiar tool without learning new systems.

#### Acceptance Criteria

1. THE Attendance_System SHALL connect to Google_Sheet using the Google Sheets API via Service_Account credentials
2. WHEN a TA provides a Spreadsheet_ID, THE Attendance_System SHALL validate that the Google_Sheet is accessible
3. WHEN the Google_Sheet is not accessible, THE Attendance_System SHALL display an error message instructing the TA to add the Service_Account email as an Editor
4. THE Attendance_System SHALL read the list of Course_Sheet names from the Google_Sheet
5. WHEN a Course_Sheet is selected, THE Attendance_System SHALL read the header row to identify available Attendance_Column names
6. THE Attendance_System SHALL identify the Student_ID column by searching for headers matching "ID" or "رقم الجلوس"
7. WHEN a Student_ID is scanned, THE Attendance_System SHALL locate the student's row by matching the Student_ID value
8. WHEN a student's row is found, THE Attendance_System SHALL write "P" to the cell at the intersection of the student's row and the selected Attendance_Column
9. WHEN a Student_ID is not found in the Course_Sheet, THE Attendance_System SHALL return a "Student Not Found" status

### Requirement 2: Configuration Management

**User Story:** As a TA, I want to configure the system once on my phone, so that I don't have to re-enter settings every time I take attendance.

#### Acceptance Criteria

1. WHEN a TA first accesses the Attendance_System, THE Attendance_System SHALL display a configuration page requesting the Spreadsheet_ID
2. WHEN a TA submits a Spreadsheet_ID, THE Attendance_System SHALL store the Spreadsheet_ID in browser localStorage
3. WHEN a TA returns to the Attendance_System, THE Attendance_System SHALL retrieve the Spreadsheet_ID from localStorage and skip the configuration page
4. THE Attendance_System SHALL provide a settings option to update or clear the stored Spreadsheet_ID
5. THE Attendance_System SHALL display the Service_Account email address with instructions to add it as an Editor to the Google_Sheet

### Requirement 3: Session Initialization

**User Story:** As a TA, I want to select which course and week I'm recording attendance for, so that the system marks the correct column in my spreadsheet.

#### Acceptance Criteria

1. WHEN the Spreadsheet_ID is configured, THE Attendance_System SHALL display a session initialization page
2. THE Attendance_System SHALL fetch and display a list of Course_Sheet names from the Google_Sheet
3. WHEN a TA selects a Course_Sheet, THE Attendance_System SHALL fetch the header row from that Course_Sheet
4. THE Attendance_System SHALL display a list of Attendance_Column names starting from column D onwards
5. WHEN a TA selects both a Course_Sheet and an Attendance_Column, THE Attendance_System SHALL enable the "Start Scanner" button
6. WHEN the TA clicks "Start Scanner", THE Attendance_System SHALL navigate to the Scanner_Interface

### Requirement 4: QR Code Scanning

**User Story:** As a TA, I want to scan student QR codes quickly using my phone's camera, so that I can record attendance efficiently during lab sessions.

#### Acceptance Criteria

1. THE Scanner_Interface SHALL use the html5-qrcode library to access the device camera
2. THE Scanner_Interface SHALL display a camera viewfinder optimized for mobile screens
3. WHEN a QR code is detected, THE Scanner_Interface SHALL extract the Student_ID from the QR code data
4. WHEN a Student_ID is extracted, THE Scanner_Interface SHALL send the Student_ID to the backend for processing
5. THE Scanner_Interface SHALL continue scanning without requiring manual reset after each successful scan
6. WHEN the camera cannot be accessed, THE Scanner_Interface SHALL display an error message with troubleshooting instructions

### Requirement 5: Attendance Recording Feedback

**User Story:** As a TA, I want immediate visual feedback after scanning each student, so that I know whether the attendance was recorded successfully.

#### Acceptance Criteria

1. WHEN attendance is successfully recorded, THE Scanner_Interface SHALL display a green toast notification with the message "Attendance Recorded"
2. WHEN a Student_ID is not found in the Course_Sheet, THE Scanner_Interface SHALL display a red toast notification with the message "Student Not Found"
3. WHEN a Google Sheets API error occurs, THE Scanner_Interface SHALL display a red toast notification with an error description
4. THE Scanner_Interface SHALL automatically dismiss toast notifications after 3 seconds
5. THE Scanner_Interface SHALL allow multiple toast notifications to be visible simultaneously when scanning rapidly

### Requirement 6: Duplicate Scan Prevention

**User Story:** As a TA, I want to prevent accidentally scanning the same student multiple times, so that attendance records remain accurate.

#### Acceptance Criteria

1. WHEN a Student_ID is successfully scanned, THE Attendance_System SHALL record the Student_ID and timestamp in a Scan_Cooldown list
2. WHEN a Student_ID is scanned, THE Attendance_System SHALL check if the Student_ID exists in the Scan_Cooldown list
3. IF a Student_ID is in the Scan_Cooldown list and less than 30 seconds have elapsed, THEN THE Attendance_System SHALL display a yellow toast notification with the message "Already Scanned"
4. IF a Student_ID is in the Scan_Cooldown list and less than 30 seconds have elapsed, THEN THE Attendance_System SHALL NOT update the Google_Sheet
5. WHEN 30 seconds have elapsed since a scan, THE Attendance_System SHALL remove the Student_ID from the Scan_Cooldown list

### Requirement 7: Manual ID Entry

**User Story:** As a TA, I want to manually enter a Student_ID when the QR code is damaged or unreadable, so that I can still record attendance for all students.

#### Acceptance Criteria

1. THE Scanner_Interface SHALL display a text input field for manual Student_ID entry
2. WHEN a TA enters a Student_ID in the text input and submits, THE Attendance_System SHALL process it identically to a scanned Student_ID
3. WHEN manual entry is successful, THE Scanner_Interface SHALL clear the text input field
4. THE Attendance_System SHALL apply the same Scan_Cooldown rules to manually entered Student_IDs

### Requirement 8: Mobile-First User Interface

**User Story:** As a TA, I want a responsive interface optimized for my phone, so that I can easily use the system during lab sessions without a laptop.

#### Acceptance Criteria

1. THE Attendance_System SHALL render all pages with a responsive layout that adapts to mobile screen sizes
2. THE Scanner_Interface SHALL display the camera viewfinder at a size that fills at least 80% of the viewport width on mobile devices
3. THE Attendance_System SHALL use touch-friendly UI elements with minimum tap target sizes of 44x44 pixels
4. THE Attendance_System SHALL display text with minimum font size of 16 pixels to prevent automatic zoom on mobile browsers
5. THE Scanner_Interface SHALL position the manual entry input and submit button within easy thumb reach on mobile devices

### Requirement 9: Asynchronous Operations

**User Story:** As a TA, I want the interface to remain responsive while the system updates the spreadsheet, so that I can continue scanning students without delays.

#### Acceptance Criteria

1. THE Attendance_System SHALL use asynchronous API calls for all Google Sheets operations
2. WHILE a Google Sheets operation is in progress, THE Scanner_Interface SHALL remain interactive and continue scanning
3. WHEN multiple scans occur rapidly, THE Attendance_System SHALL queue the Google Sheets updates and process them asynchronously
4. THE Attendance_System SHALL display a loading indicator for operations that take longer than 1 second
5. WHEN an asynchronous operation fails, THE Attendance_System SHALL display an error notification without blocking subsequent scans

### Requirement 10: QR Code Generation Script

**User Story:** As a TA, I want to generate QR codes for my students from a CSV file, so that students can print their attendance cards before the semester starts.

#### Acceptance Criteria

1. THE QR_Generator_Script SHALL accept a CSV file containing Student_ID and student name columns as input
2. WHEN the CSV file is processed, THE QR_Generator_Script SHALL generate one QR code image for each student
3. THE QR_Generator_Script SHALL encode only the Student_ID value in each QR code
4. THE QR_Generator_Script SHALL add a footer to each QR code image containing the student's name and Student_ID in readable text
5. THE QR_Generator_Script SHALL save generated QR code images with filenames in the format "{Student_ID}.png"
6. THE QR_Generator_Script SHALL create an output directory for generated images if it does not exist

### Requirement 11: Error Handling and Recovery

**User Story:** As a TA, I want clear error messages when something goes wrong, so that I can fix issues quickly during lab sessions.

#### Acceptance Criteria

1. WHEN the Google Sheets API returns an authentication error, THE Attendance_System SHALL display a message instructing the TA to verify Service_Account permissions
2. WHEN the Google Sheets API returns a rate limit error, THE Attendance_System SHALL retry the operation after a 2-second delay
3. WHEN the selected Course_Sheet does not contain a Student_ID column, THE Attendance_System SHALL display an error message and prevent session initialization
4. WHEN the selected Attendance_Column does not exist in the Course_Sheet, THE Attendance_System SHALL display an error message and return to session initialization
5. WHEN network connectivity is lost, THE Attendance_System SHALL display a notification indicating offline status

### Requirement 12: Session Management

**User Story:** As a TA, I want to easily switch between courses and weeks, so that I can handle multiple lab sections in one day.

#### Acceptance Criteria

1. WHILE the Scanner_Interface is active, THE Attendance_System SHALL display the currently selected Course_Sheet and Attendance_Column
2. THE Scanner_Interface SHALL provide a "Change Session" button to return to session initialization
3. WHEN the TA clicks "Change Session", THE Attendance_System SHALL stop the camera and navigate to the session initialization page
4. WHEN the TA changes the session, THE Attendance_System SHALL clear the Scan_Cooldown list
5. THE Attendance_System SHALL preserve the Spreadsheet_ID in localStorage when changing sessions

## Notes

- The system prioritizes simplicity and reliability for non-technical TAs
- All Google Sheets operations must be asynchronous to maintain UI responsiveness
- The mobile-first design ensures the system works well in lab environments where TAs move around
- The stateless architecture means no server-side session management is required
- Service Account credentials will be stored securely on the server (not exposed to client)
