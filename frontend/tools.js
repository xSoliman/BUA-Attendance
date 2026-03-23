/**
 * tools.js — GUI logic for Attendance Sheet & QR Code generators
 */

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

function parsePaste(text) {
  return text
    .split(/\r?\n/)
    .map((l) => l.trim())
    .filter(Boolean)
    .map((line) => {
      const sep = line.includes("\t") ? "\t" : ",";
      const parts = line.split(sep).map((p) => p.trim().replace(/^"|"$/g, ""));
      return { id: parts[0] || "", name: parts[1] || "", section: parts[2] || "" };
    })
    .filter((s) => s.id || s.name);
}

// ── Paginated table controller ────────────────────────────────────────────────

const PAGE_SIZE = 5;

function createPaginatedTable(tbodyEl, paginationEl) {
  let rows = [];
  let page = 0;

  function totalPages() { return Math.max(1, Math.ceil(rows.length / PAGE_SIZE)); }

  function render() {
    tbodyEl.innerHTML = "";
    const start = page * PAGE_SIZE;
    rows.slice(start, start + PAGE_SIZE).forEach((row, localIdx) => {
      const gi = start + localIdx; // global index
      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td class="row-num">${gi + 1}</td>
        <td><input type="text" placeholder="20210001" value="${esc(row.id)}"      aria-label="Student ID" /></td>
        <td><input type="text" placeholder="Student name" value="${esc(row.name)}" aria-label="Name" /></td>
        <td><input type="text" placeholder="A1" value="${esc(row.section)}"       aria-label="Section" /></td>
        <td><button class="btn-remove" aria-label="Remove row">✕</button></td>
      `;
      const inputs = tr.querySelectorAll("input");
      inputs[0].addEventListener("input", () => { rows[gi].id      = inputs[0].value; });
      inputs[1].addEventListener("input", () => { rows[gi].name    = inputs[1].value; });
      inputs[2].addEventListener("input", () => { rows[gi].section = inputs[2].value; });
      tr.querySelector(".btn-remove").addEventListener("click", () => {
        rows.splice(gi, 1);
        if (page >= totalPages()) page = totalPages() - 1;
        render();
      });
      tbodyEl.appendChild(tr);
    });
    renderPagination();
  }

  function renderPagination() {
    paginationEl.innerHTML = "";
    if (totalPages() <= 1) return;
    const prev = document.createElement("button");
    prev.className = "btn-page";
    prev.textContent = "← Prev";
    prev.disabled = page === 0;
    prev.addEventListener("click", () => { page--; render(); });

    const info = document.createElement("span");
    info.className = "page-info";
    info.textContent = `Page ${page + 1} of ${totalPages()}  (${rows.length} students)`;

    const next = document.createElement("button");
    next.className = "btn-page";
    next.textContent = "Next →";
    next.disabled = page === totalPages() - 1;
    next.addEventListener("click", () => { page++; render(); });

    paginationEl.append(prev, info, next);
  }

  return {
    addRow(data = {}) {
      rows.push({ id: data.id || "", name: data.name || "", section: data.section || "" });
      page = totalPages() - 1;
      render();
    },
    appendRows(newRows) {
      rows = rows.concat(newRows.filter((r) => r.id.trim() || r.name.trim()));
      page = totalPages() - 1;
      render();
    },
    reset(n = 5) {
      rows = Array.from({ length: n }, () => ({ id: "", name: "", section: "" }));
      page = 0;
      render();
    },
    collect() {
      const students = [], errors = [];
      rows.forEach((row, i) => {
        const id = row.id.trim(), name = row.name.trim(), section = row.section.trim();
        if (!id && !name) return;
        if (!id || !name) { errors.push(`Row ${i + 1}: ID and Name are required.`); return; }
        students.push({ id, name, section });
      });
      return { students, errors };
    },
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
  const rows = parsePaste(document.getElementById("paste-area").value);
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
      const active = panel.id === "tab-" + target;
      panel.classList.toggle("active", active);
      panel.hidden = !active;
    });
  });
});

// ── Attendance tab — multi-course manager ─────────────────────────────────────

const attCoursesEl = document.getElementById("att-courses");
const attControllers = []; // [{nameInput, table, pagiEl}]

function createCourseBlock(index) {
  const id = `course-${Date.now()}-${index}`;

  const block = document.createElement("div");
  block.className = "course-block";
  block.innerHTML = `
    <div class="course-header">
      <div class="field-row course-name-field">
        <label>Course name (tab label) <span class="required">*</span></label>
        <input type="text" class="course-name-input" placeholder="e.g. Logic Design" maxlength="31" />
      </div>
      <div class="course-header-actions">
        <button class="btn-secondary btn-sm course-add-row">+ Add row</button>
        <button class="btn-secondary btn-sm course-paste-btn">Paste data</button>
        <button class="btn-danger-sm btn-sm course-remove-btn">Remove course</button>
      </div>
    </div>
    <div class="table-wrapper">
      <table aria-label="Student list">
        <thead>
          <tr>
            <th>#</th>
            <th>Student ID <span class="required">*</span></th>
            <th>Name <span class="required">*</span></th>
            <th>Section</th>
            <th></th>
          </tr>
        </thead>
        <tbody class="course-tbody"></tbody>
      </table>
    </div>
    <div class="pagination-bar course-pagination"></div>
  `;

  const tbodyEl     = block.querySelector(".course-tbody");
  const pagiEl      = block.querySelector(".course-pagination");
  const nameInput   = block.querySelector(".course-name-input");
  const table       = createPaginatedTable(tbodyEl, pagiEl);
  table.reset(5);

  block.querySelector(".course-add-row").addEventListener("click", () => table.addRow());
  block.querySelector(".course-paste-btn").addEventListener("click", () => {
    openPasteModal((rows) => table.appendRows(rows));
  });
  block.querySelector(".course-remove-btn").addEventListener("click", () => {
    const idx = attControllers.findIndex((c) => c.block === block);
    if (idx !== -1) attControllers.splice(idx, 1);
    block.remove();
    renumberCourses();
  });

  attCoursesEl.appendChild(block);
  attControllers.push({ block, nameInput, table });
  renumberCourses();
}

function renumberCourses() {
  attControllers.forEach((c, i) => {
    const label = c.block.querySelector(".course-name-field label");
    label.innerHTML = `Course ${i + 1} name (tab label) <span class="required">*</span>`;
  });
}

// Start with one course
createCourseBlock(0);

document.getElementById("att-add-course").addEventListener("click", () => {
  createCourseBlock(attControllers.length);
});

document.getElementById("att-generate-btn").addEventListener("click", async () => {
  const statusEl = document.getElementById("att-status");
  const btn      = document.getElementById("att-generate-btn");
  const infoBox  = document.getElementById("att-info-box");

  // Validate & collect all courses
  const courses = [];
  const errors  = [];

  attControllers.forEach((ctrl, i) => {
    const name = ctrl.nameInput.value.trim();
    if (!name) { errors.push(`Course ${i + 1}: name is required.`); return; }

    const { students, errors: rowErrors } = ctrl.table.collect();
    rowErrors.forEach((e) => errors.push(`Course "${name}": ${e}`));
    if (students.length) courses.push({ name, students });
  });

  if (errors.length)  { setStatus(statusEl, "error", errors[0]); return; }
  if (!courses.length){ setStatus(statusEl, "error", "Add at least one student."); return; }

  const outputName = document.getElementById("att-output-name").value.trim() || "Attendance";

  btn.disabled = true;
  setStatus(statusEl, "loading", `Generating ${courses.length} course(s)…`);
  infoBox.hidden = true;

  try {
    const res = await fetch(`${API_BASE}/api/tools/generate-attendance`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ courses, output_name: outputName }),
    });

    if (!res.ok) {
      const err = await res.json().catch(() => ({ detail: "Unknown error" }));
      throw new Error(err.detail || `Server error ${res.status}`);
    }

    const blob = await res.blob();
    const total = courses.reduce((s, c) => s + c.students.length, 0);
    downloadBlob(blob, `${outputName}.xlsx`);
    setStatus(statusEl, "success",
      `Downloaded "${outputName}.xlsx" — ${courses.length} course(s), ${total} students`);
    infoBox.hidden = false;
  } catch (e) {
    setStatus(statusEl, "error", "Error: " + e.message);
  } finally {
    btn.disabled = false;
  }
});

// ── QR tab ────────────────────────────────────────────────────────────────────

const qrTable = createPaginatedTable(
  document.getElementById("qr-tbody"),
  document.getElementById("qr-pagination")
);
qrTable.reset();

document.getElementById("qr-add-row").addEventListener("click",  () => qrTable.addRow());
document.getElementById("qr-paste-btn").addEventListener("click", () => openPasteModal((r) => qrTable.appendRows(r)));
document.getElementById("qr-clear-btn").addEventListener("click", () => {
  qrTable.reset();
  clearStatus(document.getElementById("qr-status"));
});

document.getElementById("qr-generate-btn").addEventListener("click", async () => {
  const statusEl = document.getElementById("qr-status");
  const btn      = document.getElementById("qr-generate-btn");

  const { students, errors } = qrTable.collect();
  if (errors.length)   { setStatus(statusEl, "error", errors[0]); return; }
  if (!students.length){ setStatus(statusEl, "error", "Add at least one student."); return; }

  const college = document.getElementById("qr-college").value.trim();
  const level   = document.getElementById("qr-level").value.trim();

  btn.disabled = true;
  setStatus(statusEl, "loading", "Generating QR codes…");

  try {
    const res = await fetch(`${API_BASE}/api/tools/generate-qr`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ students, college, level }),
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
