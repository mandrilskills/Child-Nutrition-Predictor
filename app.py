import streamlit as st
import json
import numpy as np
from dotenv import load_dotenv

from utils import generate_pdf_report

load_dotenv()

# ─────────────────────────────────────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="PNAS — Pediatric Nutritional Assessment",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# GLOBAL CSS  —  Dark Clinical Precision theme
# Palette:
#   Background:   #090E1A  (near-black navy)
#   Surface:      #0F1629  (card surface)
#   Surface-2:    #151E35  (elevated surface)
#   Border:       #1E2D4F  (subtle border)
#   Primary text: #E8EDF5  (near-white)
#   Secondary:    #7A8BB0  (muted)
#   Accent:       #4A7FDB  (clinical blue)
#   Gold:         #C9A84C  (status / highlight)
#   Green:        #2ECC8B
#   Amber:        #E8A020
#   Red:          #E05252
# Font stack: 'DM Sans' (body) + 'DM Mono' (data/labels)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,300&family=DM+Mono:wght@300;400;500&family=Playfair+Display:wght@600;700&display=swap');

/* ── Reset & Base ──────────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #090E1A !important;
    color: #E8EDF5 !important;
}

.stApp {
    background-color: #090E1A !important;
}

/* ── Hide Streamlit chrome ─────────────────────────────────────────────── */
#MainMenu, footer, header { visibility: hidden; }
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}
section[data-testid="stSidebar"] { display: none; }

