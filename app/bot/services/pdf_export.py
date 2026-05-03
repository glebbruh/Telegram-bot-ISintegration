from io import BytesIO
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

from bot.formatters.checks import build_checks_status_legend_for_pdf, format_checks_response_for_pdf
from bot.formatters.tasks import format_tasks_response

FONT_NAME = "NotoSans"
FONT_NAME_BOLD = "NotoSans-Bold"

BASE_DIR = Path(__file__).resolve().parents[1]
FONT_PATH = BASE_DIR / "services" / "fonts" / "NotoSans-Regular.ttf"
FONT_PATH_BOLD = BASE_DIR / "services" / "fonts" / "NotoSans-Bold.ttf"

def _register_font():
    try:
        pdfmetrics.getFont(FONT_NAME)
        return
    except KeyError:
        if not FONT_PATH.exists():
            raise RuntimeError(f"Шрифт не найден: {FONT_PATH}")
        pdfmetrics.registerFont(TTFont(FONT_NAME, str(FONT_PATH)))
    try:
        pdfmetrics.getFont(FONT_NAME_BOLD)
    except KeyError:
        if not FONT_PATH_BOLD.exists():
            raise RuntimeError(f"Шрифт не найден: {FONT_PATH_BOLD}")
        pdfmetrics.registerFont(TTFont(FONT_NAME_BOLD, str(FONT_PATH_BOLD)))


def _draw_multiline_text(pdf: canvas.Canvas, text: str, x: float, y: float, line_height: float, bottom_margin: float):
    for line in text.splitlines():
        if y < bottom_margin:
            pdf.showPage()
            pdf.setFont(FONT_NAME, 11)
            y = A4[1] - 20 * mm
        pdf.drawString(x, y, line)
        y -= line_height
    return y

def build_checks_pdf_bytes(response_data: dict) -> bytes:
    _register_font()
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setTitle("checks_result")
    width, height = A4
    left_margin = 15 * mm
    top_y = height - 20 * mm
    bottom_margin = 15 * mm
    line_height = 7 * mm
    pdf.setFont(FONT_NAME, 14)
    pdf.drawString(left_margin, top_y, "Результаты проверок")
    pdf.setFont(FONT_NAME, 11)
    y = top_y - 12 * mm
    y = _draw_multiline_text(
        pdf,
        build_checks_status_legend_for_pdf(),
        left_margin,
        y,
        line_height,
        bottom_margin,
    )
    y -= 5 * mm
    checks_text = format_checks_response_for_pdf(response_data)
    _draw_multiline_text(
        pdf,
        checks_text,
        left_margin,
        y,
        line_height,
        bottom_margin,
    )
    pdf.save()
    return buffer.getvalue()

def build_tasks_pdf_bytes(response_data: dict) -> bytes:
    _register_font()
    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    pdf.setTitle("tasks_result")
    width, height = A4
    left_margin = 15 * mm
    top_y = height - 20 * mm
    bottom_margin = 15 * mm
    line_height = 7 * mm
    pdf.setFont(FONT_NAME, 14)
    pdf.drawString(left_margin, top_y, "Результаты задач")
    pdf.setFont(FONT_NAME, 11)
    y = top_y - 12 * mm
    tasks_text = format_tasks_response(response_data)
    _draw_multiline_text(
        pdf,
        tasks_text,
        left_margin,
        y,
        line_height,
        bottom_margin,
    )
    pdf.save()
    return buffer.getvalue()