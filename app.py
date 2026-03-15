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
# PALETTE  (Light Clinical)
#
#  Page bg       #F5F6FA   soft grey-white
#  Surface       #FFFFFF   white cards
#  Surface-2     #F0F2F8   input fills
#  Border        #DDE1EC   grey border
#  Text-primary  #1A1F36   near-black
#  Text-sec      #5A6177   slate grey
#  Text-muted    #9198AD   light grey
#  Accent        #3A6FD4   clinical blue
#  Accent-light  #EBF1FB   blue tint
#  Green         #1A9E6A / bg #EBF8F2
#  Amber         #C47B0A / bg #FEF4E2
#  Red           #C0392B / bg #FDECEA
#  Topbar        #1A2540   deep navy
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;0,9..40,700;1,9..40,300&family=DM+Mono:wght@300;400;500&family=Playfair+Display:wght@600;700&display=swap');

/* ── Reset ──────────────────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif !important;
    background-color: #F5F6FA !important;
    color: #1A1F36 !important;
}
.stApp { background-color: #F5F6FA !important; }
#MainMenu, footer, header { visibility: hidden; }
section[data-testid="stSidebar"] { display: none; }
.block-container { padding: 0 !important; max-width: 100% !important; }

/* ══════════════════════════════════════════════════════════════════════════
   CENTRED PAGE WRAP  —  all body content sits inside this
══════════════════════════════════════════════════════════════════════════ */
.page-wrap {
    max-width: 1080px;
    margin: 0 auto;
    padding: 32px 48px 60px;
}

