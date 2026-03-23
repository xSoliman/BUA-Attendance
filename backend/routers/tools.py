"""
API endpoints for the GUI tools:
  POST /api/tools/generate-attendance  -> .xlsx download
  POST /api/tools/generate-qr          -> .zip download
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel

from core.attendance import generate_attendance_sheet
from core.qr_generator import generate_qr_zip

router = APIRouter(prefix="/api/tools", tags=["tools"])


class Student(BaseModel):
    id: str
    name: str
    section: str = ""


class AttendanceRequest(BaseModel):
    courses: list[dict]   # [{name: str, students: [{id, name, section}]}]
    output_name: str = "Attendance"


class QRRequest(BaseModel):
    students: list[Student]
    college: str = ""
    level: str = ""


@router.post("/generate-attendance")
def generate_attendance(req: AttendanceRequest):
    if not req.courses or not any(c.get("students") for c in req.courses):
        raise HTTPException(status_code=400, detail="No students provided.")

    xlsx_bytes = generate_attendance_sheet(req.courses)

    filename = req.output_name.strip() or "Attendance"
    filename = "".join(c for c in filename if c.isalnum() or c in " _-").strip()
    if not filename:
        filename = "Attendance"

    return Response(
        content=xlsx_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": f'attachment; filename="{filename}.xlsx"'},
    )


@router.post("/generate-qr")
def generate_qr(req: QRRequest):
    if not req.students:
        raise HTTPException(status_code=400, detail="No students provided.")

    student_dicts = [s.model_dump() for s in req.students]
    zip_bytes = generate_qr_zip(
        student_dicts,
        college=req.college.strip(),
        level=req.level.strip(),
    )

    return Response(
        content=zip_bytes,
        media_type="application/zip",
        headers={"Content-Disposition": 'attachment; filename="qr_codes.zip"'},
    )
