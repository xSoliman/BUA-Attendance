"""
Core QR code generation logic.
Rewritten from scripts/qr_generator/generate_qr.py
with same logic, exposed as callable functions (no CLI dependency).
"""

import io
import zipfile
import qrcode
from PIL import Image, ImageDraw, ImageFont


# Arabic-capable font search paths (same as original script)
_FONT_PATHS = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    "C:\\Windows\\Fonts\\arial.ttf",
    "C:\\Windows\\Fonts\\tahoma.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
]


def _load_font(size: int = 16):
    for path in _FONT_PATHS:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            continue
    return ImageFont.load_default()


def _make_qr_image(student_id: str, student_name: str) -> Image.Image:
    """Generate QR image with footer. Same logic as original generate_qr.py."""
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(f"{student_name} - {student_id}")
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    qr_w, qr_h = qr_img.size
    footer_h = 80
    final = Image.new("RGB", (qr_w, qr_h + footer_h), "white")
    final.paste(qr_img, (0, 0))

    draw = ImageDraw.Draw(final)
    font = _load_font(16)

    name_text = str(student_name)
    id_text = f"ID: {student_id}"

    name_bbox = draw.textbbox((0, 0), name_text, font=font)
    name_w = name_bbox[2] - name_bbox[0]
    draw.text(((qr_w - name_w) // 2, qr_h + 15), name_text, fill="black", font=font)

    id_bbox = draw.textbbox((0, 0), id_text, font=font)
    id_w = id_bbox[2] - id_bbox[0]
    draw.text(((qr_w - id_w) // 2, qr_h + 40), id_text, fill="black", font=font)

    return final


def generate_qr_zip(
    students: list[dict],
    sheet_name: str = "",
    tab_name: str = "",
) -> bytes:
    """
    Generate a zip archive of QR code PNGs for a list of students.

    Each student dict must have: id, name
    Optional key: section

    Directory structure inside zip:
      [sheet_name/][tab_name/][section/]<id>.png

    Returns raw bytes of the .zip file.
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for student in students:
            student_id = str(student.get("id", "")).strip()
            student_name = str(student.get("name", "")).strip()
            section = str(student.get("section", "")).strip()

            if not student_id or student_id == "nan":
                continue

            img = _make_qr_image(student_id, student_name)

            # Build path inside zip
            parts = []
            if sheet_name:
                parts.append(sheet_name)
            if tab_name:
                parts.append(tab_name)
            if section:
                parts.append(section)
            parts.append(f"{student_id}.png")
            zip_path = "/".join(parts)

            img_buf = io.BytesIO()
            img.save(img_buf, format="PNG")
            zf.writestr(zip_path, img_buf.getvalue())

    buf.seek(0)
    return buf.read()
