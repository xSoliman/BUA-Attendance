// QR Attendance System - Main Application Logic

// Configuration
const API_BASE_URL = 'https://bua-attendance.onrender.com';
const COOLDOWN_DURATION = 30000; // 30 seconds in milliseconds
const TOAST_DURATION = 3000; // 3 seconds

// State Management
let sessionContext = {
    spreadsheetId: null,
    sheetName: null,
    columnName: null
};

let cooldownCache = new Map();
let qrScanner = null;

// Utility Functions
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

async function recordAttendance(studentId) {
    try {
        const response = await fetch(`${API_BASE_URL}/attendance`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                spreadsheet_id: sessionContext.spreadsheetId,
                sheet_name: sessionContext.sheetName,
                column_name: sessionContext.columnName,
                student_id: studentId
            })
        });
        
        const result = await response.json();
        
        if (result.status === 'success') {
            showToast('Attendance Recorded', 'success');
            addToCooldown(studentId);
        } else if (result.status === 'not_found') {
            showToast('Student Not Found', 'error');
        } else {
            showToast(result.message, 'error');
        }
    } catch (error) {
        if (!navigator.onLine) {
            showToast('Offline - will retry when connected', 'warning');
        } else {
            showToast('Network error. Please try again.', 'error');
        }
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
    if (checkCooldown(studentId)) {
        showToast('Already Scanned', 'warning');
        return;
    }
    
    recordAttendance(studentId);
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
            const spreadsheetId = input.value.trim();
            
            if (!spreadsheetId) {
                showToast('Please enter a Spreadsheet ID', 'error');
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
    
    // Initialize scanner
    initializeScanner();
    
    // Start periodic cooldown cleanup (every 5 seconds)
    const cleanupInterval = setInterval(cleanupCooldown, 5000);
    
    // Store interval ID for cleanup on page unload
    window.addEventListener('beforeunload', () => {
        clearInterval(cleanupInterval);
    });
    
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
        changeBtn.addEventListener('click', () => {
            stopScanner();
            clearCooldown();
            window.location.href = 'session.html';
        });
    }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initPage);
