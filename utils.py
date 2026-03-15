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
    styles["value"] = ParagraphStyle("value", fontName="Helvetica", fontSize=9, textColor=C_DARK, alignment=TA_LEFT)
    styles["body"] = ParagraphStyle("body", fontName="Helvetica", fontSize=9, textColor=C_DARK, alignment=TA_JUSTIFY, leading=14, spaceBefore=2, spaceAfter=2)
    styles["caption"] = ParagraphStyle("caption", fontName="Helvetica-Oblique", fontSize=8, textColor=C_MID, alignment=TA_LEFT)
    styles["footer"] = ParagraphStyle("footer", fontName="Helvetica", fontSize=7.5, textColor=C_MID, alignment=TA_CENTER)
    styles["status_ok"] = ParagraphStyle("status_ok", fontName="Helvetica-Bold", fontSize=11, textColor=C_STATUS_OK, alignment=TA_CENTER)
    styles["status_warn"] = ParagraphStyle("status_warn", fontName="Helvetica-Bold", fontSize=11, textColor=C_STATUS_WARN, alignment=TA_CENTER)
    styles["status_crit"] = ParagraphStyle("status_crit", fontName="Helvetica-Bold", fontSize=11, textColor=C_STATUS_CRIT, alignment=TA_CENTER)
    styles["table_header"] = ParagraphStyle("table_header", fontName="Helvetica-Bold", fontSize=9, textColor=C_WHITE, alignment=TA_CENTER)
    styles["table_cell_center"] = ParagraphStyle("table_cell_center", fontName="Helvetica", fontSize=9, textColor=C_DARK, alignment=TA_CENTER)

    return styles

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def _section_banner(text: str, styles) -> Table:
    cell = Paragraph(text, styles["section_heading"])
    tbl = Table([[cell]], colWidths=[170 * mm])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), C_ACCENT),
        ("TOPPADDING",    (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
    ]))
    return tbl

def _kv_table(rows: list, styles) -> Table:
    col_w = [55 * mm, 115 * mm]
    table_data = [[Paragraph(str(k), styles["label"]), Paragraph(str(v), styles["value"])] for k, v in rows]
    style_cmds = [
        ("GRID",        (0, 0), (-1, -1), 0.4, C_LIGHT),
        ("TOPPADDING",  (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0,0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",(0, 0), (-1, -1), 8),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
    ]
    for i in range(len(table_data)):
        if i % 2 == 1:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), C_BG_STRIPE))

    tbl = Table(table_data, colWidths=col_w)
    tbl.setStyle(TableStyle(style_cmds))
    return tbl

def _comparative_table(data: list, styles) -> Table:
    headers = ["Metric", "Actual Value", "WHO Ideal", "Variance"]
    table_data = [[Paragraph(h, styles["table_header"]) for h in headers]]

    for row in data:
        table_data.append([
            Paragraph(str(row["Metric"]), styles["table_cell_center"]),
            Paragraph(str(row["Actual"]), styles["table_cell_center"]),
            Paragraph(str(row["Ideal"]), styles["table_cell_center"]),
            Paragraph(str(row["Variance"]), styles["table_cell_center"])
        ])

    col_w = [42.5 * mm] * 4
    tbl = Table(table_data, colWidths=col_w)
    
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), C_ACCENT),
        ("GRID", (0, 0), (-1, -1), 0.5, C_LIGHT),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]
    
    for i in range(1, len(table_data)):
        if i % 2 == 0:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), C_BG_STRIPE))

    tbl.setStyle(TableStyle(style_cmds))
    return tbl

def _metrics_row(metrics: list, styles) -> Table:
    col_w = [170 * mm / len(metrics)] * len(metrics)
    cells = []
    for label, value in metrics:
        cell_content = [
            [Paragraph(str(value), ParagraphStyle("metric_val", fontName="Helvetica-Bold", fontSize=14, textColor=C_ACCENT, alignment=TA_CENTER))],
            [Paragraph(str(label), ParagraphStyle("metric_lbl", fontName="Helvetica", fontSize=7.5, textColor=C_MID, alignment=TA_CENTER))],
        ]
        inner = Table(cell_content, colWidths=[col_w[0] - 2 * mm])
        inner.setStyle(TableStyle([
            ("TOPPADDING",    (0, 0), (-1, -1), 3),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ("LEFTPADDING",   (0, 0), (-1, -1), 0),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ]))
        cells.append(inner)

    tbl = Table([cells], colWidths=col_w)
    tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), C_ACCENT_LITE),
        ("BOX",           (0, 0), (-1, -1), 0.5, C_ACCENT),
        ("INNERGRID",     (0, 0), (-1, -1), 0.5, C_ACCENT),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING",   (0, 0), (-1, -1), 4),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 4),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return tbl

