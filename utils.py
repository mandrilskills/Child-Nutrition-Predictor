import datetime
import io
import re

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT, TA_JUSTIFY

# ---------------------------------------------------------------------------
# WHO PEDIATRIC REFERENCE STANDARDS
# ---------------------------------------------------------------------------
def get_ideal_metrics(age, gender):
    """
    Returns approximate WHO median (Weight in kg, Height in cm) for a given age and gender.
    Format: age: (Male Weight, Male Height, Female Weight, Female Height)
    """
    ideals = {
        0: (7.3, 67.6, 6.7, 65.7),
        1: (10.3, 75.7, 9.5, 74.0),
        2: (12.2, 86.8, 11.5, 85.5),
        3: (14.3, 95.2, 13.9, 94.0),
        4: (16.3, 102.3, 15.8, 100.3),
        5: (18.3, 109.0, 18.2, 107.9),
        6: (20.5, 115.5, 20.2, 114.6),
        7: (22.9, 121.7, 22.8, 120.6),
        8: (25.4, 127.3, 25.6, 126.6),
        9: (28.1, 132.6, 28.6, 132.2),
        10: (31.2, 137.8, 31.9, 138.4),
        11: (34.8, 143.1, 35.8, 144.0),
        12: (39.2, 149.1, 40.5, 149.8),
        13: (44.6, 156.0, 45.4, 155.4),
        14: (50.8, 163.2, 49.8, 159.8),
        15: (56.7, 170.1, 53.0, 161.7)
    }
    safe_age = int(max(0, min(age, 15)))
    m_w, m_h, f_w, f_h = ideals[safe_age]
    
    if gender == "Male":
        return m_w, m_h
    else:
        return f_w, f_h

# ---------------------------------------------------------------------------
# Colour Palette  (monochromatic / near-monochromatic — clinical feel)
# ---------------------------------------------------------------------------
C_BLACK       = colors.HexColor("#1A1A2E")   # Near-black for headings
C_DARK        = colors.HexColor("#2C3E50")   # Body text
C_MID         = colors.HexColor("#5D6D7E")   # Captions / sub-labels
C_LIGHT       = colors.HexColor("#AEB6BF")   # Dividers / muted elements
C_BG_STRIPE   = colors.HexColor("#F4F6F7")   # Table row stripe (very light grey)
C_ACCENT      = colors.HexColor("#1A5276")   # Section header bar (deep navy)
C_ACCENT_LITE = colors.HexColor("#D6EAF8")   # Light accent fill
C_WHITE       = colors.white

# Status-specific colours (kept minimal)
C_STATUS_OK   = colors.HexColor("#1E8449")   # Healthy
C_STATUS_WARN = colors.HexColor("#B7950B")   # At Risk
C_STATUS_CRIT = colors.HexColor("#922B21")   # Malnourished


# ---------------------------------------------------------------------------
# Text Sanitisation
# ---------------------------------------------------------------------------
def sanitize_for_pdf(text: str) -> str:
    emoji_pattern = re.compile(
        "["
        u"\U0001F600-\U0001F64F"
        u"\U0001F300-\U0001F5FF"
        u"\U0001F680-\U0001F6FF"
        u"\U0001F1E0-\U0001F1FF"
        u"\U00002702-\U000027B0"
        u"\U000024C2-\U0001F251"
        u"\u2600-\u26FF"
        u"\u2700-\u27BF"
        "]+", flags=re.UNICODE
    )
    text = emoji_pattern.sub("", text)

    replacements = {
        "\u2019": "'", "\u2018": "'",
        "\u201C": '"', "\u201D": '"',
        "\u2013": "-", "\u2014": "-",
        "\u2022": "-", "\u2023": "-",
        "\u25CF": "-", "\u25E6": "-",
        "\u2713": "[OK]", "\u2714": "[OK]",
        "\u2715": "[X]",  "\u2716": "[X]",
        "\u00A0": " ", "⭐": "", "🛡️": "", "✅": "", "⚠️": ""
    }
    for src, tgt in replacements.items():
        text = text.replace(src, tgt)

    return text.encode("latin-1", "replace").decode("latin-1")


# ---------------------------------------------------------------------------
# Style Sheet
# ---------------------------------------------------------------------------
def _build_styles():
    base = getSampleStyleSheet()
    styles = {}
    
    styles["doc_title"] = ParagraphStyle("doc_title", fontName="Helvetica-Bold", fontSize=18, textColor=C_WHITE, alignment=TA_CENTER, spaceAfter=2)
    styles["doc_subtitle"] = ParagraphStyle("doc_subtitle", fontName="Helvetica", fontSize=9, textColor=colors.HexColor("#D5D8DC"), alignment=TA_CENTER, spaceAfter=0)
    styles["section_heading"] = ParagraphStyle("section_heading", fontName="Helvetica-Bold", fontSize=10, textColor=C_WHITE, alignment=TA_LEFT, leftIndent=4, spaceBefore=0, spaceAfter=0)
    styles["label"] = ParagraphStyle("label", fontName="Helvetica-Bold", fontSize=9, textColor=C_DARK, alignment=TA_LEFT)
    styles["value"] = ParagraphStyle
