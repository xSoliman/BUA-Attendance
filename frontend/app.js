// QR Attendance System - Main Application Logic

// Configuration
const API_BASE_URL = 'https://bua-attendance.onrender.com/api';
const COOLDOWN_DURATION = 30000; // 30 seconds in milliseconds
const TOAST_DURATION = 3000; // 3 seconds
const REQUEST_TIMEOUT = 10000; // 10 seconds timeout for requests
const SCAN_DELAY = 2000; // 2 seconds delay between scans
const SEMESTER_START_DATE = new Date('2026-02-07'); // First day of Week 1: February 7, 2026

// State Management
let sessionContext = {
    spreadsheetId: null,
    sheetName: null,
    columnName: null
};

let cooldownCache = new Map();
let qrScanner = null;
let isProcessing = false; // Flag to prevent concurrent scans
let processingQueue = new Set(); // Track IDs being processed
let scannedStudents = []; // Store scanned student IDs with timestamps
let lastScanTime = 0; // Track last scan time for delay

// Calculate current week based on semester start date
function getCurrentWeek() {
    const now = new Date();
    const diffTime = now - SEMESTER_START_DATE;
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24));
    const weekNumber = Math.floor(diffDays / 7) + 1; // +1 because week 1 starts on day 0
    
    // Return week number if it's between 1 and 14, otherwise return null
    if (weekNumber >= 1 && weekNumber <= 14) {
        return weekNumber;
    }
    return null;
}

// Scanner Status Management
function updateScannerStatus(status, message) {
    const statusElement = document.getElementById('scanner-status');
    if (!statusElement) return;
    
    // Remove all status classes
    statusElement.classList.remove('ready', 'waiting', 'processing', 'error');
    
    // Add new status class and update text
    statusElement.classList.add(status);
    statusElement.textContent = message;
}

function updateLastScanned(studentName, studentId) {
    const lastScannedElement = document.getElementById('last-scanned');
    if (!lastScannedElement) return;
    
    const displayText = studentName ? studentName : studentId;
    lastScannedElement.textContent = displayText;
    
    // Add highlight animation
    lastScannedElement.classList.remove('highlight');
    void lastScannedElement.offsetWidth; // Trigger reflow
    lastScannedElement.classList.add('highlight');
    
    // Remove highlight after animation
    setTimeout(() => {
        lastScannedElement.classList.remove('highlight');
    }, 500);
}

// Utility Functions
function parseQRData(qrData) {
    /**
     * Parse QR code data to extract name and ID
     * Supports formats:
     * - "Name - ID" (new format with name)
     * - "ID" (legacy format, ID only)
     * 
     * Returns: { name: string|null, id: string }
     */
    qrData = qrData.trim();
    
    // Check if format is "Name - ID"
    if (qrData.includes(' - ')) {
        const parts = qrData.split(' - ');
        if (parts.length >= 2) {
            const name = parts.slice(0, -1).join(' - ').trim(); // Handle names with " - " in them
            const id = parts[parts.length - 1].trim();
            return { name, id };
        }
    }
    
    // Legacy format: just ID
    return { name: null, id: qrData };
}

function extractSpreadsheetId(input) {
    // Remove whitespace
    input = input.trim();
    
    // If it's already just an ID (no slashes), return it
    if (!input.includes('/') && !input.includes('\\')) {
        return input;
    }
    
    // Try to extract from URL
    // Google Sheets URL format: https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/edit...
    const patterns = [
        /\/spreadsheets\/d\/([a-zA-Z0-9-_]+)/,  // Standard URL
        /\/d\/([a-zA-Z0-9-_]+)/,                 // Short format
        /id=([a-zA-Z0-9-_]+)/                    // Query parameter format
    ];
    
    for (const pattern of patterns) {
        const match = input.match(pattern);
        if (match && match[1]) {
            return match[1];
        }
    }
    
    // If no pattern matched, return the input as-is
    return input;
}

function showLoader() {
    const loader = document.getElementById('loading-overlay');
    if (loader) {
        loader.style.display = 'flex';
    }
}

function hideLoader() {
    const loader = document.getElementById('loading-overlay');
    if (loader) {
        loader.style.display = 'none';
    }
}
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    toast.id = `toast-${Date.now()}`;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, TOAST_DURATION);
}

function getStoredConfig() {
    const config = localStorage.getItem('qr-attendance-config');
    return config ? JSON.parse(config) : null;
}

