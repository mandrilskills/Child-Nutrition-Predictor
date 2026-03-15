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
    """
    Strip emoji and replace non-latin unicode characters with safe equivalents.
    ReportLab handles unicode better than fpdf, but we still clean aggressively.
    """
    # Remove emoji / symbols
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
        "\u00A0": " ",
    }
    for src, tgt in replacements.items():
        text = text.replace(src, tgt)

    # Strip any remaining non-latin-1 characters
    return text.encode("latin-1", "replace").decode("latin-1")


# ---------------------------------------------------------------------------
# Style Sheet
# ---------------------------------------------------------------------------
def _build_styles():
    base = getSampleStyleSheet()

    styles = {}

    styles["doc_title"] = ParagraphStyle(
        "doc_title",
        fontName="Helvetica-Bold",
        fontSize=18,
        textColor=C_WHITE,
        alignment=TA_CENTER,
        spaceAfter=2,
    )
    styles["doc_subtitle"] = ParagraphStyle(
        "doc_subtitle",
        fontName="Helvetica",
        fontSize=9,
        textColor=colors.HexColor("#D5D8DC"),
        alignment=TA_CENTER,
        spaceAfter=0,
    )
    styles["section_heading"] = ParagraphStyle(
        "section_heading",
        fontName="Helvetica-Bold",
        fontSize=10,
        textColor=C_WHITE,
        alignment=TA_LEFT,
        leftIndent=4,
        spaceBefore=0,
        spaceAfter=0,
    )
    styles["label"] = ParagraphStyle(
        "label",
        fontName="Helvetica-Bold",
        fontSize=9,
        textColor=C_DARK,
        alignment=TA_LEFT,
    )
    styles["value"] = ParagraphStyle(
        "value",
        fontName="Helvetica",
        fontSize=9,
        textColor=C_DARK,
        alignment=TA_LEFT,
    )
    styles["body"] = ParagraphStyle(
        "body",
        fontName="Helvetica",
        fontSize=9,
        textColor=C_DARK,
        alignment=TA_JUSTIFY,
        leading=14,
        spaceBefore=2,
        spaceAfter=2,
    )
    styles["caption"] = ParagraphStyle(
        "caption",
        fontName="Helvetica-Oblique",
        fontSize=8,
        textColor=C_MID,
        alignment=TA_LEFT,
    )
    styles["footer"] = ParagraphStyle(
        "footer",
        fontName="Helvetica",
        fontSize=7.5,
        textColor=C_MID,
        alignment=TA_CENTER,
    )
    styles["status_ok"] = ParagraphStyle(
        "status_ok",
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=C_STATUS_OK,
        alignment=TA_CENTER,
    )
    styles["status_warn"] = ParagraphStyle(
        "status_warn",
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=C_STATUS_WARN,
        alignment=TA_CENTER,
    )
    styles["status_crit"] = ParagraphStyle(
        "status_crit",
        fontName="Helvetica-Bold",
        fontSize=11,
        textColor=C_STATUS_CRIT,
        alignment=TA_CENTER,
    )

    return styles


# ---------------------------------------------------------------------------
# Helper: Section Header Banner
# ---------------------------------------------------------------------------
def _section_banner(text: str, styles) -> Table:
    """Returns a full-width dark navy banner used as a section heading."""
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


# ---------------------------------------------------------------------------
# Helper: Two-column KV table for patient data
# ---------------------------------------------------------------------------
def _kv_table(rows: list, styles) -> Table:
    """
    rows: list of (label, value) tuples.
    Renders a clean two-column grid with alternating row fills.
    """
    col_w = [55 * mm, 115 * mm]
    table_data = [
        [Paragraph(str(k), styles["label"]),
         Paragraph(str(v), styles["value"])]
        for k, v in rows
    ]

    style_cmds = [
        ("GRID",        (0, 0), (-1, -1), 0.4, C_LIGHT),
        ("TOPPADDING",  (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING",(0,0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",(0, 0), (-1, -1), 8),
        ("VALIGN",      (0, 0), (-1, -1), "MIDDLE"),
    ]
    # Alternating row background
    for i in range(len(table_data)):
        if i % 2 == 1:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), C_BG_STRIPE))

    tbl = Table(table_data, colWidths=col_w)
    tbl.setStyle(TableStyle(style_cmds))
    return tbl