def _ai_text_block(raw_text: str, styles) -> list:
    elements = []
    for line in sanitize_for_pdf(raw_text).splitlines():
        line = line.strip()
        if not line:
            elements.append(Spacer(1, 3))
            continue
        if line.startswith("-") or line.startswith("*"):
            bullet_style = ParagraphStyle("bullet", fontName="Helvetica", fontSize=9, textColor=C_DARK, leftIndent=12, leading=14, spaceBefore=1, spaceAfter=1)
            elements.append(Paragraph(line, bullet_style))
        else:
            elements.append(Paragraph(line, styles["body"]))
    return elements

def _draw_page_frame(canvas, doc):
    canvas.saveState()
    page_w, page_h = A4

    banner_h = 28 * mm
    canvas.setFillColor(C_BLACK)
    canvas.rect(0, page_h - banner_h, page_w, banner_h, fill=1, stroke=0)

    canvas.setFillColor(C_WHITE)
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawCentredString(page_w / 2, page_h - 14 * mm, "Pediatric Nutritional Assessment Report")

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#AEB6BF"))
    canvas.drawCentredString(page_w / 2, page_h - 21 * mm, f"System: Machine Learning & Agentic AI Framework   |   Generated: {datetime.datetime.now().strftime('%d %b %Y, %H:%M')}   |   CONFIDENTIAL")

    canvas.setStrokeColor(C_ACCENT)
    canvas.setLineWidth(2)
    canvas.line(0, page_h - banner_h, page_w, page_h - banner_h)

    footer_y = 12 * mm
    canvas.setStrokeColor(C_LIGHT)
    canvas.setLineWidth(0.5)
    canvas.line(15 * mm, footer_y, page_w - 15 * mm, footer_y)

    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(C_MID)
    canvas.drawString(15 * mm, footer_y - 5 * mm, "FOR CLINICAL USE ONLY  |  Not a substitute for professional medical advice.")
    canvas.drawRightString(page_w - 15 * mm, footer_y - 5 * mm, f"Page {doc.page}")

    canvas.restoreState()

# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def generate_pdf_report(
    patient_data: dict,
    comparative_data: list,
    ml_prediction: str,
    explainer_text: str,
    unicef_text: str,
    audit_text: str,
) -> bytes:
    buffer = io.BytesIO()
    styles = _build_styles()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=38 * mm, 
        bottomMargin=22 * mm,
        title="Pediatric Nutritional Assessment Report",
    )

    story = []
    story.append(Spacer(1, 4 * mm))

    # SECTION 1 — Patient Demographics
    story.append(_section_banner("1.  Patient Demographics & Clinical Context", styles))
    story.append(Spacer(1, 3 * mm))
    
    display_keys = ["Age", "Gender", "Regular Meals", "Eats Veggies", "Clean Water", "Region", "Setting"]
    kv_rows = [(k, patient_data[k]) for k in display_keys if k in patient_data]
    story.append(KeepTogether([_kv_table(kv_rows, styles)]))
    story.append(Spacer(1, 5 * mm))

    # SECTION 2 — WHO Anthropometric Comparison
    story.append(_section_banner("2.  Clinical Anthropometric Comparison (WHO Standards)", styles))
    story.append(Spacer(1, 3 * mm))
    story.append(KeepTogether([_comparative_table(comparative_data, styles)]))
    story.append(Spacer(1, 5 * mm))

    # SECTION 3 — ML Diagnostic Summary
    story.append(_section_banner("3.  Deterministic ML Diagnostic Summary", styles))
    story.append(Spacer(1, 3 * mm))

    bmi_val = patient_data.get("Calculated BMI", "—")
    budget_val = patient_data.get("Daily Budget (INR)", "—")
    
    metrics = [
        ("Patient Age", f"{patient_data.get('Age', '—')} yrs"),
        ("BMI Score", str(bmi_val)),
        ("Daily Budget", f"INR {budget_val}"),
        ("Region", str(patient_data.get("Region", "—"))),
    ]
    story.append(_metrics_row(metrics, styles))
    story.append(Spacer(1, 4 * mm))

    pred_upper = ml_prediction.upper()
    if pred_upper == "HEALTHY":
        status_style = styles["status_ok"]
    elif pred_upper == "AT RISK":
        status_style = styles["status_warn"]
    else:
        status_style = styles["status_crit"]

    status_cell = Paragraph(f"DIAGNOSTIC STATUS:  {pred_upper}", status_style)
    status_tbl = Table([[status_cell]], colWidths=[170 * mm])
    status_tbl.setStyle(TableStyle([
        ("BOX",           (0, 0), (-1, -1), 1, C_LIGHT),
        ("BACKGROUND",    (0, 0), (-1, -1), C_BG_STRIPE),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(KeepTogether([status_tbl]))
    story.append(Spacer(1, 5 * mm))

    # SECTION 4 — AI Clinical Analysis (No KeepTogether to avoid loop errors)
    story.append(_section_banner("4.  AI Clinical Analysis  —  Explainer Agent", styles))
    story.append(Spacer(1, 3 * mm))
    ai_blocks = _ai_text_block(explainer_text, styles)
    if ai_blocks:
        story.extend(ai_blocks)  
    else:
        story.append(Paragraph("No output generated.", styles["body"]))
    story.append(Spacer(1, 5 * mm))

    # SECTION 5 — Socio-Economic Intervention (No KeepTogether to avoid loop errors)
    story.append(_section_banner("5.  Socio-Economically Constrained Intervention  —  Policy Agent", styles))
    story.append(Spacer(1, 3 * mm))
    ai_blocks = _ai_text_block(unicef_text, styles)
    if ai_blocks:
        story.extend(ai_blocks)
    else:
        story.append(Paragraph("No output generated.", styles["body"]))
    story.append(Spacer(1, 5 * mm))

    # SECTION 6 — CMO Safety Audit (No KeepTogether to avoid loop errors)
    story.append(_section_banner("6.  CMO Guardrail Safety Audit  —  Critic Agent", styles))
    story.append(Spacer(1, 3 * mm))

    audit_elements = _ai_text_block(audit_text, styles)
    if audit_elements:
        story.extend(audit_elements)
    
    audit_upper = audit_text.upper()
    if "VERIFIED SAFE" in audit_upper:
        verdict_text = "AUDIT VERDICT:  STATUS VERIFIED SAFE"
        verdict_color = C_STATUS_OK
        verdict_bg    = colors.HexColor("#E9F7EF")
    else:
        verdict_text = "AUDIT VERDICT:  FLAGGED - REQUIRES HUMAN DOCTOR REVIEW"
        verdict_color = C_STATUS_CRIT
        verdict_bg    = colors.HexColor("#FDEDEC")

    verdict_style = ParagraphStyle("verdict", fontName="Helvetica-Bold", fontSize=9.5, textColor=verdict_color, alignment=TA_CENTER)
    verdict_cell = Paragraph(verdict_text, verdict_style)
    verdict_tbl = Table([[verdict_cell]], colWidths=[170 * mm])
    verdict_tbl.setStyle(TableStyle([
        ("BOX",           (0, 0), (-1, -1), 1, verdict_color),
        ("BACKGROUND",    (0, 0), (-1, -1), verdict_bg),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    story.append(Spacer(1, 4 * mm))
    story.append(KeepTogether([verdict_tbl]))
    story.append(Spacer(1, 6 * mm))

    # FOOTER NOTE
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_LIGHT))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(
        "This report is generated by an automated AI-assisted system and is intended solely as a clinical "
        "decision-support tool. It does not constitute a medical diagnosis or replace the judgment of a "
        "licensed healthcare professional. All recommendations must be reviewed and validated by a "
        "qualified clinician before implementation.", styles["caption"]))

    doc.build(story, onFirstPage=_draw_page_frame, onLaterPages=_draw_page_frame)
    return buffer.getvalue()
