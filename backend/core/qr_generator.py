"""
Core QR code generation logic.
Supports Arabic text via arabic-reshaper + python-bidi.
Directory structure: [college/]group/section/id.png
"""

import io
import re
import zipfile

import qrcode
from PIL import Image, ImageDraw, ImageFont

# Arabic reshaping — graceful fallback if libs not installed
try:
    import arabic_reshaper
    from bidi.algorithm import get_display as bidi_display
    _ARABIC_SUPPORT = True
except ImportError:
    _ARABIC_SUPPORT = False


# Font search order — prefer Noto Arabic for full Arabic coverage
_FONT_PATHS = [
    "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "C:\\Windows\\Fonts\\arial.ttf",
    "C:\\Windows\\Fonts\\tahoma.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
]

_font_cache: dict = {}


def _load_font(size: int = 16) -> ImageFont.FreeTypeFont:
    if size in _font_cache:
        return _font_cache[size]
    for path in _FONT_PATHS:
        try:
            f = ImageFont.truetype(path, size)
            _font_cache[size] = f
            return f
        except Exception:
            continue
    # Last resort — PIL built-in (no Arabic, but won't crash)
    return ImageFont.load_default()


def _prepare_text(text: str) -> str:
    """Reshape + apply bidi algorithm so Arabic renders correctly in PIL."""
    if not _ARABIC_SUPPORT:
        return text
    try:
        reshaped = arabic_reshaper.reshape(text)
        return bidi_display(reshaped)
    except Exception:
        return text


def _extract_group(section: str) -> str:
    """
    Extract group letter(s) from a section code.
    'A1' -> 'A',  'B12' -> 'B',  'AB3' -> 'AB'
    """
    match = re.match(r"^([A-Za-z]+)", section.strip())
    return match.group(1).upper() if match else "Unknown"


def _make_qr_image(student_id: str, student_name: str) -> Image.Image:
    """Generate a QR PNG with a two-line footer (name + ID). Arabic-safe."""
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

    name_text = _prepare_text(str(student_name))
    id_text   = f"ID: {student_id}"

    def centered_x(text):
        bbox = draw.textbbox((0, 0), text, font=font)
        return (qr_w - (bbox[2] - bbox[0])) // 2

    draw.text((centered_x(name_text), qr_h + 15), name_text, fill="black", font=font)
    draw.text((centered_x(id_text),   qr_h + 42), id_text,   fill="black", font=font)

    return final


def generate_qr_zip(students: list[dict], college: str = "") -> bytes:
    """
    Generate a zip of QR PNGs.

    Path inside zip:
      [college/]<group>/<section>/<id>.png

    Group is derived automatically from the section code (leading letters).
    """
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
        for student in students:
            student_id   = str(student.get("id",      "")).strip()
            student_name = str(student.get("name",    "")).strip()
            section      = str(student.get("section", "")).strip()

            if not student_id or student_id == "nan":
                continue

            group = _extract_group(section) if section else "Unknown"

            parts = []
            if college:
                parts.append(college)
            parts.append(group)
            if section:
                parts.append(section)
            parts.append(f"{student_id}.png")
            zip_path = "/".join(parts)

            img = _make_qr_image(student_id, student_name)
            img_buf = io.BytesIO()
            img.save(img_buf, format="PNG")
            zf.writestr(zip_path, img_buf.getvalue())

    buf.seek(0)
    return buf.read()