# ---------------------------------------------------------------------------
# Helper: Metrics summary bar (4 key numbers)
# ---------------------------------------------------------------------------
def _metrics_row(metrics: list, styles) -> Table:
    """
    metrics: list of (label, value) tuples — renders as a horizontal card strip.
    """
    col_w = [170 * mm / len(metrics)] * len(metrics)
    cells = []
    for label, value in metrics:
        cell_content = [
            [Paragraph(str(value), ParagraphStyle(
                "metric_val",
                fontName="Helvetica-Bold",
                fontSize=14,
                textColor=C_ACCENT,
                alignment=TA_CENTER,
            ))],
            [Paragraph(str(label), ParagraphStyle(
                "metric_lbl",
                fontName="Helvetica",
                fontSize=7.5,
                textColor=C_MID,
                alignment=TA_CENTER,
            ))],
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


# ---------------------------------------------------------------------------
# Helper: Multi-line AI text block
# ---------------------------------------------------------------------------
def _ai_text_block(raw_text: str, styles) -> list:
    """
    Converts a multi-line AI response into a list of Paragraphs.
    Lines starting with '-' are treated as bullet items.
    """
    elements = []
    for line in sanitize_for_pdf(raw_text).splitlines():
        line = line.strip()
        if not line:
            elements.append(Spacer(1, 3))
            continue
        if line.startswith("-") or line.startswith("*"):
            # Bullet point — indent slightly
            bullet_style = ParagraphStyle(
                "bullet",
                fontName="Helvetica",
                fontSize=9,
                textColor=C_DARK,
                leftIndent=12,
                leading=14,
                spaceBefore=1,
                spaceAfter=1,
            )
            elements.append(Paragraph(line, bullet_style))
        else:
            elements.append(Paragraph(line, styles["body"]))
    return elements


# ---------------------------------------------------------------------------
# Header / Footer callbacks
# ---------------------------------------------------------------------------
def _draw_page_frame(canvas, doc):
    """Draws the document header banner and footer on every page."""
    canvas.saveState()
    page_w, page_h = A4

    # ── Top banner ──────────────────────────────────────────────────────────
    banner_h = 28 * mm
    canvas.setFillColor(C_BLACK)
    canvas.rect(0, page_h - banner_h, page_w, banner_h, fill=1, stroke=0)

    canvas.setFillColor(C_WHITE)
    canvas.setFont("Helvetica-Bold", 14)
    canvas.drawCentredString(page_w / 2, page_h - 14 * mm,
                             "Pediatric Nutritional Assessment Report")

    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(colors.HexColor("#AEB6BF"))
    canvas.drawCentredString(
        page_w / 2, page_h - 21 * mm,
        f"Neuro-Symbolic AI Framework   |   "
        f"Generated: {datetime.datetime.now().strftime('%d %b %Y, %H:%M')}"
        f"   |   CONFIDENTIAL"
    )

    # Thin accent line below banner
    canvas.setStrokeColor(C_ACCENT)
    canvas.setLineWidth(2)
    canvas.line(0, page_h - banner_h, page_w, page_h - banner_h)

    # ── Footer ──────────────────────────────────────────────────────────────
    footer_y = 12 * mm
    canvas.setStrokeColor(C_LIGHT)
    canvas.setLineWidth(0.5)
    canvas.line(15 * mm, footer_y, page_w - 15 * mm, footer_y)

    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(C_MID)
    canvas.drawString(15 * mm, footer_y - 5 * mm,
                      "FOR CLINICAL USE ONLY  |  Not a substitute for professional medical advice.")
    canvas.drawRightString(page_w - 15 * mm, footer_y - 5 * mm,
                           f"Page {doc.page}")

    canvas.restoreState()


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------
def generate_pdf_report(
    patient_data: dict,
    bmi: float,
    ml_prediction: str,
    explainer_text: str,
    unicef_text: str,
    audit_text: str,
) -> bytes:
    """
    Generates a clean, professional clinical PDF report.

    Parameters
    ----------
    patient_data   : dict  – patient demographics & socio-economic data
    bmi            : float – calculated BMI
    ml_prediction  : str   – ML model output label
    explainer_text : str   – AI clinical explainer agent output
    unicef_text    : str   – UNICEF policy intervention agent output
    audit_text     : str   – Safety audit / CMO critic agent output

    Returns
    -------
    bytes – raw PDF file content
    """
    buffer = io.BytesIO()
    styles = _build_styles()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        topMargin=38 * mm,      # leaves room for the header banner
        bottomMargin=22 * mm,
        title="Pediatric Nutritional Assessment Report",
        author="Neuro-Symbolic AI Framework",
    )

    story = []

    # ── Spacer under header (already drawn on canvas) ──────────────────────
    story.append(Spacer(1, 4 * mm))

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 1 — Patient Demographics & Context
    # ════════════════════════════════════════════════════════════════════════
    story.append(_section_banner("1.  Patient Demographics & Clinical Context", styles))
    story.append(Spacer(1, 3 * mm))

    # Build KV rows from patient_data dict + computed BMI
    kv_rows = [(k, v) for k, v in patient_data.items()]
    kv_rows.append(("Calculated BMI", f"{bmi:.2f}"))

    story.append(KeepTogether([_kv_table(kv_rows, styles)]))
    story.append(Spacer(1, 5 * mm))

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 2 — ML Diagnostic Summary (metrics card + status)
    # ════════════════════════════════════════════════════════════════════════
    story.append(_section_banner("2.  Deterministic ML Diagnostic Summary", styles))
    story.append(Spacer(1, 3 * mm))

    age_val    = patient_data.get("Age", "—")
    budget_val = patient_data.get("Daily Budget (INR)", "—")
    region_val = patient_data.get("Region", "—")

    metrics = [
        ("Patient Age", f"{age_val} yrs"),
        ("BMI Score",   f"{bmi:.1f}"),
        ("Daily Budget", f"INR {budget_val}"),
        ("Region", str(region_val)),
    ]
    story.append(_metrics_row(metrics, styles))
    story.append(Spacer(1, 4 * mm))

    # Status badge
    pred_upper = ml_prediction.upper()
    if pred_upper == "HEALTHY":
        status_style = styles["status_ok"]
        status_label = f"DIAGNOSTIC STATUS:  {pred_upper}"
    elif pred_upper == "AT RISK":
        status_style = styles["status_warn"]
        status_label = f"DIAGNOSTIC STATUS:  {pred_upper}"
    else:
        status_style = styles["status_crit"]
        status_label = f"DIAGNOSTIC STATUS:  {pred_upper}"

    status_cell = Paragraph(status_label, status_style)
    status_tbl = Table([[status_cell]], colWidths=[170 * mm])
    status_tbl.setStyle(TableStyle([
        ("BOX",           (0, 0), (-1, -1), 1, C_LIGHT),
        ("BACKGROUND",    (0, 0), (-1, -1), C_BG_STRIPE),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(KeepTogether([status_tbl]))
    story.append(Spacer(1, 5 * mm))

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 3 — AI Clinical Analysis (Explainer Agent)
    # ════════════════════════════════════════════════════════════════════════
    story.append(_section_banner("3.  AI Clinical Analysis  —  Explainer Agent", styles))
    story.append(Spacer(1, 3 * mm))
    story.append(KeepTogether(
        _ai_text_block(explainer_text, styles) or [Paragraph("No output generated.", styles["body"])]
    ))
    story.append(Spacer(1, 5 * mm))

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 4 — Socio-Economic Intervention (UNICEF Policy Agent)
    # ════════════════════════════════════════════════════════════════════════
    story.append(_section_banner("4.  Socio-Economically Constrained Intervention  —  Policy Agent", styles))
    story.append(Spacer(1, 3 * mm))
    story.append(KeepTogether(
        _ai_text_block(unicef_text, styles) or [Paragraph("No output generated.", styles["body"])]
    ))
    story.append(Spacer(1, 5 * mm))

    # ════════════════════════════════════════════════════════════════════════
    # SECTION 5 — CMO Safety Audit (Critic Agent)
    # ════════════════════════════════════════════════════════════════════════
    story.append(_section_banner("5.  CMO Guardrail Safety Audit  —  Critic Agent", styles))
    story.append(Spacer(1, 3 * mm))

    audit_elements = _ai_text_block(audit_text, styles)

    # Determine audit verdict for visual callout
    audit_upper = audit_text.upper()
    if "VERIFIED SAFE" in audit_upper:
        verdict_text = "AUDIT VERDICT:  STATUS VERIFIED SAFE"
        verdict_color = C_STATUS_OK
        verdict_bg    = colors.HexColor("#E9F7EF")
    else:
        verdict_text = "AUDIT VERDICT:  FLAGGED - REQUIRES HUMAN DOCTOR REVIEW"
        verdict_color = C_STATUS_CRIT
        verdict_bg    = colors.HexColor("#FDEDEC")

    verdict_style = ParagraphStyle(
        "verdict",
        fontName="Helvetica-Bold",
        fontSize=9.5,
        textColor=verdict_color,
        alignment=TA_CENTER,
    )
    verdict_cell = Paragraph(verdict_text, verdict_style)
    verdict_tbl = Table([[verdict_cell]], colWidths=[170 * mm])
    verdict_tbl.setStyle(TableStyle([
        ("BOX",           (0, 0), (-1, -1), 1, verdict_color),
        ("BACKGROUND",    (0, 0), (-1, -1), verdict_bg),
        ("TOPPADDING",    (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    story.append(KeepTogether(audit_elements + [Spacer(1, 4 * mm), verdict_tbl]))
    story.append(Spacer(1, 6 * mm))

    # ════════════════════════════════════════════════════════════════════════
    # DOCUMENT FOOTER NOTE
    # ════════════════════════════════════════════════════════════════════════
    story.append(HRFlowable(width="100%", thickness=0.5, color=C_LIGHT))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(
        "This report is generated by an automated AI-assisted system and is intended solely as a clinical "
        "decision-support tool. It does not constitute a medical diagnosis or replace the judgment of a "
        "licensed healthcare professional. All recommendations must be reviewed and validated by a "
        "qualified clinician before implementation.",
        styles["caption"]
    ))

    # ── Build ────────────────────────────────────────────────────────────────
    doc.build(story, onFirstPage=_draw_page_frame, onLaterPages=_draw_page_frame)
    return buffer.getvalue()
