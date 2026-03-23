/**
 * tools.js — GUI logic for Attendance Sheet & QR Code generators
 */

// Match the same API base used by app.js
const API_BASE = "https://bua-attendance.onrender.com";

// ── Utilities ────────────────────────────────────────────────────────────────

function setStatus(el, type, msg) {
  el.className = "status-msg " + type;
  el.textContent = msg;
}

function clearStatus(el) {
  el.className = "status-msg";
  el.textContent = "";
}

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

function esc(v) {
  return (v || "").replace(/&/g, "&amp;").replace(/"/g, "&quot;").replace(/</g, "&lt;");
}

/** Parse pasted text into [{id, name, section}], skipping blank lines */
function parsePaste(text) {
  return text
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter(Boolean)
    .map((line) => {
      const sep = line.includes("\t") ? "\t" : ",";
      const parts = line.split(sep).map((p) => p.trim().replace(/^"|"$/g, ""));
      return { id: parts[0] || "", name: parts[1] || "", section: parts[2] || "" };
    })
    .filter((s) => s.id.trim() || s.name.trim()); // skip rows with no id AND no name
}

// ── Paginated student store ───────────────────────────────────────────────────
// The attendance table is backed by an in-memory array; the DOM shows one page.

const PAGE_SIZE = 10;

/**
 * Creates a paginated table controller.
 * @param {string} tbodyId
 * @param {string} paginationId
 */
function createPaginatedTable(tbodyId, paginationId) {
  let rows = []; // [{id, name, section}]
  let page = 0;  // 0-indexed current page

  const tbody = document.getElementById(tbodyId);
  const pagination = document.getElementById(paginationId);

  function totalPages() {
    return Math.max(1, Math.ceil(rows.length / PAGE_SIZE));
  }

  function render() {
    tbody.innerHTML = "";
    const start = page * PAGE_SIZE;
    const slice = rows.slice(start, start + PAGE_SIZE);

    slice.forEach((row, localIdx) => {
      const globalIdx = start + localIdx;
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td class="row-num">${globalIdx + 1}</td>
        <td><input type="text" placeholder="20210001" value="${esc(row.id)}"      aria-label="Student ID" /></td>
        <td><input type="text" placeholder="Student name" value="${esc(row.name)}" aria-label="Name" /></td>
        <td><input type="text" placeholder="A1" value="${esc(row.section)}"       aria-label="Section" /></td>
        <td><button class="btn-remove" title="Remove row" aria-label="Remove row">✕</button></td>
      `;

      // Sync input changes back to the store
      const inputs = tr.querySelectorAll("input");
      inputs[0].addEventListener("input", () => { rows[globalIdx].id      = inputs[0].value; });
      inputs[1].addEventListener("input", () => { rows[globalIdx].name    = inputs[1].value; });
      inputs[2].addEventListener("input", () => { rows[globalIdx].section = inputs[2].value; });

      tr.querySelector(".btn-remove").addEventListener("click", () => {
        rows.splice(globalIdx, 1);
        // Stay on same page unless it no longer exists
        if (page >= totalPages()) page = totalPages() - 1;
        render();
        renderPagination();
      });

      tbody.appendChild(tr);
    });

    renderPagination();
  }

  function renderPagination() {
    const tp = totalPages();
    pagination.innerHTML = "";

    if (tp <= 1) return; // no controls needed for a single page

    const info = document.createElement("span");
    info.className = "page-info";
    info.textContent = `Page ${page + 1} of ${tp}  (${rows.length} students)`;

    const prev = document.createElement("button");
    prev.className = "btn-page";
    prev.textContent = "← Prev";
    prev.disabled = page === 0;
    prev.addEventListener("click", () => { page--; render(); });

    const next = document.createElement("button");
    next.className = "btn-page";
    next.textContent = "Next →";
    next.disabled = page === tp - 1;
    next.addEventListener("click", () => { page++; render(); });

    pagination.appendChild(prev);
    pagination.appendChild(info);
    pagination.appendChild(next);
  }

  return {
    /** Add a single blank row and jump to its page */
    addRow(data = {}) {
      rows.push({ id: data.id || "", name: data.name || "", section: data.section || "" });
      page = totalPages() - 1;
      render();
    },

    /** Replace all rows (e.g. after paste), skip truly empty entries */
    setRows(newRows) {
      rows = newRows.filter((r) => r.id.trim() || r.name.trim());
      page = 0;
      render();
    },

    /** Append rows (paste import) */
    appendRows(newRows) {
      const filtered = newRows.filter((r) => r.id.trim() || r.name.trim());
      rows = rows.concat(filtered);
      page = totalPages() - 1;
      render();
    },

    /** Clear everything and reset to 5 blank rows */
    reset() {
      rows = Array.from({ length: 5 }, () => ({ id: "", name: "", section: "" }));
      page = 0;
      render();
    },

    /**
     * Collect all non-empty rows with validation.
     * Returns {students, errors}
     */
    collect() {
      // First flush any pending DOM edits (inputs on current page are already synced via events)
      const students = [];
      const errors = [];

      rows.forEach((row, i) => {
        const id   = row.id.trim();
        const name = row.name.trim();
        const section = row.section.trim();

        if (!id && !name) return; // skip blank rows silently

        if (!id || !name) {
          errors.push(`Row ${i + 1}: both ID and Name are required.`);
          return;
        }
        students.push({ id, name, section });
      });

      return { students, errors };
    },

    getRows() { return rows; },
    getPage() { return page; },
  };
}

// ── Paste modal ───────────────────────────────────────────────────────────────

let _pasteCallback = null;

function openPasteModal(onConfirm) {
  _pasteCallback = onConfirm;
  document.getElementById("paste-area").value = "";
  document.getElementById("paste-modal").hidden = false;
  document.getElementById("paste-area").focus();
}

document.getElementById("paste-confirm").addEventListener("click", () => {
  const text = document.getElementById("paste-area").value;
  const rows = parsePaste(text);
  if (_pasteCallback) _pasteCallback(rows);
  document.getElementById("paste-modal").hidden = true;
});

document.getElementById("paste-cancel").addEventListener("click", () => {
  document.getElementById("paste-modal").hidden = true;
});

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

const attTable = createPaginatedTable("att-tbody", "att-pagination");
attTable.reset();

document.getElementById("att-add-row").addEventListener("click", () => attTable.addRow());

document.getElementById("att-paste-btn").addEventListener("click", () => {
  openPasteModal((rows) => attTable.appendRows(rows));
});

document.getElementById("att-clear-btn").addEventListener("click", () => {
  attTable.reset();
  clearStatus(document.getElementById("att-status"));
  document.getElementById("att-info-box").hidden = true;
});

document.getElementById("att-generate-btn").addEventListener("click", async () => {
  const statusEl = document.getElementById("att-status");
  const btn      = document.getElementById("att-generate-btn");
  const infoBox  = document.getElementById("att-info-box");

  const { students, errors } = attTable.collect();

  if (errors.length) { setStatus(statusEl, "error", errors[0]); return; }
  if (!students.length) { setStatus(statusEl, "error", "Add at least one student."); return; }

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
      throw new Error(err.detail || `Server error ${res.status}`);
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

const qrTable = createPaginatedTable("qr-tbody", "qr-pagination");
qrTable.reset();

document.getElementById("qr-add-row").addEventListener("click", () => qrTable.addRow());

document.getElementById("qr-paste-btn").addEventListener("click", () => {
  openPasteModal((rows) => qrTable.appendRows(rows));
});

document.getElementById("qr-clear-btn").addEventListener("click", () => {
  qrTable.reset();
  clearStatus(document.getElementById("qr-status"));
});

document.getElementById("qr-generate-btn").addEventListener("click", async () => {
  const statusEl = document.getElementById("qr-status");
  const btn      = document.getElementById("qr-generate-btn");

  const { students, errors } = qrTable.collect();

  if (errors.length) { setStatus(statusEl, "error", errors[0]); return; }
  if (!students.length) { setStatus(statusEl, "error", "Add at least one student."); return; }

  const college = document.getElementById("qr-college").value.trim();

  btn.disabled = true;
  setStatus(statusEl, "loading", "Generating QR codes…");

  try {
    const res = await fetch(`${API_BASE}/api/tools/generate-qr`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ students, college }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Unknown error" }));
      throw new Error(err.detail || `Server error ${res.status}`);
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
