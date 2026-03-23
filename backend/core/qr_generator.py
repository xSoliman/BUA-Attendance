"""
Core QR code generation logic.
- Bundles NotoNaskhArabic-Regular.ttf for guaranteed Arabic support on any server.
- Uses arabic-reshaper + python-bidi for correct Arabic glyph shaping.
- Zip path: [college/][level/]group/section/id.png
  Group is derived automatically from the leading letter(s) of the section code.
"""

import io
import os
import re
import zipfile

import qrcode
from PIL import Image, ImageDraw, ImageFont

# ── Arabic support ────────────────────────────────────────────────────────────
try:
    import arabic_reshaper
    from bidi.algorithm import get_display as bidi_display
    _ARABIC_SUPPORT = True
except ImportError:
    _ARABIC_SUPPORT = False

# ── Bundled font (lives next to this file in the repo) ────────────────────────
_HERE = os.path.dirname(os.path.abspath(__file__))
_BUNDLED_FONT = os.path.join(_HERE, "NotoNaskhArabic-Regular.ttf")

# System font fallbacks (used only if bundled font is somehow missing)
_SYSTEM_FONTS = [
    "/usr/share/fonts/truetype/noto/NotoNaskhArabic-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSansArabic-Regular.ttf",
    "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "C:\\Windows\\Fonts\\arial.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
]

_font_cache: dict = {}


def _load_font(size: int = 16) -> ImageFont.FreeTypeFont:
    if size in _font_cache:
        return _font_cache[size]

    # Try bundled font first — guaranteed to exist in the repo
    candidates = [_BUNDLED_FONT] + _SYSTEM_FONTS
    for path in candidates:
        try:
            f = ImageFont.truetype(path, size)
            _font_cache[size] = f
            return f
        except Exception:
            continue

    return ImageFont.load_default()


def _prepare_text(text: str) -> str:
    """Reshape Arabic text and apply bidi so PIL renders it correctly."""
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

    def centered_x(text: str) -> int:
        bbox = draw.textbbox((0, 0), text, font=font)
        return (qr_w - (bbox[2] - bbox[0])) // 2

    draw.text((centered_x(name_text), qr_h + 15), name_text, fill="black", font=font)
    draw.text((centered_x(id_text),   qr_h + 42), id_text,   fill="black", font=font)

    return final


def generate_qr_zip(
    students: list[dict],
    college: str = "",
    level: str = "",
) -> bytes:
    """
    Generate a zip of QR PNGs.

    Zip path structure:
      [college/][level/]<group>/<section>/<id>.png

    Group is derived automatically from the section's leading letters.
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
            if level:
                parts.append(level)
            parts.append(group)
            if section:
                parts.append(section)
            parts.append(f"{student_id}.png")

            img = _make_qr_image(student_id, student_name)
            img_buf = io.BytesIO()
            img.save(img_buf, format="PNG")
            zf.writestr("/".join(parts), img_buf.getvalue())

    buf.seek(0)
    return buf.read()