/* ══════════════════════════════════════════════════════════════════════════
   TOP NAV BAR
══════════════════════════════════════════════════════════════════════════ */
.topbar {
    background: #1A2540;
    padding: 0 48px;
    height: 54px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.topbar-left { display: flex; align-items: center; gap: 14px; }
.topbar-logo {
    width: 30px; height: 30px;
    background: #3A6FD4;
    border-radius: 7px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
.topbar-logo svg { width: 15px; height: 15px; }
.topbar-name {
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    font-weight: 500;
    letter-spacing: 0.15em;
    color: #FFFFFF;
    text-transform: uppercase;
}
.topbar-sep { width: 1px; height: 18px; background: #2E3D60; }
.topbar-sub {
    font-size: 12px;
    font-weight: 300;
    color: #8A9CC4;
}
.topbar-badge {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    font-weight: 400;
    letter-spacing: 0.1em;
    color: #8A9CC4;
    background: #243055;
    border: 1px solid #2E3D60;
    border-radius: 4px;
    padding: 3px 10px;
    text-transform: uppercase;
}

/* ══════════════════════════════════════════════════════════════════════════
   HERO BAND
══════════════════════════════════════════════════════════════════════════ */
.hero-band {
    background: #FFFFFF;
    border-bottom: 1px solid #DDE1EC;
    padding: 40px 48px 32px;
}
.hero-inner { max-width: 1080px; margin: 0 auto; }
.hero-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    font-weight: 500;
    letter-spacing: 0.22em;
    color: #3A6FD4;
    text-transform: uppercase;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    gap: 10px;
}
.hero-eyebrow::before {
    content: '';
    display: inline-block;
    width: 18px; height: 1.5px;
    background: #3A6FD4;
}
.hero-title {
    font-family: 'Playfair Display', serif;
    font-size: 34px;
    font-weight: 700;
    color: #1A1F36;
    line-height: 1.2;
    margin-bottom: 10px;
}
.hero-title span { color: #3A6FD4; }
.hero-desc {
    font-size: 14px;
    font-weight: 400;
    color: #5A6177;
    max-width: 580px;
    line-height: 1.7;
    margin-bottom: 24px;
}
.pipeline { display: flex; align-items: center; flex-wrap: wrap; }
.pipe-step {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    font-weight: 500;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #9198AD;
    background: #F0F2F8;
    border: 1px solid #DDE1EC;
    padding: 6px 14px;
    display: flex;
    align-items: center;
    gap: 7px;
}
.pipe-step:first-child { border-radius: 5px 0 0 5px; }
.pipe-step:last-child  { border-radius: 0 5px 5px 0; }
.pipe-dot { width: 5px; height: 5px; border-radius: 50%; background: #BEC5D6; flex-shrink: 0; }
.pipe-step.on { color: #3A6FD4; background: #EBF1FB; border-color: #C0D1F0; }
.pipe-step.on .pipe-dot { background: #3A6FD4; }
.pipe-arrow {
    width: 0; height: 0;
    border-top: 11px solid transparent;
    border-bottom: 11px solid transparent;
    border-left: 8px solid #DDE1EC;
    margin: 0 -1px; flex-shrink: 0; z-index: 1;
}

/* ══════════════════════════════════════════════════════════════════════════
   SECTION HEADINGS
══════════════════════════════════════════════════════════════════════════ */
.sec-head {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 18px;
}
.sec-num {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #3A6FD4;
    background: #EBF1FB;
    border: 1px solid #C0D1F0;
    border-radius: 4px;
    padding: 3px 9px;
}
.sec-title {
    font-size: 12.5px;
    font-weight: 600;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #1A1F36;
}
.sec-rule {
    flex: 1;
    height: 1px;
    background: linear-gradient(to right, #DDE1EC, transparent);
}

/* ══════════════════════════════════════════════════════════════════════════
   FORM CARDS
══════════════════════════════════════════════════════════════════════════ */
.form-card {
    background: #FFFFFF;
    border: 1px solid #DDE1EC;
    border-radius: 9px;
    padding: 18px 18px 6px;
    margin-bottom: 2px;
}
.form-card-head {
    display: flex;
    align-items: center;
    gap: 9px;
    padding-bottom: 12px;
    margin-bottom: 2px;
    border-bottom: 1px solid #EEF0F6;
}
.fc-icon {
    width: 26px; height: 26px;
    background: #EBF1FB;
    border: 1px solid #C0D1F0;
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
.fc-label {
    font-family: 'DM Mono', monospace;
    font-size: 9.5px;
    font-weight: 500;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: #5A6177;
}

/* ── Streamlit widget overrides ─────────────────────────────────────────── */
label[data-testid="stWidgetLabel"] p {
    font-family: 'DM Mono', monospace !important;
    font-size: 9.5px !important;
    font-weight: 500 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    color: #5A6177 !important;
    margin-bottom: 3px !important;
}
div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input {
    background: #F0F2F8 !important;
    border: 1px solid #DDE1EC !important;
    color: #1A1F36 !important;
    border-radius: 6px !important;
    font-size: 13px !important;
}
div[data-testid="stNumberInput"] input:focus,
div[data-testid="stTextInput"] input:focus {
    border-color: #3A6FD4 !important;
    box-shadow: 0 0 0 3px rgba(58,111,212,0.1) !important;
    background: #FFFFFF !important;
}
div[data-testid="stSelectbox"] > div > div {
    background: #F0F2F8 !important;
    border: 1px solid #DDE1EC !important;
    color: #1A1F36 !important;
    border-radius: 6px !important;
    font-size: 13px !important;
}

/* ── Submit button ──────────────────────────────────────────────────────── */
.stButton > button {
    font-family: 'DM Mono', monospace !important;
    font-size: 10.5px !important;
    font-weight: 500 !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
    background: #1A2540 !important;
    color: #FFFFFF !important;
    border: 1px solid #1A2540 !important;
    border-radius: 7px !important;
    height: 44px !important;
    transition: background 0.2s ease !important;
}
.stButton > button:hover {
    background: #243055 !important;
    border-color: #243055 !important;
}

/* ── Download button ────────────────────────────────────────────────────── */
div[data-testid="stDownloadButton"] button {
    font-family: 'DM Mono', monospace !important;
    font-size: 10.5px !important;
    font-weight: 500 !important;
    letter-spacing: 0.14em !important;
    text-transform: uppercase !important;
    background: #FFFFFF !important;
    color: #1A2540 !important;
    border: 1.5px solid #1A2540 !important;
    border-radius: 7px !important;
    height: 44px !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stDownloadButton"] button:hover {
    background: #1A2540 !important;
    color: #FFFFFF !important;
}

/* ══════════════════════════════════════════════════════════════════════════
   METRIC CARDS
══════════════════════════════════════════════════════════════════════════ */
.metrics-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 18px;
}
.mc {
    background: #FFFFFF;
    border: 1px solid #DDE1EC;
    border-top: 3px solid #3A6FD4;
    border-radius: 8px;
    padding: 16px 16px 12px;
}
.mc.green { border-top-color: #1A9E6A; }
.mc.amber { border-top-color: #C47B0A; }
.mc.red   { border-top-color: #C0392B; }
.mc-lbl {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    font-weight: 500;
    letter-spacing: 0.13em;
    text-transform: uppercase;
    color: #9198AD;
    margin-bottom: 7px;
}
.mc-val {
    font-family: 'Playfair Display', serif;
    font-size: 24px;
    font-weight: 700;
    color: #1A1F36;
    line-height: 1;
    margin-bottom: 3px;
}
.mc-unit {
    font-family: 'DM Mono', monospace;
    font-size: 9.5px;
    font-weight: 300;
    color: #9198AD;
}
.mc.green .mc-val { color: #1A9E6A; }
.mc.amber .mc-val { color: #C47B0A; }
.mc.red   .mc-val { color: #C0392B; }

/* ══════════════════════════════════════════════════════════════════════════
   STATUS STRIP
══════════════════════════════════════════════════════════════════════════ */
.s-strip {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    border-radius: 8px;
    padding: 13px 16px;
    margin-bottom: 24px;
    border: 1px solid;
}
.s-strip.green { background: #EBF8F2; border-color: #9EDAC3; }
.s-strip.amber { background: #FEF4E2; border-color: #EEC97A; }
.s-strip.red   { background: #FDECEA; border-color: #EFA9A9; }
.s-pill {
    font-family: 'DM Mono', monospace;
    font-size: 8.5px;
    font-weight: 500;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    padding: 4px 11px;
    border-radius: 20px;
    white-space: nowrap;
    margin-top: 2px;
    border: 1px solid;
    flex-shrink: 0;
}
.s-pill.green { color: #1A9E6A; background: #D0F1E3; border-color: #9EDAC3; }
.s-pill.amber { color: #9A5E00; background: #FCE8B4; border-color: #EEC97A; }
.s-pill.red   { color: #B03020; background: #FAD1CE; border-color: #EFA9A9; }
.s-msg { font-size: 13px; font-weight: 400; line-height: 1.65; }
.s-msg.green { color: #144F38; }
.s-msg.amber { color: #6B3C00; }
.s-msg.red   { color: #761818; }

/* ══════════════════════════════════════════════════════════════════════════
   AGENT PANELS
══════════════════════════════════════════════════════════════════════════ */
.ap {
    background: #FFFFFF;
    border: 1px solid #DDE1EC;
    border-radius: 9px;
    overflow: hidden;
    margin-bottom: 12px;
}
.ap-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 12px 18px;
    background: #F8F9FC;
    border-bottom: 1px solid #EEF0F6;
}
.ap-left { display: flex; align-items: center; gap: 10px; }
.ap-phase {
    font-family: 'DM Mono', monospace;
    font-size: 8.5px;
    font-weight: 500;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    color: #3A6FD4;
    background: #EBF1FB;
    border: 1px solid #C0D1F0;
    border-radius: 3px;
    padding: 3px 8px;
}
.ap-title { font-size: 13px; font-weight: 600; color: #1A1F36; }
.ap-status {
    font-family: 'DM Mono', monospace;
    font-size: 8.5px;
    font-weight: 400;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #9198AD;
    display: flex;
    align-items: center;
    gap: 5px;
}
.ap-status-dot { width: 6px; height: 6px; border-radius: 50%; background: #1A9E6A; }
.ap-body {
    padding: 18px 20px;
    font-size: 13.5px;
    font-weight: 400;
    line-height: 1.8;
    color: #2E3550;
}

/* Audit variants */
.ap.ap-safe    { border-color: #9EDAC3; }
.ap.ap-safe    .ap-head { background: #EBF8F2; border-color: #9EDAC3; }
.ap.ap-flagged { border-color: #EFA9A9; }
.ap.ap-flagged .ap-head { background: #FDECEA; border-color: #EFA9A9; }
.ap-body.safe    { color: #144F38; }
.ap-body.flagged { color: #761818; }

.verdict {
    font-family: 'DM Mono', monospace;
    font-size: 8.5px;
    font-weight: 500;
    letter-spacing: 0.15em;
    text-transform: uppercase;
    padding: 4px 11px;
    border-radius: 4px;
    border: 1px solid;
}
.verdict.safe    { color: #1A9E6A; background: #D0F1E3; border-color: #9EDAC3; }
.verdict.flagged { color: #B03020; background: #FAD1CE; border-color: #EFA9A9; }

/* ══════════════════════════════════════════════════════════════════════════
   ARCHITECTURE CARDS
══════════════════════════════════════════════════════════════════════════ */
.arch-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    margin-top: 18px;
}
.arch-card {
    background: #FFFFFF;
    border: 1px solid #DDE1EC;
    border-radius: 9px;
    padding: 22px 20px;
}
.arch-num {
    font-family: 'Playfair Display', serif;
    font-size: 42px;
    font-weight: 700;
    color: #EEF0F6;
    line-height: 1;
    margin-bottom: 10px;
}
.arch-ttl { font-size: 13px; font-weight: 600; color: #1A1F36; margin-bottom: 7px; }
.arch-dsc { font-size: 12.5px; font-weight: 400; color: #5A6177; line-height: 1.65; }
.arch-tag {
    display: inline-block;
    margin-top: 13px;
    font-family: 'DM Mono', monospace;
    font-size: 8.5px;
    font-weight: 500;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #3A6FD4;
    background: #EBF1FB;
    border: 1px solid #C0D1F0;
    border-radius: 4px;
    padding: 3px 9px;
}

/* ══════════════════════════════════════════════════════════════════════════
   UTILITIES
══════════════════════════════════════════════════════════════════════════ */
.divider { height: 1px; background: #DDE1EC; margin: 26px 0; }
.gap-sm  { height: 10px; }
.gap-md  { height: 22px; }

.err-box {
    background: #FDECEA;
    border: 1px solid #EFA9A9;
    border-radius: 8px;
    padding: 14px 18px;
    font-size: 13px;
    color: #761818;
}

div[data-testid="stSpinner"] p {
    font-family: 'DM Mono', monospace !important;
    font-size: 10px !important;
    letter-spacing: 0.1em !important;
    color: #5A6177 !important;
    text-transform: uppercase !important;
}
div.stMarkdown p { font-size: 14px; line-height: 1.7; color: #2E3550; }

.exp-title { font-size: 13.5px; font-weight: 600; color: #1A1F36; margin-bottom: 4px; }
.exp-desc  {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    font-weight: 400;
    letter-spacing: 0.04em;
    color: #9198AD;
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
    <div class="err-box" style="margin:40px 48px;">
        <strong>System Initialisation Error</strong><br>
        Ensure <code>model_logic.py</code> and <code>label_encoders.json</code>
        are present in the working directory.
    </div>
    """, unsafe_allow_html=True)
    st.stop()

from agent_graph import clinical_agent_app


# ─────────────────────────────────────────────────────────────────────────────
# TOP NAV BAR  (full-bleed, outside centred wrap)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
    <div class="topbar-left">
        <div class="topbar-logo">
            <svg viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="7" y="1" width="2" height="14" rx="1" fill="white"/>
                <rect x="1" y="7" width="14" height="2" rx="1" fill="white"/>
                <rect x="4.5" y="2" width="1.5" height="4" rx="0.75" fill="white" opacity="0.45"/>
                <rect x="10" y="10" width="1.5" height="4" rx="0.75" fill="white" opacity="0.45"/>
            </svg>
        </div>
        <span class="topbar-name">PNAS</span>
        <div class="topbar-sep"></div>
        <span class="topbar-sub">Pediatric Nutritional Assessment System</span>
    </div>
    <span class="topbar-badge">Clinical Decision Support &nbsp;v2.0</span>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HERO BAND  (full-bleed white, inner content capped to 1080px)
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-band">
  <div class="hero-inner">
    <div class="hero-eyebrow">Neuro-Symbolic AI Framework</div>
    <div class="hero-title">Pediatric <span>Nutritional</span> Assessment Platform</div>
    <div class="hero-desc">
        Integrating deterministic machine learning with self-auditing multi-agent AI to deliver
        geo-culturally specific, budget-constrained clinical interventions for pediatric nutritional risk.
    </div>
    <div class="pipeline">
        <div class="pipe-step on"><div class="pipe-dot"></div>Patient Intake</div>
        <div class="pipe-arrow"></div>
        <div class="pipe-step on"><div class="pipe-dot"></div>ML Diagnosis</div>
        <div class="pipe-arrow"></div>
        <div class="pipe-step on"><div class="pipe-dot"></div>Explainer Agent</div>
        <div class="pipe-arrow"></div>
        <div class="pipe-step on"><div class="pipe-dot"></div>Policy Agent</div>
        <div class="pipe-arrow"></div>
        <div class="pipe-step on"><div class="pipe-dot"></div>Safety Audit</div>
        <div class="pipe-arrow"></div>
        <div class="pipe-step on"><div class="pipe-dot"></div>Report Export</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# CENTRED PAGE WRAP OPENS HERE
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="page-wrap">', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 01 — PATIENT INTAKE FORM
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="gap-md"></div>
<div class="sec-head">
    <span class="sec-num">01</span>
    <span class="sec-title">Patient Intake Form</span>
    <div class="sec-rule"></div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    st.markdown("""
    <div class="form-card">
        <div class="form-card-head">
            <div class="fc-icon">
                <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                    <circle cx="6.5" cy="3.5" r="2.5" stroke="#3A6FD4" stroke-width="1.2"/>
                    <path d="M1 12c0-3.038 2.462-5.5 5.5-5.5S12 8.962 12 12"
                          stroke="#3A6FD4" stroke-width="1.2" stroke-linecap="round"/>
                </svg>
            </div>
            <span class="fc-label">Physical Metrics</span>
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
        <div class="form-card-head">
            <div class="fc-icon">
                <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                    <path d="M6.5 1v11M1 6.5h11" stroke="#3A6FD4" stroke-width="1.2" stroke-linecap="round"/>
                    <circle cx="6.5" cy="6.5" r="5.5" stroke="#3A6FD4" stroke-width="1.2"/>
                </svg>
            </div>
            <span class="fc-label">Dietary &amp; Environmental</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    meals_input  = st.selectbox("Consistent Regular Meals?", ["Yes", "No"])
    fruits_input = st.selectbox("Daily Vegetable / Fruit Intake?", ["Yes", "No"])
    water_input  = st.selectbox("Access to Clean Drinking Water?", ["Yes", "No"])

with col3:
    st.markdown("""
    <div class="form-card">
        <div class="form-card-head">
            <div class="fc-icon">
                <svg width="13" height="13" viewBox="0 0 13 13" fill="none">
                    <path d="M6.5 1L1.5 3.8v2.7c0 2.8 2.3 5.1 5 5.5 2.7-.4 5-2.7 5-5.5V3.8L6.5 1z"
                          stroke="#3A6FD4" stroke-width="1.2" stroke-linejoin="round"/>
                </svg>
            </div>
            <span class="fc-label">Socio-Economic Context</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    region  = st.text_input("Region / State", value="West Bengal")
    setting = st.selectbox("Living Setting", ["Rural", "Urban", "Peri-Urban"])
    budget  = st.number_input("Daily Food Budget (INR)", min_value=10, max_value=2000, value=60)

st.markdown('<div class="gap-sm"></div>', unsafe_allow_html=True)
analyze_btn = st.button("Initialize Clinical Assessment", use_container_width=True)
st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


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
        ml_scores       = score(input_features)
        predicted_index = int(np.argmax(ml_scores))
        status_map      = {v: k for k, v in encoders['Nutrition_Status'].items()}
        ml_prediction   = status_map[predicted_index]
        height_m        = height / 100
        bmi             = weight / (height_m ** 2)

    except Exception as e:
        st.markdown(f'<div class="err-box"><strong>Processing Error:</strong> {e}</div>',
                    unsafe_allow_html=True)
        st.stop()

    # colour classes
    clr = {"Healthy": "green", "At Risk": "amber", "Malnourished": "red"}.get(ml_prediction, "amber")

    # ── SECTION 02 — Diagnostic Summary ─────────────────────────────────────
    st.markdown("""
    <div class="sec-head">
        <span class="sec-num">02</span>
        <span class="sec-title">Diagnostic Summary</span>
        <div class="sec-rule"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="metrics-row">
        <div class="mc">
            <div class="mc-lbl">Patient Age</div>
            <div class="mc-val">{age}</div>
            <div class="mc-unit">years</div>
        </div>
        <div class="mc">
            <div class="mc-lbl">Calculated BMI</div>
            <div class="mc-val">{bmi:.1f}</div>
            <div class="mc-unit">kg / m²</div>
        </div>
        <div class="mc">
            <div class="mc-lbl">Daily Budget</div>
            <div class="mc-val">{budget}</div>
            <div class="mc-unit">INR / day</div>
        </div>
        <div class="mc {clr}">
            <div class="mc-lbl">Diagnostic Status</div>
            <div class="mc-val">{ml_prediction}</div>
            <div class="mc-unit">ML Prediction</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if ml_prediction == "Healthy":
        msg = ("Primary ML evaluation indicates the patient is within "
               "<strong>healthy nutritional parameters</strong>. "
               "No immediate intervention required; lifestyle maintenance is advised.")
    elif ml_prediction == "At Risk":
        msg = ("Primary ML evaluation has flagged <strong>elevated nutritional risk</strong>. "
               "Targeted dietary and socio-economic interventions are recommended without delay.")
    else:
        msg = ("Primary ML evaluation has detected <strong>acute malnourishment</strong>. "
               "Immediate multi-modal clinical and dietary intervention is strongly advised.")

    st.markdown(f"""
    <div class="s-strip {clr}">
        <span class="s-pill {clr}">{ml_prediction}</span>
        <span class="s-msg {clr}">{msg}</span>
    </div>
    """, unsafe_allow_html=True)

    # ── Multi-Agent Execution ────────────────────────────────────────────────
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
        st.markdown(
            '<div class="err-box"><strong>System Failure:</strong> '
            'The agentic framework did not complete the 3-tier audit process.</div>',
            unsafe_allow_html=True)
        st.stop()

    explainer_msg = messages[-3].content
    unicef_msg    = messages[-2].content
    audit_msg     = messages[-1].content

    # ── SECTION 03 — Agent Outputs ───────────────────────────────────────────
    st.markdown("""
    <div class="divider"></div>
    <div class="sec-head">
        <span class="sec-num">03</span>
        <span class="sec-title">Multi-Agent Clinical Evaluation</span>
        <div class="sec-rule"></div>
    </div>
    """, unsafe_allow_html=True)

    # Phase 1
    st.markdown(f"""
    <div class="ap">
        <div class="ap-head">
            <div class="ap-left">
                <span class="ap-phase">Phase 01</span>
                <span class="ap-title">Clinical Analysis — Explainer Agent</span>
            </div>
            <div class="ap-status"><div class="ap-status-dot"></div>Complete</div>
        </div>
        <div class="ap-body">{explainer_msg}</div>
    </div>
    """, unsafe_allow_html=True)

    # Phase 2
    st.markdown(f"""
    <div class="ap">
        <div class="ap-head">
            <div class="ap-left">
                <span class="ap-phase">Phase 02</span>
                <span class="ap-title">Socio-Economic Intervention — Policy Agent</span>
            </div>
            <div class="ap-status"><div class="ap-status-dot"></div>Complete</div>
        </div>
        <div class="ap-body">{unicef_msg}</div>
    </div>
    """, unsafe_allow_html=True)

    # Phase 3 — Safety Audit
    is_safe    = "VERIFIED SAFE" in audit_msg.upper()
    ap_cls     = "ap-safe"    if is_safe else "ap-flagged"
    body_cls   = "safe"       if is_safe else "flagged"
    verd_cls   = "safe"       if is_safe else "flagged"
    verd_lbl   = "Verified Safe" if is_safe else "Flagged — Human Review Required"

    st.markdown(f"""
    <div class="ap {ap_cls}">
        <div class="ap-head">
            <div class="ap-left">
                <span class="ap-phase">Phase 03</span>
                <span class="ap-title">Medical Guardrail — CMO Safety Audit</span>
            </div>
            <span class="verdict {verd_cls}">{verd_lbl}</span>
        </div>
        <div class="ap-body {body_cls}">{audit_msg}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── SECTION 04 — Report Export ────────────────────────────────────────────
    st.markdown("""
    <div class="divider"></div>
    <div class="sec-head">
        <span class="sec-num">04</span>
        <span class="sec-title">Report Export</span>
        <div class="sec-rule"></div>
    </div>
    """, unsafe_allow_html=True)

    pdf_bytes = generate_pdf_report(
        patient_dict, bmi, ml_prediction,
        explainer_msg, unicef_msg, audit_msg
    )

    dl_col1, dl_col2 = st.columns([3, 1], gap="medium")
    with dl_col1:
        st.markdown("""
        <div style="padding:12px 0 6px;">
            <div class="exp-title">Clinical Assessment Report (PDF)</div>
            <div class="exp-desc">Patient demographics · ML diagnosis · Agent analyses · Audit verdict</div>
        </div>
        """, unsafe_allow_html=True)
    with dl_col2:
        st.markdown('<div style="padding-top:8px;"></div>', unsafe_allow_html=True)
        st.download_button(
            label="Download PDF",
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
    <div class="sec-head">
        <span class="sec-num">02</span>
        <span class="sec-title">System Architecture</span>
        <div class="sec-rule"></div>
    </div>
    <p style="font-size:13px; color:#5A6177; margin-bottom:0;">
        System ready. Complete the Patient Intake Form above and initialise the assessment to begin.
    </p>
    <div class="arch-grid">
        <div class="arch-card">
            <div class="arch-num">01</div>
            <div class="arch-ttl">Deterministic ML Sensor</div>
            <div class="arch-dsc">
                A mathematically rigorous Decision Tree model computes the immediate nutritional
                risk classification from anthropometric and dietary inputs, with zero runtime dependencies.
            </div>
            <span class="arch-tag">Decision Tree · m2cgen</span>
        </div>
        <div class="arch-card">
            <div class="arch-num">02</div>
            <div class="arch-ttl">Multi-Agent AI Analysis</div>
            <div class="arch-dsc">
                A LangGraph-orchestrated network of specialised AI agents synthesises hyper-local,
                budget-constrained interventions guided by UNICEF pediatric nutrition standards.
            </div>
            <span class="arch-tag">LangGraph · Gemini 2.5</span>
        </div>
        <div class="arch-card">
            <div class="arch-num">03</div>
            <div class="arch-ttl">CMO Safety Guardrail</div>
            <div class="arch-dsc">
                A dedicated critic agent acting as Chief Medical Officer performs a strict clinical
                safety audit on all generated interventions prior to output and report generation.
            </div>
            <span class="arch-tag">Critic Agent · Safety Audit</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Close page-wrap
st.markdown('</div>', unsafe_allow_html=True)
