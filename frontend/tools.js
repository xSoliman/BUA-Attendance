/**
 * tools.js — GUI logic for Attendance Sheet & QR Code generators
 */

const API_BASE = (window.API_BASE_URL || "http://localhost:8000").replace(/\/$/, "");

// ── Utilities ────────────────────────────────────────────────────────────────

function setStatus(el, type, msg) {
  el.className = "status-msg " + type;
  el.textContent = msg;
}

function clearStatus(el) {
  el.className = "status-msg";
  el.textContent = "";
}

/** Trigger a file download from a Blob */
function downloadBlob(blob, filename) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);
}

/** Parse pasted text (tab or comma separated) into [{id, name, section}] */
function parsePaste(text) {
  return text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      // Support tab-separated (from Excel) or comma-separated
      const sep = line.includes("\t") ? "\t" : ",";
      const parts = line.split(sep).map((p) => p.trim().replace(/^"|"$/g, ""));
      return {
        id: parts[0] || "",
        name: parts[1] || "",
        section: parts[2] || "",
      };
    })
    .filter((s) => s.id || s.name);
}

// ── Table builder ─────────────────────────────────────────────────────────────

function buildTable(tbodyId, initialRows = 5) {
  const tbody = document.getElementById(tbodyId);
  tbody.innerHTML = "";
  for (let i = 0; i < initialRows; i++) addRow(tbody);
}

function addRow(tbody, data = {}) {
  const rowCount = tbody.rows.length + 1;
  const tr = document.createElement("tr");
  tr.innerHTML = `
    <td class="row-num">${rowCount}</td>
    <td><input type="text" placeholder="20210001" value="${esc(data.id)}" aria-label="Student ID" /></td>
    <td><input type="text" placeholder="Student name" value="${esc(data.name)}" aria-label="Name" /></td>
    <td><input type="text" placeholder="A1" value="${esc(data.section)}" aria-label="Section" /></td>
    <td><button class="btn-remove" title="Remove row" aria-label="Remove row">✕</button></td>
  `;
  tr.querySelector(".btn-remove").addEventListener("click", () => {
    tr.remove();
    reindex(tbody);
  });
  tbody.appendChild(tr);
}

function reindex(tbody) {
  Array.from(tbody.rows).forEach((tr, i) => {
    const numCell = tr.querySelector(".row-num");
    if (numCell) numCell.textContent = i + 1;
  });
}