function saveConfig(spreadsheetId) {
    const config = {
        spreadsheetId,
        lastUpdated: new Date().toISOString()
    };
    localStorage.setItem('qr-attendance-config', JSON.stringify(config));
}

function clearConfig() {
    localStorage.removeItem('qr-attendance-config');
}

function saveSessionContext(context) {
    sessionStorage.setItem('qr-attendance-session', JSON.stringify(context));
}

function getSessionContext() {
    const session = sessionStorage.getItem('qr-attendance-session');
    return session ? JSON.parse(session) : null;
}

// API Functions
async function fetchServiceAccountEmail() {
    try {
        const response = await fetch(`${API_BASE_URL}/service-account-email`);
        const data = await response.json();
        return data.email;
    } catch (error) {
        console.error('Error fetching service account email:', error);
        return 'Error loading email';
    }
}

async function validateSpreadsheet(spreadsheetId) {
    try {
        const response = await fetch(`${API_BASE_URL}/validate-spreadsheet`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ spreadsheet_id: spreadsheetId })
        });
        return await response.json();
    } catch (error) {
        console.error('Error validating spreadsheet:', error);
        return { valid: false, message: 'Network error. Please try again.' };
    }
}

async function fetchSheets(spreadsheetId) {
    try {
        const response = await fetch(`${API_BASE_URL}/sheets/${spreadsheetId}`);
        const data = await response.json();
        return data.sheets;
    } catch (error) {
        console.error('Error fetching sheets:', error);
        return [];
    }
}

async function fetchColumns(spreadsheetId, sheetName) {
    try {
        const response = await fetch(`${API_BASE_URL}/sheets/${spreadsheetId}/${encodeURIComponent(sheetName)}/columns`);
        const data = await response.json();
        return data.columns;
    } catch (error) {
        console.error('Error fetching columns:', error);
        return [];
    }
}

function recordAttendanceLocally(studentId, studentName = null) {
    // Add to scanned list with timestamp
    const scanTime = new Date();
    scannedStudents.push({
        id: studentId,
        name: studentName,
        timestamp: scanTime.toISOString(),
        displayTime: scanTime.toLocaleTimeString()
    });
    
    // Add to cooldown (30 seconds)
    addToCooldown(studentId);
    
    // Update UI
    updateScannedList();
    
    // Update last scanned display
    updateLastScanned(studentName, studentId);
    
    // Show toast with name if available
    const displayText = studentName ? `✓ ${studentName}` : `✓ ${studentId}`;
    showToast(displayText, 'success');
    
    // Save to localStorage for persistence
    saveScannedStudents();
}

function showScannerCooldown() {
    let countdown = Math.ceil(SCAN_DELAY / 1000);
    
    // Update scanner status immediately
    updateScannerStatus('waiting', `Ready in ${countdown}s...`);
    
    const interval = setInterval(() => {
        countdown--;
        if (countdown > 0) {
            updateScannerStatus('waiting', `Ready in ${countdown}s...`);
        } else {
            updateScannerStatus('ready', '✓ Ready to scan');
            clearInterval(interval);
        }
    }, 1000);
}

function updateScannedList() {
    const listContainer = document.getElementById('scanned-list');
    const countSpan = document.getElementById('scan-count');
    
    if (!listContainer || !countSpan) return;
    
    // Update count
    countSpan.textContent = scannedStudents.length;
    
    // Update button states
    updateScannerButtons();
    
    // Clear and rebuild list
    if (scannedStudents.length === 0) {
        listContainer.innerHTML = '<p class="empty-message">No students scanned yet</p>';
        return;
    }
    
    listContainer.innerHTML = '';
    
    // Add items in reverse order (newest first)
    scannedStudents.slice().reverse().forEach((student, index) => {
        const item = document.createElement('div');
        item.className = 'scanned-item';
        
        // Display name if available, otherwise just ID
        const displayName = student.name ? student.name : student.id;
        const displayId = student.name ? `ID: ${student.id}` : '';
        
        item.innerHTML = `
            <div>
                <div class="student-id">${displayName}</div>
                ${displayId ? `<div class="student-id-label">${displayId}</div>` : ''}
                <div class="scan-time">${student.displayTime}</div>
            </div>
            <button class="remove-btn" onclick="removeScannedStudent('${student.id}')" title="Remove">
                ✕
            </button>
        `;
        listContainer.appendChild(item);
    });
}

