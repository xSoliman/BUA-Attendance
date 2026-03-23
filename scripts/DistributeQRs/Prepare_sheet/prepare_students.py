"""
prepare_students.py
────────────────────────────────────────────────────────────────────────────────
Replaces the three-step workflow (process_data → merge_sections → manual copy)
with a single script that:

  1. Reads all.csv  (columns: "ID number", "Email address")
  2. Reads sections.xlsx  (columns: ID, Name, Section — one or more tabs)
  3. Asks which sections to include (or "all")
  4. Maps each student ID → email
  5. Writes ../students.xlsx  (columns: ID, Email, Section)
     ready for send_qr.py with no further steps

Usage:
    python prepare_students.py

Input files (must be in the same directory as this script):
    all.csv        — full student registry with IDs and emails
    sections.xlsx  — target students with ID / Name / Section columns
"""

import os
import sys
import pandas as pd
from pathlib import Path

# ─── paths ────────────────────────────────────────────────────────────────────
HERE        = Path(__file__).parent
ALL_CSV     = HERE / "all.csv"
SECTIONS_XL = HERE / "sections.xlsx"
OUTPUT_FILE = HERE.parent / "students.xlsx"   # written directly for send_qr.py
REPORT_FILE = HERE / "report.txt"


def load_id_email_map() -> dict:
    """Load all.csv and return {id_str: email} mapping."""
    df = pd.read_csv(ALL_CSV, low_memory=False)

    id_col    = "ID number"
    email_col = "Email address"

    if id_col not in df.columns or email_col not in df.columns:
        print(f"Error: all.csv must have '{id_col}' and '{email_col}' columns.")
        print(f"Found: {df.columns.tolist()}")
        sys.exit(1)

    df[id_col] = df[id_col].astype(str).str.strip().str.replace(".0", "", regex=False)
    return dict(zip(df[id_col], df[email_col]))


def load_all_students() -> pd.DataFrame:
    """
    Read every tab of sections.xlsx.
    Returns a combined DataFrame with columns: ID, Name, Section.
    """
    all_sheets = pd.read_excel(SECTIONS_XL, sheet_name=None)
    frames = []

    for sheet_name, df in all_sheets.items():
        if "ID" not in df.columns or "Section" not in df.columns:
            print(f"  Skipping tab '{sheet_name}': missing ID or Section column.")
            continue
        df = df.copy()
        df["ID"] = df["ID"].astype(str).str.strip().str.replace(".0", "", regex=False)
        df["Section"] = df["Section"].astype(str).str.strip()
        if "Name" not in df.columns:
            df["Name"] = ""
        frames.append(df[["ID", "Name", "Section"]])

    if not frames:
        print("Error: no usable tabs found in sections.xlsx.")
        sys.exit(1)

    combined = pd.concat(frames, ignore_index=True)
    combined = combined[combined["Section"].str.strip() != ""]
    return combined


def pick_sections(available: list[str]) -> list[str]:
    """Interactively ask the user which sections to include."""
    print("\nAvailable sections:")
    for s in sorted(available):
        print(f"  {s}")

    print('\nEnter section codes separated by spaces, or type "all" to include everything.')
    raw = input("Sections: ").strip()

    if raw.lower() == "all":
        return sorted(available)

    chosen = [s.strip().upper() for s in raw.split() if s.strip()]
    unknown = [s for s in chosen if s not in [a.upper() for a in available]]
    if unknown:
        print(f"Warning: these sections were not found and will be skipped: {unknown}")

    # match case-insensitively against available list
    avail_upper = {a.upper(): a for a in available}
    return [avail_upper[s] for s in chosen if s in avail_upper]


def main():
    # ── validate inputs ───────────────────────────────────────────────────────
    for path, label in [(ALL_CSV, "all.csv"), (SECTIONS_XL, "sections.xlsx")]:
        if not path.exists():
            print(f"Error: {label} not found at {path}")
            sys.exit(1)

    print("Reading all.csv …")
    id_to_email = load_id_email_map()
    print(f"  Loaded {len(id_to_email):,} email mappings.")

    print("Reading sections.xlsx …")
    students_df = load_all_students()
    print(f"  Loaded {len(students_df):,} students across "
          f"{students_df['Section'].nunique()} sections.")

    # ── section selection ─────────────────────────────────────────────────────
    available = students_df["Section"].unique().tolist()
    chosen    = pick_sections(available)

    if not chosen:
        print("No valid sections selected. Exiting.")
        sys.exit(0)

    filtered = students_df[students_df["Section"].isin(chosen)]
    print(f"\nSelected {len(filtered):,} students from {len(chosen)} section(s): "
          f"{', '.join(chosen)}")

    # ── map IDs → emails ──────────────────────────────────────────────────────
    rows    = []
    found   = []   # (id, name, section, email)
    missing = []   # (id, name, section)

    for _, row in filtered.iterrows():
        sid  = row["ID"]
        name = row.get("Name", "Unknown")
        sec  = row["Section"]
        if sid in id_to_email:
            email = id_to_email[sid]
            rows.append({"ID": sid, "Email": email, "Section": sec})
            found.append((sid, name, sec, email))
        else:
            missing.append((sid, name, sec))

    # ── report ────────────────────────────────────────────────────────────────
    sep = "-" * 60
    lines = []

    lines.append("PREPARE STUDENTS — REPORT")
    lines.append(sep)
    lines.append(f"Sections selected : {', '.join(chosen)}")
    lines.append(f"Total students    : {len(filtered):,}")
    lines.append(f"Found (with email): {len(found):,}")
    lines.append(f"Missing (no email): {len(missing):,}")
    lines.append("")

    lines.append(f"✅ FOUND ({len(found)})")
    lines.append(sep)
    for sid, name, sec, email in found:
        lines.append(f"  ID: {sid:<14}  Section: {sec:<6}  Email: {email:<40}  Name: {name}")

    lines.append("")
    lines.append(f"❌ MISSING ({len(missing)})")
    lines.append(sep)
    if missing:
        for sid, name, sec in missing:
            lines.append(f"  ID: {sid:<14}  Section: {sec:<6}  Name: {name}")
    else:
        lines.append("  (none — all students matched)")

    report_text = "\n".join(lines)

    # Print summary to console
    print(f"\n{'='*60}")
    print(f"  Found   : {len(found):,}")
    print(f"  Missing : {len(missing):,}")
    print(f"{'='*60}")
    if missing:
        print(f"\n⚠️  Missing students (no email found):")
        for sid, name, sec in missing:
            print(f"   ID: {sid}  Section: {sec}  Name: {name}")

    # Always write the full report file
    REPORT_FILE.write_text(report_text, encoding="utf-8")
    print(f"\n📄 Full report saved → {REPORT_FILE}")

    if not rows:
        print("Error: no students with emails found. Nothing to write.")
        sys.exit(1)

    # ── write output ──────────────────────────────────────────────────────────
    out_df = pd.DataFrame(rows)
    out_df.to_excel(OUTPUT_FILE, index=False)
    print(f"\n✅ Written {len(out_df):,} rows → {OUTPUT_FILE}")
    print("   Ready to run send_qr.py.")


if __name__ == "__main__":
    main()
