// QR Attendance System - Main Application Logic

// Configuration
const API_BASE_URL = 'https://bua-attendance.onrender.com/api';
const COOLDOWN_DURATION = 30000; // 30 seconds in milliseconds
const TOAST_DURATION = 3000; // 3 seconds
const REQUEST_TIMEOUT = 10000; // 10 seconds timeout for requests
const SCAN_DELAY = 2000; // 2 seconds delay between scans

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

// Utility Functions
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

function recordAttendanceLocally(studentId) {
    // Add to scanned list with timestamp
    const scanTime = new Date();
    scannedStudents.push({
        id: studentId,
        timestamp: scanTime.toISOString(),
        displayTime: scanTime.toLocaleTimeString()
    });
    
    // Add to cooldown (30 seconds)
    addToCooldown(studentId);
    
    // Update UI
    updateScannedList();
    showToast(`✓ ${studentId} scanned`, 'success');
    
    // Save to localStorage for persistence
    saveScannedStudents();
}

function showScannerCooldown() {
    let countdown = Math.ceil(SCAN_DELAY / 1000);
    const toastId = `scanner-cooldown-${Date.now()}`;
    
    // Create countdown toast
    const container = document.getElementById('toast-container');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = 'toast warning';
    toast.id = toastId;
    toast.textContent = `Ready in ${countdown}s...`;
    container.appendChild(toast);
    
    // Update countdown every second
    const interval = setInterval(() => {
        countdown--;
        if (countdown > 0) {
            toast.textContent = `Ready in ${countdown}s...`;
        } else {
            toast.textContent = '✓ Ready to scan';
            toast.className = 'toast success';
            setTimeout(() => {
                toast.remove();
            }, 500);
            clearInterval(interval);
        }
    }, 1000);
    
    // Remove after delay
    setTimeout(() => {
        clearInterval(interval);
        if (toast.parentNode) {
            toast.remove();
        }
    }, SCAN_DELAY + 500);
}