/* ── Global link & focus ───────────────────────────────────────────────── */
a { color: #4A7FDB; }
*:focus { outline: 1px solid #4A7FDB !important; }

/* ══════════════════════════════════════════════════════════════════════════
   TOP NAVIGATION BAR
══════════════════════════════════════════════════════════════════════════ */
.topbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 40px;
    height: 58px;
    background: #0B1220;
    border-bottom: 1px solid #1E2D4F;
    position: sticky;
    top: 0;
    z-index: 999;
}
.topbar-brand {
    display: flex;
    align-items: center;
    gap: 12px;
}
.topbar-logo {
    width: 32px; height: 32px;
    background: linear-gradient(135deg, #1E3A6E 0%, #4A7FDB 100%);
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
}
.topbar-logo svg { width: 18px; height: 18px; }
.topbar-name {
    font-family: 'DM Mono', monospace;
    font-size: 13px;
    font-weight: 500;
    letter-spacing: 0.12em;
    color: #E8EDF5;
    text-transform: uppercase;
}
.topbar-divider {
    width: 1px; height: 22px;
    background: #1E2D4F;
    margin: 0 4px;
}
.topbar-sub {
    font-family: 'DM Sans', sans-serif;
    font-size: 12px;
    font-weight: 300;
    color: #4A7FDB;
    letter-spacing: 0.04em;
}
.topbar-badge {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.1em;
    color: #7A8BB0;
    background: #0F1629;
    border: 1px solid #1E2D4F;
    border-radius: 4px;
    padding: 3px 10px;
    text-transform: uppercase;
}

/* ══════════════════════════════════════════════════════════════════════════
   HERO HEADER
══════════════════════════════════════════════════════════════════════════ */
.hero {
    padding: 52px 40px 40px;
    border-bottom: 1px solid #1E2D4F;
    background:
        radial-gradient(ellipse 80% 60% at 10% 0%, rgba(74,127,219,0.07) 0%, transparent 60%),
        radial-gradient(ellipse 50% 40% at 90% 100%, rgba(201,168,76,0.04) 0%, transparent 60%),
        #090E1A;
}
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 10.5px;
    font-weight: 500;
    letter-spacing: 0.2em;
    color: #4A7FDB;
    text-transform: uppercase;
    margin-bottom: 14px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.hero-eyebrow::before {
    content: '';
    display: inline-block;
    width: 24px; height: 1px;
    background: #4A7FDB;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 42px;
    font-weight: 700;
    line-height: 1.15;
    color: #E8EDF5;
    margin-bottom: 14px;
    letter-spacing: -0.01em;
}
.hero-title span { color: #4A7FDB; }
.hero-subtitle {
    font-size: 15px;
    font-weight: 300;
    color: #7A8BB0;
    max-width: 620px;
    line-height: 1.7;
    margin-bottom: 28px;
}
.hero-pipeline {
    display: flex;
    align-items: center;
    gap: 0;
    flex-wrap: wrap;
}
.pipeline-step {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 7px 16px 7px 12px;
    background: #0F1629;
    border: 1px solid #1E2D4F;
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    font-weight: 400;
    letter-spacing: 0.08em;
    color: #7A8BB0;
    text-transform: uppercase;
    position: relative;
}
.pipeline-step:first-child { border-radius: 5px 0 0 5px; }
.pipeline-step:last-child  { border-radius: 0 5px 5px 0; }
.pipeline-step .dot {
    width: 6px; height: 6px;
    border-radius: 50%;
    background: #1E2D4F;
    flex-shrink: 0;
}
.pipeline-step.active { color: #4A7FDB; border-color: #2A4A8A; background: #111B35; }
.pipeline-step.active .dot { background: #4A7FDB; box-shadow: 0 0 6px rgba(74,127,219,0.6); }
.pipeline-arrow {
    width: 0; height: 0;
    border-top: 14px solid transparent;
    border-bottom: 14px solid transparent;
    border-left: 10px solid #1E2D4F;
    z-index: 2;
    margin: 0 -1px;
    flex-shrink: 0;
}

/* ══════════════════════════════════════════════════════════════════════════
   MAIN CONTENT AREA
══════════════════════════════════════════════════════════════════════════ */
.main-content {
    padding: 36px 40px;
    max-width: 1400px;
    margin: 0 auto;
}

/* ══════════════════════════════════════════════════════════════════════════
   SECTION HEADERS
══════════════════════════════════════════════════════════════════════════ */
.section-label {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 18px;
}
.section-number {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    font-weight: 500;
    color: #4A7FDB;
    background: rgba(74,127,219,0.1);
    border: 1px solid rgba(74,127,219,0.25);
    border-radius: 4px;
    padding: 3px 8px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.section-title {
    font-size: 14px;
    font-weight: 600;
    letter-spacing: 0.06em;
    color: #E8EDF5;
    text-transform: uppercase;
}
.section-rule {
    flex: 1;
    height: 1px;
    background: linear-gradient(to right, #1E2D4F, transparent);
}

/* ══════════════════════════════════════════════════════════════════════════
   FORM CARDS
══════════════════════════════════════════════════════════════════════════ */
.form-card {
    background: #0F1629;
    border: 1px solid #1E2D4F;
    border-radius: 10px;
    padding: 24px;
    height: 100%;
    transition: border-color 0.2s ease;
}
.form-card:hover { border-color: #2A4A8A; }
.form-card-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 20px;
    padding-bottom: 14px;
    border-bottom: 1px solid #1E2D4F;
}
.form-card-icon {
    width: 28px; height: 28px;
    background: rgba(74,127,219,0.12);
    border: 1px solid rgba(74,127,219,0.2);
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
.form-card-title {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.14em;
    color: #7A8BB0;
    text-transform: uppercase;
}

/* ── Streamlit Input Overrides ─────────────────────────────────────────── */
div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input,
div[data-testid="stSelectbox"] > div > div,
div[data-testid="stSlider"] {
    background: #151E35 !important;
    border-color: #1E2D4F !important;
    color: #E8EDF5 !important;
    border-radius: 6px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-size: 13px !important;
}
div[data-testid="stSelectbox"] > div > div:hover,
div[data-testid="stNumberInput"] input:focus,
div[data-testid="stTextInput"] input:focus {
    border-color: #4A7FDB !important;
    box-shadow: 0 0 0 2px rgba(74,127,219,0.15) !important;
}
label[data-testid="stWidgetLabel"] p {
    font-family: 'DM Mono', monospace !important;
    font-size: 10.5px !important;
    font-weight: 400 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: #7A8BB0 !important;
    margin-bottom: 4px !important;
}
div[data-testid="stSlider"] > div { padding: 0 2px; }
div[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
    background: #4A7FDB !important;
    border: 2px solid #6B9FEB !important;
}
div[class*="stSlider"] div[data-baseweb="slider"] div[class*="thumb"] {
    background: #4A7FDB !important;
}

/* ── Submit Button ─────────────────────────────────────────────────────── */
.stButton > button {
    font-family: 'DM Mono', monospace !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
    background: linear-gradient(135deg, #1E3A6E 0%, #2A5199 50%, #1E3A6E 100%) !important;
    background-size: 200% 100% !important;
    color: #E8EDF5 !important;
    border: 1px solid #3060B0 !important;
    border-radius: 6px !important;
    padding: 12px 28px !important;
    height: 46px !important;
    transition: all 0.3s ease !important;
    box-shadow: 0 2px 12px rgba(74,127,219,0.15), inset 0 1px 0 rgba(255,255,255,0.05) !important;
}
.stButton > button:hover {
    background-position: right center !important;
    border-color: #4A7FDB !important;
    box-shadow: 0 4px 20px rgba(74,127,219,0.3), inset 0 1px 0 rgba(255,255,255,0.08) !important;
    transform: translateY(-1px) !important;
}
.stButton > button:active { transform: translateY(0) !important; }

/* ── Download Button ───────────────────────────────────────────────────── */
div[data-testid="stDownloadButton"] button {
    font-family: 'DM Mono', monospace !important;
    font-size: 11px !important;
    font-weight: 500 !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    background: transparent !important;
    color: #C9A84C !important;
    border: 1px solid #C9A84C !important;
    border-radius: 6px !important;
    height: 46px !important;
    transition: all 0.25s ease !important;
}
div[data-testid="stDownloadButton"] button:hover {
    background: rgba(201,168,76,0.08) !important;
    box-shadow: 0 0 16px rgba(201,168,76,0.2) !important;
}

/* ══════════════════════════════════════════════════════════════════════════
   METRIC CARDS
══════════════════════════════════════════════════════════════════════════ */
.metric-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-bottom: 24px;
}
.metric-card {
    background: #0F1629;
    border: 1px solid #1E2D4F;
    border-radius: 10px;
    padding: 20px 20px 16px;
    position: relative;
    overflow: hidden;
}
.metric-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(to right, #4A7FDB, transparent);
}
.metric-label {
    font-family: 'DM Mono', monospace;
    font-size: 9.5px;
    font-weight: 500;
    letter-spacing: 0.14em;
    color: #7A8BB0;
    text-transform: uppercase;
    margin-bottom: 8px;
}
.metric-value {
    font-family: 'Playfair Display', serif;
    font-size: 28px;
    font-weight: 700;
    color: #E8EDF5;
    line-height: 1;
    margin-bottom: 4px;
}
.metric-unit {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    font-weight: 300;
    color: #4A6A9A;
}

/* Status variants */
.metric-card.healthy::before { background: linear-gradient(to right, #2ECC8B, transparent); }
.metric-card.healthy .metric-value { color: #2ECC8B; }
.metric-card.atrisk::before  { background: linear-gradient(to right, #E8A020, transparent); }
.metric-card.atrisk .metric-value  { color: #E8A020; }
.metric-card.malnourished::before { background: linear-gradient(to right, #E05252, transparent); }
.metric-card.malnourished .metric-value { color: #E05252; }

/* ══════════════════════════════════════════════════════════════════════════
   STATUS BANNER
══════════════════════════════════════════════════════════════════════════ */
.status-banner {
    border-radius: 8px;
    padding: 14px 22px;
    margin-bottom: 28px;
    display: flex;
    align-items: center;
    gap: 14px;
    border-width: 1px;
    border-style: solid;
}
.status-banner.healthy {
    background: rgba(46,204,139,0.06);
    border-color: rgba(46,204,139,0.25);
}
.status-banner.atrisk {
    background: rgba(232,160,32,0.06);
    border-color: rgba(232,160,32,0.25);
}
.status-banner.malnourished {
    background: rgba(224,82,82,0.06);
    border-color: rgba(224,82,82,0.25);
}
.status-pill {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    font-weight: 500;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    padding: 4px 12px;
    border-radius: 20px;
    flex-shrink: 0;
    border-width: 1px;
    border-style: solid;
}
.status-pill.healthy { color: #2ECC8B; background: rgba(46,204,139,0.1); border-color: rgba(46,204,139,0.3); }
.status-pill.atrisk  { color: #E8A020; background: rgba(232,160,32,0.1); border-color: rgba(232,160,32,0.3); }
.status-pill.malnourished { color: #E05252; background: rgba(224,82,82,0.1); border-color: rgba(224,82,82,0.3); }
.status-text {
    font-size: 13px;
    font-weight: 400;
    line-height: 1.5;
}
.status-text.healthy    { color: #A3E4C8; }
.status-text.atrisk     { color: #F0CD88; }
.status-text.malnourished { color: #F0AAAA; }

/* ══════════════════════════════════════════════════════════════════════════
   AGENT RESULT PANELS
══════════════════════════════════════════════════════════════════════════ */
.agent-panel {
    background: #0F1629;
    border: 1px solid #1E2D4F;
    border-radius: 10px;
    margin-bottom: 16px;
    overflow: hidden;
}
.agent-panel-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 14px 20px;
    background: #111B35;
    border-bottom: 1px solid #1E2D4F;
}
.agent-panel-title {
    display: flex;
    align-items: center;
    gap: 10px;
}
.agent-phase-tag {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    font-weight: 500;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #4A7FDB;
    background: rgba(74,127,219,0.1);
    border: 1px solid rgba(74,127,219,0.2);
    border-radius: 3px;
    padding: 3px 8px;
}
.agent-name {
    font-family: 'DM Sans', sans-serif;
    font-size: 13px;
    font-weight: 600;
    color: #C8D4E8;
}
.agent-status-dot {
    width: 8px; height: 8px;
    border-radius: 50%;
    background: #2ECC8B;
    box-shadow: 0 0 8px rgba(46,204,139,0.5);
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.4; }
}
.agent-panel-body {
    padding: 20px;
    font-size: 13.5px;
    font-weight: 300;
    line-height: 1.8;
    color: #B0BECC;
}

/* Audit panel verified / flagged */
.agent-panel.verified { border-color: rgba(46,204,139,0.3); }
.agent-panel.verified .agent-panel-header { background: rgba(46,204,139,0.05); border-color: rgba(46,204,139,0.2); }
.agent-panel.flagged  { border-color: rgba(224,82,82,0.3); }
.agent-panel.flagged  .agent-panel-header { background: rgba(224,82,82,0.05); border-color: rgba(224,82,82,0.2); }

.verdict-badge {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    font-weight: 500;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    padding: 4px 12px;
    border-radius: 4px;
    border: 1px solid;
}
.verdict-badge.safe    { color: #2ECC8B; background: rgba(46,204,139,0.1); border-color: rgba(46,204,139,0.3); }
.verdict-badge.flagged { color: #E05252; background: rgba(224,82,82,0.1);  border-color: rgba(224,82,82,0.3); }

/* ══════════════════════════════════════════════════════════════════════════
   ARCHITECTURE CARDS (empty state)
══════════════════════════════════════════════════════════════════════════ */
.arch-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-top: 24px;
}
.arch-card {
    background: #0F1629;
    border: 1px solid #1E2D4F;
    border-radius: 10px;
    padding: 24px;
    position: relative;
    overflow: hidden;
}
.arch-card::after {
    content: '';
    position: absolute;
    bottom: 0; right: 0;
    width: 80px; height: 80px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(74,127,219,0.06) 0%, transparent 70%);
}
.arch-step-num {
    font-family: 'Playfair Display', serif;
    font-size: 48px;
    font-weight: 700;
    color: #1A2A4A;
    line-height: 1;
    margin-bottom: 12px;
}
.arch-step-title {
    font-family: 'DM Sans', sans-serif;
    font-size: 13px;
    font-weight: 600;
    color: #C8D4E8;
    margin-bottom: 8px;
}
.arch-step-desc {
    font-size: 12px;
    font-weight: 300;
    color: #5A6B88;
    line-height: 1.65;
}
.arch-tag {
    display: inline-block;
    margin-top: 14px;
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #4A7FDB;
    background: rgba(74,127,219,0.08);
    border: 1px solid rgba(74,127,219,0.2);
    border-radius: 4px;
    padding: 3px 10px;
}

/* ══════════════════════════════════════════════════════════════════════════
   SPINNER OVERRIDE
══════════════════════════════════════════════════════════════════════════ */
div[data-testid="stSpinner"] > div {
    border-color: #1E2D4F !important;
    border-top-color: #4A7FDB !important;
}
div[data-testid="stSpinner"] p {
    font-family: 'DM Mono', monospace !important;
    font-size: 11px !important;
    letter-spacing: 0.1em !important;
    color: #7A8BB0 !important;
    text-transform: uppercase !important;
}

/* ══════════════════════════════════════════════════════════════════════════
   DIVIDERS & SPACERS
══════════════════════════════════════════════════════════════════════════ */
.h-rule {
    border: none;
    border-top: 1px solid #1E2D4F;
    margin: 28px 0;
}
.spacer-sm { height: 16px; }
.spacer-md { height: 28px; }
.spacer-lg { height: 44px; }

/* ══════════════════════════════════════════════════════════════════════════
   MISC STREAMLIT OVERRIDES
══════════════════════════════════════════════════════════════════════════ */
div[data-testid="stAlert"] {
    background: #0F1629 !important;
    border-color: #1E2D4F !important;
    border-radius: 8px !important;
}
div.stMarkdown p {
    font-size: 14px;
    line-height: 1.7;
    color: #B0BECC;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# LOAD MODEL ASSETS
# ─────────────────────────────────────────────────────────────────────────────
try:
    from model_logic import score
    with open('label_encoders.json', 'r') as f:
        encoders = json.load(f)
except Exception:
    st.markdown("""
    <div style="margin:60px 40px; padding:24px; background:#0F1629; border:1px solid rgba(224,82,82,0.3);
                border-radius:10px; color:#F0AAAA; font-family:'DM Sans',sans-serif; font-size:13px;">
        <strong>System Initialisation Error</strong><br>
        Ensure <code>model_logic.py</code> and <code>label_encoders.json</code> are present in the working directory.
    </div>
    """, unsafe_allow_html=True)
    st.stop()

from agent_graph import clinical_agent_app


# ─────────────────────────────────────────────────────────────────────────────
# TOP NAV BAR
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
    <div class="topbar-brand">
        <div class="topbar-logo">
            <svg viewBox="0 0 18 18" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="8" y="1" width="2" height="16" rx="1" fill="#6BAAF0"/>
                <rect x="1" y="8" width="16" height="2" rx="1" fill="#6BAAF0"/>
                <rect x="5" y="3" width="2" height="4" rx="1" fill="#4A7FDB" opacity="0.6"/>
                <rect x="11" y="11" width="2" height="4" rx="1" fill="#4A7FDB" opacity="0.6"/>
            </svg>
        </div>
        <span class="topbar-name">PNAS</span>
        <div class="topbar-divider"></div>
        <span class="topbar-sub">Pediatric Nutritional Assessment System</span>
    </div>
    <span class="topbar-badge">Clinical Decision Support v2.0</span>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HERO SECTION
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-eyebrow">Neuro-Symbolic AI Framework</div>
    <div class="hero-title">
        Pediatric <span>Nutritional</span><br>Assessment Platform
    </div>
    <div class="hero-subtitle">
        Integrating deterministic machine learning with self-auditing multi-agent AI to deliver
        geo-culturally specific, budget-constrained clinical interventions for pediatric nutritional risk.
    </div>
    <div class="hero-pipeline">
        <div class="pipeline-step active">
            <div class="dot"></div>Patient Intake
        </div>
        <div class="pipeline-arrow"></div>
        <div class="pipeline-step active">
            <div class="dot"></div>ML Diagnosis
        </div>
        <div class="pipeline-arrow"></div>
        <div class="pipeline-step active">
            <div class="dot"></div>Explainer Agent
        </div>
        <div class="pipeline-arrow"></div>
        <div class="pipeline-step active">
            <div class="dot"></div>Policy Agent
        </div>
        <div class="pipeline-arrow"></div>
        <div class="pipeline-step active">
            <div class="dot"></div>Safety Audit
        </div>
        <div class="pipeline-arrow"></div>
        <div class="pipeline-step active">
            <div class="dot"></div>Report Export
        </div>
    </div>
</div>
<div class="main-content">
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 01 — PATIENT INTAKE FORM
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="section-label">
    <span class="section-number">01</span>
    <span class="section-title">Patient Intake Form</span>
    <div class="section-rule"></div>
</div>
""", unsafe_allow_html=True)

# Three form columns, each wrapped in a card
col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    st.markdown("""
    <div class="form-card">
        <div class="form-card-header">
            <div class="form-card-icon">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <circle cx="7" cy="4" r="3" stroke="#4A7FDB" stroke-width="1.2"/>
                    <path d="M1 13c0-3.314 2.686-6 6-6s6 2.686 6 6" stroke="#4A7FDB" stroke-width="1.2" stroke-linecap="round"/>
                </svg>
            </div>
            <span class="form-card-title">Physical Metrics</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    age          = st.number_input("Age (years)", min_value=0, max_value=15, value=5)
    gender_input = st.selectbox("Gender", ["Male", "Female"])
    weight       = st.slider("Weight (kg)", min_value=2.0, max_value=50.0, value=16.65, step=0.05)
    height       = st.slider("Height (cm)", min_value=40.0, max_value=150.0, value=95.0, step=0.5)

with col2:
    st.markdown("""
    <div class="form-card">
        <div class="form-card-header">
            <div class="form-card-icon">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path d="M2 7h10M7 2v10" stroke="#4A7FDB" stroke-width="1.2" stroke-linecap="round"/>
                    <circle cx="7" cy="7" r="5.5" stroke="#4A7FDB" stroke-width="1.2"/>
                </svg>
            </div>
            <span class="form-card-title">Dietary &amp; Environmental</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    meals_input  = st.selectbox("Consistent Regular Meals?", ["Yes", "No"])
    fruits_input = st.selectbox("Daily Vegetable / Fruit Intake?", ["Yes", "No"])
    water_input  = st.selectbox("Access to Clean Drinking Water?", ["Yes", "No"])

with col3:
    st.markdown("""
    <div class="form-card">
        <div class="form-card-header">
            <div class="form-card-icon">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path d="M7 1L2 4v3c0 3 2.5 5.5 5 6 2.5-.5 5-3 5-6V4L7 1z" stroke="#4A7FDB" stroke-width="1.2" stroke-linejoin="round"/>
                </svg>
            </div>
            <span class="form-card-title">Socio-Economic Context</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    region  = st.text_input("Region / State", value="West Bengal")
    setting = st.selectbox("Living Setting", ["Rural", "Urban", "Peri-Urban"])
    budget  = st.number_input("Daily Food Budget (INR)", min_value=10, max_value=2000, value=60)

st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)
analyze_btn = st.button("Initialize Clinical Assessment", use_container_width=True)
st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)
st.markdown('<hr class="h-rule">', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# RESULTS  /  EMPTY STATE
# ─────────────────────────────────────────────────────────────────────────────
if analyze_btn:

    # ── ML Inference ────────────────────────────────────────────────────────
    try:
        input_features = [
            float(age),
            float(encoders['Gender'][gender_input]),
            float(weight),
            float(height),
            float(encoders['Has_Regular_Meals'][meals_input]),
            float(encoders['Eats_Fruits_Veggies'][fruits_input]),
            float(encoders['Clean_Drinking_Water'][water_input]),
        ]
        ml_scores      = score(input_features)
        predicted_index = int(np.argmax(ml_scores))
        status_map     = {v: k for k, v in encoders['Nutrition_Status'].items()}
        ml_prediction  = status_map[predicted_index]

        height_m = height / 100
        bmi      = weight / (height_m ** 2)

    except Exception as e:
        st.markdown(f"""
        <div style="padding:20px; background:#0F1629; border:1px solid rgba(224,82,82,0.3);
                    border-radius:8px; color:#F0AAAA; font-size:13px; font-family:'DM Sans',sans-serif;">
            <strong>Processing Error:</strong> {e}
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    # ── Helper: CSS class from prediction ───────────────────────────────────
    pred_class = {
        "Healthy":      "healthy",
        "At Risk":      "atrisk",
        "Malnourished": "malnourished",
    }.get(ml_prediction, "atrisk")

    # ── SECTION 02 — Diagnostic Summary ─────────────────────────────────────
    st.markdown("""
    <div class="section-label">
        <span class="section-number">02</span>
        <span class="section-title">Diagnostic Summary</span>
        <div class="section-rule"></div>
    </div>
    """, unsafe_allow_html=True)

    # Metric cards
    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-card">
            <div class="metric-label">Patient Age</div>
            <div class="metric-value">{age}</div>
            <div class="metric-unit">years</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Calculated BMI</div>
            <div class="metric-value">{bmi:.1f}</div>
            <div class="metric-unit">kg / m²</div>
        </div>
        <div class="metric-card">
            <div class="metric-label">Daily Budget</div>
            <div class="metric-value">{budget}</div>
            <div class="metric-unit">INR / day</div>
        </div>
        <div class="metric-card {pred_class}">
            <div class="metric-label">Diagnostic Status</div>
            <div class="metric-value">{ml_prediction}</div>
            <div class="metric-unit">ML Prediction</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Status banner
    if ml_prediction == "Healthy":
        banner_msg = (
            "Primary machine learning evaluation indicates the patient is within <strong>healthy nutritional parameters</strong>. "
            "No immediate intervention is required; lifestyle maintenance is recommended."
        )
    elif ml_prediction == "At Risk":
        banner_msg = (
            "Primary machine learning evaluation has flagged <strong>elevated nutritional risk</strong>. "
            "Targeted dietary and socio-economic interventions are recommended without delay."
        )
    else:
        banner_msg = (
            "Primary machine learning evaluation has detected <strong>acute malnourishment</strong>. "
            "Immediate multi-modal clinical and dietary intervention is strongly advised."
        )

    st.markdown(f"""
    <div class="status-banner {pred_class}">
        <span class="status-pill {pred_class}">{ml_prediction}</span>
        <span class="status-text {pred_class}">{banner_msg}</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Multi-Agent AI Execution ─────────────────────────────────────────────
    patient_dict = {
        "Age": age, "Gender": gender_input,
        "Weight (kg)": weight, "Height (cm)": height,
        "Regular Meals": meals_input, "Eats Veggies": fruits_input,
        "Clean Water": water_input, "Region": region,
        "Setting": setting, "Daily Budget (INR)": budget,
    }

    initial_state = {
        "patient_data":  patient_dict,
        "ml_prediction": ml_prediction,
        "messages":      [],
    }

    with st.spinner("Executing multi-agent clinical evaluation pipeline..."):
        final_state = clinical_agent_app.invoke(initial_state)
        messages    = final_state.get("messages", [])

    if len(messages) < 3:
        st.markdown("""
        <div style="padding:20px; background:#0F1629; border:1px solid rgba(224,82,82,0.3);
                    border-radius:8px; color:#F0AAAA; font-size:13px; font-family:'DM Sans',sans-serif;">
            <strong>System Failure:</strong> The agentic framework did not complete the required 3-tier audit process.
        </div>
        """, unsafe_allow_html=True)
        st.stop()

    explainer_msg = messages[-3].content
    unicef_msg    = messages[-2].content
    audit_msg     = messages[-1].content

    # ── SECTION 03 — Agent Outputs ───────────────────────────────────────────
    st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-label">
        <span class="section-number">03</span>
        <span class="section-title">Multi-Agent Clinical Evaluation</span>
        <div class="section-rule"></div>
    </div>
    """, unsafe_allow_html=True)

    # Phase 1 — Explainer
    st.markdown("""
    <div class="agent-panel">
        <div class="agent-panel-header">
            <div class="agent-panel-title">
                <span class="agent-phase-tag">Phase 01</span>
                <span class="agent-name">Clinical Analysis — Explainer Agent</span>
            </div>
            <div class="agent-status-dot"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f'<div style="background:#0F1629; border:1px solid #1E2D4F; border-top:none; border-radius:0 0 10px 10px; padding:20px; font-size:13.5px; font-weight:300; line-height:1.8; color:#B0BECC;">{explainer_msg}</div>', unsafe_allow_html=True)

    st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)

    # Phase 2 — Policy Agent
    st.markdown("""
    <div class="agent-panel">
        <div class="agent-panel-header">
            <div class="agent-panel-title">
                <span class="agent-phase-tag">Phase 02</span>
                <span class="agent-name">Socio-Economic Intervention — Policy Agent</span>
            </div>
            <div class="agent-status-dot"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f'<div style="background:#0F1629; border:1px solid #1E2D4F; border-top:none; border-radius:0 0 10px 10px; padding:20px; font-size:13.5px; font-weight:300; line-height:1.8; color:#B0BECC;">{unicef_msg}</div>', unsafe_allow_html=True)

    st.markdown('<div class="spacer-sm"></div>', unsafe_allow_html=True)

    # Phase 3 — Safety Audit
    is_safe        = "VERIFIED SAFE" in audit_msg.upper()
    audit_cls      = "verified" if is_safe else "flagged"
    verdict_text   = "Verified Safe" if is_safe else "Flagged — Human Review Required"
    verdict_cls    = "safe" if is_safe else "flagged"

    st.markdown(f"""
    <div class="agent-panel {audit_cls}">
        <div class="agent-panel-header">
            <div class="agent-panel-title">
                <span class="agent-phase-tag">Phase 03</span>
                <span class="agent-name">Medical Guardrail — CMO Safety Audit</span>
            </div>
            <span class="verdict-badge {verdict_cls}">{verdict_text}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown(f'<div style="background:#0F1629; border:1px solid {"rgba(46,204,139,0.3)" if is_safe else "rgba(224,82,82,0.3)"}; border-top:none; border-radius:0 0 10px 10px; padding:20px; font-size:13.5px; font-weight:300; line-height:1.8; color:{"#A3E4C8" if is_safe else "#F0AAAA"};">{audit_msg}</div>', unsafe_allow_html=True)

    # ── SECTION 04 — Report Export ────────────────────────────────────────────
    st.markdown('<div class="spacer-md"></div>', unsafe_allow_html=True)
    st.markdown('<hr class="h-rule">', unsafe_allow_html=True)
    st.markdown("""
    <div class="section-label">
        <span class="section-number">04</span>
        <span class="section-title">Report Export</span>
        <div class="section-rule"></div>
    </div>
    <div style="font-size:12px; font-weight:300; color:#5A6B88; font-family:'DM Mono',monospace;
                letter-spacing:0.04em; margin-bottom:14px;">
        Compiled clinical report — includes full patient demographics, ML diagnosis, agent analyses, and audit verdict.
    </div>
    """, unsafe_allow_html=True)

    pdf_bytes = generate_pdf_report(
        patient_dict, bmi, ml_prediction,
        explainer_msg, unicef_msg, audit_msg
    )
    st.download_button(
        label="Download Clinical Assessment Report  (PDF)",
        data=pdf_bytes,
        file_name=f"PNAS_Report_{ml_prediction.lower().replace(' ', '_')}.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

# ─────────────────────────────────────────────────────────────────────────────
# EMPTY STATE — Architecture Overview
# ─────────────────────────────────────────────────────────────────────────────
else:
    st.markdown("""
    <div class="section-label">
        <span class="section-number">02</span>
        <span class="section-title">System Architecture</span>
        <div class="section-rule"></div>
    </div>
    <div style="font-size:13px; font-weight:300; color:#5A6B88; margin-bottom:4px; font-family:'DM Sans',sans-serif;">
        System ready. Complete the Patient Intake Form above and initialise the assessment to begin.
    </div>
    <div class="arch-grid">
        <div class="arch-card">
            <div class="arch-step-num">01</div>
            <div class="arch-step-title">Deterministic ML Sensor</div>
            <div class="arch-step-desc">
                A mathematically rigorous Decision Tree model computes the immediate nutritional
                risk classification from anthropometric and dietary inputs, with zero runtime dependencies.
            </div>
            <span class="arch-tag">Decision Tree · m2cgen</span>
        </div>
        <div class="arch-card">
            <div class="arch-step-num">02</div>
            <div class="arch-step-title">Multi-Agent AI Analysis</div>
            <div class="arch-step-desc">
                A LangGraph-orchestrated network of specialised AI agents synthesises hyper-local,
                budget-constrained interventions guided by UNICEF pediatric nutrition standards.
            </div>
            <span class="arch-tag">LangGraph · Gemini 2.5</span>
        </div>
        <div class="arch-card">
            <div class="arch-step-num">03</div>
            <div class="arch-step-title">CMO Safety Guardrail</div>
            <div class="arch-step-desc">
                A dedicated critic agent acting as Chief Medical Officer performs a strict clinical
                safety audit on all generated interventions prior to output and report generation.
            </div>
            <span class="arch-tag">Critic Agent · Safety Audit</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Close the main-content div
st.markdown("</div>", unsafe_allow_html=True)