function removeScannedStudent(studentId) {
    // Remove from scanned list
    scannedStudents = scannedStudents.filter(s => s.id !== studentId);
    
    // Remove from cooldown
    cooldownCache.delete(studentId);
    
    // Update UI
    updateScannedList();
    saveScannedStudents();
    showToast(`Removed ${studentId}`, 'warning');
}

function saveScannedStudents() {
    sessionStorage.setItem('scanned-students', JSON.stringify(scannedStudents));
}

function loadScannedStudents() {
    const saved = sessionStorage.getItem('scanned-students');
    if (saved) {
        scannedStudents = JSON.parse(saved);
        updateScannedList();
        
        // Restore cooldown cache
        scannedStudents.forEach(student => {
            const scanTime = new Date(student.timestamp).getTime();
            cooldownCache.set(student.id, scanTime);
        });
    }
}

function clearAllScans() {
    if (scannedStudents.length === 0) {
        showToast('No scans to clear', 'warning');
        return;
    }
    
    if (confirm(`Clear all ${scannedStudents.length} scanned students?`)) {
        scannedStudents = [];
        cooldownCache.clear();
        updateScannedList();
        saveScannedStudents();
        showToast('All scans cleared', 'success');
    }
}

function downloadScannedList() {
    if (scannedStudents.length === 0) {
        showToast('No scans to download', 'warning');
        return;
    }
    
    // Create text content with general timestamp
    let content = `QR Attendance System - Scanned Students\n`;
    content += `Session: ${sessionContext.sheetName} - ${sessionContext.columnName}\n`;
    content += `Date: ${new Date().toLocaleString('en-US', { hour12: true })}\n`;
    content += `Total Students: ${scannedStudents.length}\n`;
    content += `\n${'='.repeat(50)}\n\n`;
    
    // List students without individual timestamps
    scannedStudents.forEach((student, index) => {
        const displayText = student.name 
            ? `${student.name} - ${student.id}` 
            : student.id;
        
        content += `${index + 1}. ${displayText}\n`;
    });
    
    // Create and download file with UTF-8 BOM for proper Arabic text support
    const BOM = '\uFEFF'; // UTF-8 BOM (Byte Order Mark)
    const blob = new Blob([BOM + content], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `attendance_${sessionContext.sheetName}_${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    showToast('Downloaded!', 'success');
}

async function submitAttendanceToSheet() {
    if (scannedStudents.length === 0) {
        showToast('No students to submit', 'warning');
        return;
    }
    
    const confirmed = confirm(
        `Submit ${scannedStudents.length} scanned students to the server?\n\n` +
        `This will mark attendance in the Google Sheet.`
    );
    
    if (!confirmed) return;
    
    // Show loader
    showLoader();
    
    try {
        // Extract just the IDs
        const studentIds = scannedStudents.map(s => s.id);
        
        // Send batch request
        const response = await fetch(`${API_BASE_URL}/attendance/batch`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                spreadsheet_id: sessionContext.spreadsheetId,
                sheet_name: sessionContext.sheetName,
                column_name: sessionContext.columnName,
                student_ids: studentIds
            })
        });
        
        if (!response.ok) {
            const errData = await response.json().catch(() => ({}));
            throw new Error(errData.detail || `HTTP ${response.status}`);
        }
        
        const result = await response.json();
        
        // Show results
        hideLoader();
        
        // Check if any failed and show their error message
        const failedDetails = result.details?.filter(d => d.status === 'error') || [];
        const firstError = failedDetails[0]?.message || '';
        
        const message = `Submission Complete!\n\n` +
            `Total: ${result.total}\n` +
            `✓ Successful: ${result.successful}\n` +
            `✗ Not Found: ${result.not_found}\n` +
            `⚠ Failed: ${result.failed}` +
            (firstError ? `\n\nError: ${firstError}` : '');
        
        alert(message);
        
        if (result.successful > 0) {
            showToast(`${result.successful} students marked!`, 'success');
        }
        
        if (result.not_found > 0) {
            showToast(`${result.not_found} students not found`, 'warning');
        }
        
        // Keep the scanned list after submission (don't clear automatically)
        // Users can manually clear using the "Clear All" button if needed
        
    } catch (error) {
        hideLoader();
        console.error('Batch submission error:', error);
        showToast('Failed to submit. Please try again or download backup.', 'error');
    }
}

// Cooldown Management
function addToCooldown(studentId) {
    cooldownCache.set(studentId, Date.now());
}

function checkCooldown(studentId) {
    if (!cooldownCache.has(studentId)) {
        return false;
    }
    
    const timestamp = cooldownCache.get(studentId);
    const elapsed = Date.now() - timestamp;
    
    if (elapsed >= COOLDOWN_DURATION) {
        cooldownCache.delete(studentId);
        return false;
    }
    
    return true;
}

function clearCooldown() {
    cooldownCache.clear();
    processingQueue.clear();
    isProcessing = false;
}
function cleanupCooldown() {
    const now = Date.now();
    for (const [studentId, timestamp] of cooldownCache.entries()) {
        if (now - timestamp >= COOLDOWN_DURATION) {
            cooldownCache.delete(studentId);
        }
    }
}

// Scanner Functions
function initializeScanner() {
    const qrReader = document.getElementById('qr-reader');
    if (!qrReader) return;
    
    // Set initial scanner status
    updateScannerStatus('processing', 'Initializing camera...');
    
    qrScanner = new Html5Qrcode("qr-reader");
    
    const config = {
        fps: 10,
        qrbox: { width: 250, height: 250 }
    };
    
    qrScanner.start(
        { facingMode: "environment" },
        config,
        onScanSuccess,
        onScanError
    ).then(() => {
        // Scanner started successfully
        updateScannerStatus('ready', '✓ Ready to scan');
    }).catch(err => {
        updateScannerStatus('error', '✗ Camera access denied');
        showToast('Camera access denied. Please enable camera permissions.', 'error');
        console.error('Scanner error:', err);
    });
}

function onScanSuccess(decodedText) {
    processStudentId(decodedText);
}

function onScanError(error) {
    // Ignore scan errors (they happen frequently during scanning)
}

function processStudentId(qrData) {
    // Parse QR data to extract name and ID
    const { name, id } = parseQRData(qrData);
    
    // Check scan delay (2 seconds between scans) - ALWAYS check first
    const now = Date.now();
    const timeSinceLastScan = now - lastScanTime;
    
    if (timeSinceLastScan < SCAN_DELAY) {
        // Silently ignore - scanner is in cooldown period
        return;
    }
    
    // Update last scan time IMMEDIATELY (before any other checks)
    // This ensures delay activates for ALL scan attempts
    lastScanTime = now;
    
    // Show countdown for next scan
    showScannerCooldown();
    
    // Check if already in cooldown (scanned in last 30 seconds)
    if (checkCooldown(id)) {
        const displayText = name ? `${name} already scanned` : 'Already Scanned';
        showToast(displayText, 'warning');
        return;
    }
    
    // Record locally (instant, no backend call)
    recordAttendanceLocally(id, name);
}

function stopScanner() {
    if (qrScanner) {
        qrScanner.stop().then(() => {
            qrScanner.clear();
        }).catch(err => {
            console.error('Error stopping scanner:', err);
        });
    }
}

// Page Initialization
function initPage() {
    const path = window.location.pathname;
    
    if (path.includes('config.html')) {
        initConfigPage();
    } else if (path.includes('session.html')) {
        // Redirect to scanner.html (session is now merged with scanner)
        window.location.href = 'scanner.html';
    } else if (path.includes('scanner.html')) {
        initScannerPage();
    } else {
        // Default index.html - redirect based on config
        const config = getStoredConfig();
        if (config && config.spreadsheetId) {
            window.location.href = 'scanner.html';
        } else {
            window.location.href = 'config.html';
        }
    }
}

function initConfigPage() {
    // Load service account email
    fetchServiceAccountEmail().then(email => {
        const emailElement = document.getElementById('service-account-email');
        if (emailElement) {
            emailElement.textContent = email;
        }
    });
    
    // Load existing config
    const config = getStoredConfig();
    if (config) {
        const input = document.getElementById('spreadsheet-id');
        if (input) {
            input.value = config.spreadsheetId;
        }
    }
    
    // Save button handler
    const saveBtn = document.getElementById('save-config');
    if (saveBtn) {
        saveBtn.addEventListener('click', async () => {
            const input = document.getElementById('spreadsheet-id');
            const userInput = input.value.trim();
            
            if (!userInput) {
                showToast('Please enter a Spreadsheet ID or URL', 'error');
                return;
            }
            
            // Extract spreadsheet ID from URL or use as-is
            const spreadsheetId = extractSpreadsheetId(userInput);
            
            if (!spreadsheetId) {
                showToast('Invalid Spreadsheet ID or URL', 'error');
                return;
            }
            
            const statusDiv = document.getElementById('validation-status');
            statusDiv.textContent = 'Validating...';
            statusDiv.className = '';
            
            const result = await validateSpreadsheet(spreadsheetId);
            
            if (result.valid) {
                saveConfig(spreadsheetId);
                statusDiv.textContent = 'Configuration saved successfully!';
                statusDiv.className = 'success';
                setTimeout(() => {
                    window.location.href = 'scanner.html';
                }, 1500);
            } else {
                statusDiv.textContent = result.message;
                statusDiv.className = 'error';
            }
        });
    }
    
    // Clear button handler
    const clearBtn = document.getElementById('clear-config');
    if (clearBtn) {
        clearBtn.addEventListener('click', () => {
            if (confirm('Are you sure you want to clear the configuration?')) {
                clearConfig();
                const input = document.getElementById('spreadsheet-id');
                if (input) {
                    input.value = '';
                }
                const statusDiv = document.getElementById('validation-status');
                statusDiv.textContent = 'Configuration cleared';
                statusDiv.className = 'success';
            }
        });
    }
}

function initScannerPage() {
    const config = getStoredConfig();
    if (!config) {
        window.location.href = 'config.html';
        return;
    }
    
    sessionContext.spreadsheetId = config.spreadsheetId;
    
    // Load sheets for session selection
    fetchSheets(config.spreadsheetId).then(sheets => {
        const select = document.getElementById('course-sheet');
        if (select) {
            select.innerHTML = '<option value="">Select a course</option>';
            sheets.forEach(sheet => {
                const option = document.createElement('option');
                option.value = sheet;
                option.textContent = sheet;
                select.appendChild(option);
            });
        }
    });
    
    // Course selection handler
    const courseSelect = document.getElementById('course-sheet');
    if (courseSelect) {
        courseSelect.addEventListener('change', async (e) => {
            const sheetName = e.target.value;
            
            // Check if there are scanned students and user is changing session
            if (scannedStudents.length > 0 && sheetName && sessionContext.sheetName && sessionContext.sheetName !== sheetName) {
                if (!confirm(`You have ${scannedStudents.length} scanned students. Clear scanned list?`)) {
                    // User cancelled, revert selection
                    e.target.value = sessionContext.sheetName;
                    return;
                }
                // Clear the list
                scannedStudents = [];
                cooldownCache.clear();
                updateScannedList();
                saveScannedStudents();
            }
            
            sessionContext.sheetName = sheetName;
            
            const columnSelect = document.getElementById('attendance-column');
            if (!sheetName) {
                columnSelect.disabled = true;
                columnSelect.innerHTML = '<option value="">Select a course first</option>';
                updateScannerButtons();
                return;
            }
            
            columnSelect.disabled = false;
            columnSelect.innerHTML = '<option value="">Loading...</option>';
            
            const columns = await fetchColumns(config.spreadsheetId, sheetName);
            columnSelect.innerHTML = '<option value="">Select a week</option>';
            
            const currentWeek = getCurrentWeek();
            
            columns.forEach(column => {
                const option = document.createElement('option');
                option.value = column;
                
                // Check if this is the current week or past week
                const weekMatch = column.match(/Week (\d+)/i);
                const weekNumber = weekMatch ? parseInt(weekMatch[1]) : null;
                const isCurrentWeek = weekNumber && currentWeek && weekNumber === currentWeek;
                const isPastWeek = weekNumber && currentWeek && weekNumber < currentWeek;
                
                if (isCurrentWeek) {
                    option.textContent = `${column} ⭐ (Current Week)`;
                    option.style.fontWeight = 'bold';
                    option.style.color = '#2563eb'; // Blue for current week
                } else if (isPastWeek) {
                    option.textContent = `${column} ⚠️ (Past Week)`;
                    option.style.color = '#dc2626'; // Red for past weeks
                    option.style.fontStyle = 'italic';
                } else {
                    option.textContent = column;
                }
                
                columnSelect.appendChild(option);
            });
        });
    }
    
    // Column selection handler
    const columnSelect = document.getElementById('attendance-column');
    if (columnSelect) {
        columnSelect.addEventListener('change', (e) => {
            const columnName = e.target.value;
            
            // Check if there are scanned students and user is changing session
            if (scannedStudents.length > 0 && columnName && sessionContext.columnName && sessionContext.columnName !== columnName) {
                if (!confirm(`You have ${scannedStudents.length} scanned students. Clear scanned list?`)) {
                    // User cancelled, revert selection
                    e.target.value = sessionContext.columnName;
                    return;
                }
                // Clear the list
                scannedStudents = [];
                cooldownCache.clear();
                updateScannedList();
                saveScannedStudents();
            }
            
            // Check if selected week is a past week
            if (columnName) {
                const weekMatch = columnName.match(/Week (\d+)/i);
                const weekNumber = weekMatch ? parseInt(weekMatch[1]) : null;
                const currentWeek = getCurrentWeek();
                const isPastWeek = weekNumber && currentWeek && weekNumber < currentWeek;
                
                if (isPastWeek) {
                    const confirmed = confirm(
                        `⚠️ WARNING: You selected "${columnName}" which is a PAST WEEK.\n\n` +
                        `Current week is: Week ${currentWeek}\n\n` +
                        `If you continue:\n` +
                        `• You will OVERWRITE any existing attendance data for this week\n` +
                        `• Students already marked as present may be changed\n\n` +
                        `Are you sure you want to continue?`
                    );
                    
                    if (!confirmed) {
                        // User cancelled, clear selection
                        e.target.value = '';
                        sessionContext.columnName = '';
                        updateScannerButtons();
                        return;
                    }
                    
                    // Show additional warning toast
                    showToast(`⚠️ Past week selected: ${columnName}`, 'warning');
                }
            }
            
            sessionContext.columnName = columnName;
            updateScannerButtons();
            
            // If both course and week are selected, save session context
            if (sessionContext.sheetName && sessionContext.columnName) {
                saveSessionContext(sessionContext);
            }
        });
    }
    
    // Settings button
    const changeConfigBtn = document.getElementById('change-config-btn');
    if (changeConfigBtn) {
        changeConfigBtn.addEventListener('click', () => {
            if (confirm('Return to configuration? This will clear your current session.')) {
                window.location.href = 'config.html';
            }
        });
    }
    
    // Load previously scanned students
    loadScannedStudents();
    
    // Initialize scanner immediately on page load
    initializeScanner();
    
    // Start periodic cooldown cleanup (every 5 seconds)
    const cleanupInterval = setInterval(cleanupCooldown, 5000);
    
    // Store interval ID for cleanup on page unload
    window.addEventListener('beforeunload', () => {
        clearInterval(cleanupInterval);
    });
    
    // Submit Attendance button
    const submitAttendanceBtn = document.getElementById('submit-attendance');
    if (submitAttendanceBtn) {
        submitAttendanceBtn.addEventListener('click', submitAttendanceToSheet);
    }
    
    // Clear Scans button
    const clearScansBtn = document.getElementById('clear-scans');
    if (clearScansBtn) {
        clearScansBtn.addEventListener('click', clearAllScans);
    }
    
    // Download TXT button
    const downloadBtn = document.getElementById('download-txt');
    if (downloadBtn) {
        downloadBtn.addEventListener('click', downloadScannedList);
    }
    
    // Manual entry handler
    const submitBtn = document.getElementById('submit-manual');
    const manualInput = document.getElementById('manual-id');
    
    if (submitBtn && manualInput) {
        submitBtn.addEventListener('click', () => {
            const studentId = manualInput.value.trim();
            if (studentId) {
                processStudentId(studentId);
                manualInput.value = '';
            }
        });
        
        manualInput.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                submitBtn.click();
            }
        });
    }
}

function updateScannerButtons() {
    const sessionReady = sessionContext.sheetName && sessionContext.columnName;
    
    // Enable/disable buttons based on session readiness
    const submitManualBtn = document.getElementById('submit-manual');
    const submitAttendanceBtn = document.getElementById('submit-attendance');
    const clearScansBtn = document.getElementById('clear-scans');
    const downloadBtn = document.getElementById('download-txt');
    
    if (submitManualBtn) submitManualBtn.disabled = !sessionReady;
    if (submitAttendanceBtn) submitAttendanceBtn.disabled = !sessionReady || scannedStudents.length === 0;
    if (clearScansBtn) clearScansBtn.disabled = scannedStudents.length === 0;
    if (downloadBtn) downloadBtn.disabled = scannedStudents.length === 0;
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initPage);