function esc(v) {
  return (v || "").replace(/"/g, "&quot;").replace(/</g, "&lt;");
}

/** Collect non-empty rows from a tbody */
function collectStudents(tbody) {
  const students = [];
  const errors = [];
  Array.from(tbody.rows).forEach((tr, i) => {
    const inputs = tr.querySelectorAll("input");
    const id = inputs[0].value.trim();
    const name = inputs[1].value.trim();
    const section = inputs[2].value.trim();

    // Reset validation state
    inputs[0].classList.remove("invalid");
    inputs[1].classList.remove("invalid");

    if (!id && !name) return; // skip truly empty rows

    let rowValid = true;
    if (!id) { inputs[0].classList.add("invalid"); rowValid = false; }
    if (!name) { inputs[1].classList.add("invalid"); rowValid = false; }

    if (!rowValid) {
      errors.push(`Row ${i + 1}: ID and Name are required.`);
      return;
    }

    students.push({ id, name, section });
  });
  return { students, errors };
}

// ── Paste modal ───────────────────────────────────────────────────────────────

let _pasteTarget = null; // tbody element to populate after paste

function openPasteModal(tbody) {
  _pasteTarget = tbody;
  const modal = document.getElementById("paste-modal");
  document.getElementById("paste-area").value = "";
  modal.hidden = false;
  document.getElementById("paste-area").focus();
}

document.getElementById("paste-confirm").addEventListener("click", () => {
  const text = document.getElementById("paste-area").value;
  const rows = parsePaste(text);
  if (rows.length && _pasteTarget) {
    rows.forEach((r) => addRow(_pasteTarget, r));
    reindex(_pasteTarget);
  }
  document.getElementById("paste-modal").hidden = true;
});

document.getElementById("paste-cancel").addEventListener("click", () => {
  document.getElementById("paste-modal").hidden = true;
});

// Close modal on overlay click
document.getElementById("paste-modal").addEventListener("click", (e) => {
  if (e.target === e.currentTarget) e.currentTarget.hidden = true;
});

// ── Tab switching ─────────────────────────────────────────────────────────────

document.querySelectorAll(".tab-btn").forEach((btn) => {
  btn.addEventListener("click", () => {
    const target = btn.dataset.tab;
    document.querySelectorAll(".tab-btn").forEach((b) => {
      b.classList.toggle("active", b === btn);
      b.setAttribute("aria-selected", b === btn ? "true" : "false");
    });
    document.querySelectorAll(".tab-panel").forEach((panel) => {
      const isActive = panel.id === "tab-" + target;
      panel.classList.toggle("active", isActive);
      panel.hidden = !isActive;
    });
  });
});

// ── Attendance tab ────────────────────────────────────────────────────────────

const attTbody = document.getElementById("att-tbody");
buildTable("att-tbody", 5);

document.getElementById("att-add-row").addEventListener("click", () => {
  addRow(attTbody);
});

document.getElementById("att-paste-btn").addEventListener("click", () => {
  openPasteModal(attTbody);
});

document.getElementById("att-clear-btn").addEventListener("click", () => {
  attTbody.innerHTML = "";
  buildTable("att-tbody", 5);
  clearStatus(document.getElementById("att-status"));
  document.getElementById("att-info-box").hidden = true;
});

document.getElementById("att-generate-btn").addEventListener("click", async () => {
  const statusEl = document.getElementById("att-status");
  const btn = document.getElementById("att-generate-btn");
  const infoBox = document.getElementById("att-info-box");

  const { students, errors } = collectStudents(attTbody);

  if (errors.length) {
    setStatus(statusEl, "error", errors[0]);
    return;
  }
  if (!students.length) {
    setStatus(statusEl, "error", "Add at least one student.");
    return;
  }

  const outputName = document.getElementById("att-output-name").value.trim() || "Attendance";

  btn.disabled = true;
  setStatus(statusEl, "loading", "Generating…");
  infoBox.hidden = true;

  try {
    const res = await fetch(`${API_BASE}/api/tools/generate-attendance`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ students, output_name: outputName }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Unknown error" }));
      throw new Error(err.detail || "Server error");
    }

    const blob = await res.blob();
    downloadBlob(blob, `${outputName}.xlsx`);
    setStatus(statusEl, "success", `Downloaded "${outputName}.xlsx" (${students.length} students)`);
    infoBox.hidden = false;
  } catch (e) {
    setStatus(statusEl, "error", "Error: " + e.message);
  } finally {
    btn.disabled = false;
  }
});

// ── QR tab ────────────────────────────────────────────────────────────────────

const qrTbody = document.getElementById("qr-tbody");
buildTable("qr-tbody", 5);

document.getElementById("qr-add-row").addEventListener("click", () => {
  addRow(qrTbody);
});

document.getElementById("qr-paste-btn").addEventListener("click", () => {
  openPasteModal(qrTbody);
});

document.getElementById("qr-clear-btn").addEventListener("click", () => {
  qrTbody.innerHTML = "";
  buildTable("qr-tbody", 5);
  clearStatus(document.getElementById("qr-status"));
});

document.getElementById("qr-generate-btn").addEventListener("click", async () => {
  const statusEl = document.getElementById("qr-status");
  const btn = document.getElementById("qr-generate-btn");

  const { students, errors } = collectStudents(qrTbody);

  if (errors.length) {
    setStatus(statusEl, "error", errors[0]);
    return;
  }
  if (!students.length) {
    setStatus(statusEl, "error", "Add at least one student.");
    return;
  }

  const sheetName = document.getElementById("qr-sheet-name").value.trim();
  const tabName = document.getElementById("qr-tab-name").value.trim();

  btn.disabled = true;
  setStatus(statusEl, "loading", "Generating QR codes…");

  try {
    const res = await fetch(`${API_BASE}/api/tools/generate-qr`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ students, sheet_name: sheetName, tab_name: tabName }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Unknown error" }));
      throw new Error(err.detail || "Server error");
    }

    const blob = await res.blob();
    downloadBlob(blob, "qr_codes.zip");
    setStatus(statusEl, "success", `Downloaded qr_codes.zip (${students.length} QR codes)`);
  } catch (e) {
    setStatus(statusEl, "error", "Error: " + e.message);
  } finally {
    btn.disabled = false;
  }
});