function updateScannedList() {
    const listContainer = document.getElementById('scanned-list');
    const countSpan = document.getElementById('scan-count');
    
    if (!listContainer || !countSpan) return;
    
    // Update count
    countSpan.textContent = scannedStudents.length;
    
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
        item.innerHTML = `
            <div>
                <div class="student-id">${student.id}</div>
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
    
    // Create text content
    let content = `QR Attendance System - Scanned Students\n`;
    content += `Session: ${sessionContext.sheetName} - ${sessionContext.columnName}\n`;
    content += `Date: ${new Date().toLocaleString()}\n`;
    content += `Total Students: ${scannedStudents.length}\n`;
    content += `\n${'='.repeat(50)}\n\n`;
    
    scannedStudents.forEach((student, index) => {
        content += `${index + 1}. ${student.id} - ${student.displayTime}\n`;
    });
    
    // Create and download file
    const blob = new Blob([content], { type: 'text/plain' });
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

async function endSessionAndSubmit() {
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
            throw new Error(`HTTP ${response.status}`);
        }
        
        const result = await response.json();
        
        // Show results
        hideLoader();
        
        const message = `
            Submission Complete!\n
            Total: ${result.total}
            ✓ Successful: ${result.successful}
            ✗ Not Found: ${result.not_found}
            ⚠ Failed: ${result.failed}
        `;
        
        alert(message);
        
        if (result.successful > 0) {
            showToast(`${result.successful} students marked!`, 'success');
        }
        
        if (result.not_found > 0) {
            showToast(`${result.not_found} students not found`, 'warning');
        }
        
        // Clear scanned list after successful submission
        if (confirm('Clear scanned list?')) {
            scannedStudents = [];
            cooldownCache.clear();
            updateScannedList();
            saveScannedStudents();
        }
        
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
    ).catch(err => {
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

function processStudentId(studentId) {
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
    if (checkCooldown(studentId)) {
        showToast('Already Scanned', 'warning');
        return;
    }
    
    // Record locally (instant, no backend call)
    recordAttendanceLocally(studentId);
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
        initSessionPage();
    } else if (path.includes('scanner.html')) {
        initScannerPage();
    } else {
        // Default index.html - redirect based on config
        const config = getStoredConfig();
        if (config && config.spreadsheetId) {
            window.location.href = 'session.html';
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
                    window.location.href = 'session.html';
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

function initSessionPage() {
    const config = getStoredConfig();
    if (!config) {
        window.location.href = 'config.html';
        return;
    }
    
    sessionContext.spreadsheetId = config.spreadsheetId;
    
    // Load sheets
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
            sessionContext.sheetName = sheetName;
            
            const columnSelect = document.getElementById('attendance-column');
            if (!sheetName) {
                columnSelect.disabled = true;
                columnSelect.innerHTML = '<option value="">Select a course first</option>';
                return;
            }
            
            columnSelect.disabled = false;
            columnSelect.innerHTML = '<option value="">Loading...</option>';
            
            const columns = await fetchColumns(config.spreadsheetId, sheetName);
            columnSelect.innerHTML = '<option value="">Select a week</option>';
            columns.forEach(column => {
                const option = document.createElement('option');
                option.value = column;
                option.textContent = column;
                columnSelect.appendChild(option);
            });
        });
    }
    
    // Column selection handler
    const columnSelect = document.getElementById('attendance-column');
    if (columnSelect) {
        columnSelect.addEventListener('change', (e) => {
            sessionContext.columnName = e.target.value;
            updateStartButton();
        });
    }
    
    // Start scanner button
    const startBtn = document.getElementById('start-scanner');
    if (startBtn) {
        startBtn.addEventListener('click', () => {
            // Save session context before navigating
            saveSessionContext(sessionContext);
            window.location.href = 'scanner.html';
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
}

function updateStartButton() {
    const startBtn = document.getElementById('start-scanner');
    if (startBtn) {
        startBtn.disabled = !(sessionContext.sheetName && sessionContext.columnName);
    }
}

function initScannerPage() {
    const config = getStoredConfig();
    if (!config) {
        window.location.href = 'config.html';
        return;
    }
    
    // Load session context from sessionStorage
    const savedSession = getSessionContext();
    if (savedSession) {
        sessionContext = savedSession;
    } else {
        // No session context, redirect to session page
        window.location.href = 'session.html';
        return;
    }
    
    // Display session info
    const courseSpan = document.getElementById('current-course');
    const weekSpan = document.getElementById('current-week');
    if (courseSpan) courseSpan.textContent = sessionContext.sheetName || '-';
    if (weekSpan) weekSpan.textContent = sessionContext.columnName || '-';
    
    // Load previously scanned students
    loadScannedStudents();
    
    // Initialize scanner
    initializeScanner();
    
    // Start periodic cooldown cleanup (every 5 seconds)
    const cleanupInterval = setInterval(cleanupCooldown, 5000);
    
    // Store interval ID for cleanup on page unload
    window.addEventListener('beforeunload', () => {
        clearInterval(cleanupInterval);
    });
    
    // End Session button
    const endSessionBtn = document.getElementById('end-session');
    if (endSessionBtn) {
        endSessionBtn.addEventListener('click', endSessionAndSubmit);
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
    
    // Change session button
    const changeBtn = document.getElementById('change-session');
    if (changeBtn) {
        changeBtn.addEventListener('click', async () => {
            // Warn user about clearing session data
            const hasScannedData = scannedStudents.length > 0;
            let confirmMessage = 'Change to a different session?';
            
            if (hasScannedData) {
                confirmMessage = `You have ${scannedStudents.length} scanned student(s).\n\n` +
                                `Changing session will clear this data.\n\n` +
                                `Continue?`;
            }
            
            if (confirm(confirmMessage)) {
                // Try to stop scanner (with timeout to prevent blocking)
                try {
                    if (qrScanner) {
                        await Promise.race([
                            qrScanner.stop().then(() => qrScanner.clear()),
                            new Promise(resolve => setTimeout(resolve, 1000)) // 1 second timeout
                        ]);
                    }
                } catch (err) {
                    console.error('Error stopping scanner:', err);
                    // Continue anyway - don't let scanner errors block navigation
                }
                
                // Clear all session data
                scannedStudents = [];
                cooldownCache.clear();
                processingQueue.clear();
                isProcessing = false;
                lastScanTime = 0;
                qrScanner = null; // Reset scanner reference
                
                // Clear session storage
                sessionStorage.removeItem('scanned-students');
                sessionStorage.removeItem('qr-attendance-session');
                
                // Navigate to session page
                window.location.href = 'session.html';
            }
        });
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initPage);
