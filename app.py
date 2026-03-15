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
    page_title="Pediatric Nutritional Assessment System",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────────────────────────────────────
# PALETTE
#   Page bg      #FAF8F2   warm cream
#   Surface      #FFFFFF   white cards
#   Input bg     #F5F2E8   warm off-white for inputs
#   Border       #D8CEBF   warm beige border
#   Topbar bg    #3B0A24   deep maroon
#   Accent       #6B1A38   plum-maroon
#   Accent-light #F5E8EE   pale rose tint (for tags/pills bg)
#   Accent-mid   #C4748C   softer rose (borders, highlights)
#   Text-primary #1C1008   near-black warm
#   Text-sec     #5C4A3A   warm brown-grey
#   Text-muted   #9C8878   muted warm grey
#   Green        #2E7D52 / bg #E8F4EE
#   Amber        #8B5E00 / bg #FDF4DC
#   Red          #9B2020 / bg #FAEAEA
# ─────────────────────────────────────────────────────────────────────────────

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Source+Serif+4:ital,wght@0,400;0,600;0,700;1,400&family=Inter:wght@400;500;600&display=swap');

/* ─── Base reset ──────────────────────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
    background-color: #FAF8F2 !important;
    color: #1C1008 !important;
}
.stApp { background-color: #FAF8F2 !important; }
#MainMenu, footer, header { visibility: hidden; }
section[data-testid="stSidebar"] { display: none; }

/* Strip Streamlit's default padding entirely so our wrapper controls all spacing */
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ─── Centred content column ─────────────────────────────────────────────── */
/* This is the main constraint. Everything body-level renders inside .wrap.   */
/* max-width + auto margins = centred. Padding = comfortable side breathing.  */
.wrap {
    max-width: 960px;
    margin: 0 auto;
    padding: 36px 56px 72px 56px;
}

/* ─── TOP NAV ─────────────────────────────────────────────────────────────── */
.topbar {
    background: #3B0A24;
    padding: 0 56px;
    height: 52px;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.topbar-brand {
    display: flex;
    align-items: center;
    gap: 12px;
}
.topbar-logo {
    width: 28px; height: 28px;
    background: #6B1A38;
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
.topbar-logo svg { width: 14px; height: 14px; }
.topbar-name {
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 600;
    letter-spacing: 0.06em;
    color: #FFFFFF;
}
.topbar-divider { width: 1px; height: 16px; background: #5C2238; }
.topbar-full {
    font-size: 12px;
    font-weight: 400;
    color: #C49AAE;
}
.topbar-version {
    font-size: 11px;
    font-weight: 400;
    color: #8A5268;
    background: #4A1230;
    border: 1px solid #5C2238;
    border-radius: 4px;
    padding: 2px 10px;
}

/* ─── HERO ────────────────────────────────────────────────────────────────── */
.hero {
    background: #FFFFFF;
    border-bottom: 2px solid #D8CEBF;
    padding: 40px 56px 32px;
}
.hero-inner {
    max-width: 960px;
    margin: 0 auto;
}
.hero-tag {
    display: inline-block;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 0.06em;
    color: #6B1A38;
    background: #F5E8EE;
    border: 1px solid #C4748C;
    border-radius: 20px;
    padding: 3px 14px;
    margin-bottom: 14px;
    text-transform: uppercase;
}
.hero-title {
    font-family: 'Source Serif 4', serif;
    font-size: 32px;
    font-weight: 700;
    color: #1C1008;
    line-height: 1.25;
    margin-bottom: 10px;
}
.hero-title em {
    font-style: italic;
    color: #6B1A38;
}
.hero-subtitle {
    font-size: 15px;
    font-weight: 400;
    color: #5C4A3A;
    max-width: 600px;
    line-height: 1.7;
    margin-bottom: 24px;
}
.pipeline {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0;
}
.pipe-step {
    font-size: 11px;
    font-weight: 500;
    color: #9C8878;
    background: #F5F2E8;
    border: 1px solid #D8CEBF;
    padding: 6px 16px;
    display: flex;
    align-items: center;
    gap: 7px;
}
.pipe-step:first-child { border-radius: 5px 0 0 5px; }
.pipe-step:last-child  { border-radius: 0 5px 5px 0; }
.pipe-dot { width: 6px; height: 6px; border-radius: 50%; background: #C4B8A8; flex-shrink: 0; }
.pipe-step.on { color: #6B1A38; background: #F5E8EE; border-color: #C4748C; }
.pipe-step.on .pipe-dot { background: #6B1A38; }
.pipe-arrow {
    width: 0; height: 0;
    border-top: 13px solid transparent;
    border-bottom: 13px solid transparent;
    border-left: 9px solid #D8CEBF;
    margin: 0 -1px; flex-shrink: 0; z-index: 1;
}

/* ─── SECTION HEADERS ────────────────────────────────────────────────────── */
.sec {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 20px;
}
.sec-num {
    font-size: 11px;
    font-weight: 600;
    color: #6B1A38;
    background: #F5E8EE;
    border: 1px solid #C4748C;
    border-radius: 4px;
    padding: 3px 10px;
    flex-shrink: 0;
}
.sec-title {
    font-family: 'Source Serif 4', serif;
    font-size: 18px;
    font-weight: 600;
    color: #1C1008;
}
.sec-line {
    flex: 1;
    height: 1px;
    background: #D8CEBF;
}

/* ─── FORM SECTION CARDS ─────────────────────────────────────────────────── */
.form-card {
    background: #FFFFFF;
    border: 1px solid #D8CEBF;
    border-top: 3px solid #6B1A38;
    border-radius: 8px;
    padding: 20px 20px 8px 20px;
    margin-bottom: 4px;
}
.form-card-head {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 16px;
    padding-bottom: 12px;
    border-bottom: 1px solid #EDE8DE;
}
.fc-icon {
    width: 28px; height: 28px;
    background: #F5E8EE;
    border: 1px solid #C4748C;
    border-radius: 6px;
    display: flex; align-items: center; justify-content: center;
    flex-shrink: 0;
}
.fc-label {
    font-size: 13px;
    font-weight: 600;
    color: #3B0A24;
    letter-spacing: 0.01em;
}

/* ─── WIDGET OVERRIDES ───────────────────────────────────────────────────── */
/* Labels — plain, readable, not screaming uppercase monospace */
label[data-testid="stWidgetLabel"] p {
    font-family: 'Inter', sans-serif !important;
    font-size: 13px !important;
    font-weight: 500 !important;
    letter-spacing: 0 !important;
    text-transform: none !important;
    color: #3B2A1A !important;
    margin-bottom: 4px !important;
}

/* Inputs */
div[data-testid="stNumberInput"] input,
div[data-testid="stTextInput"] input {
    background: #F5F2E8 !important;
    border: 1px solid #C8BFB0 !important;
    color: #1C1008 !important;
    border-radius: 6px !important;
    font-size: 14px !important;
    font-family: 'Inter', sans-serif !important;
}
div[data-testid="stNumberInput"] input:focus,
div[data-testid="stTextInput"] input:focus {
    border-color: #6B1A38 !important;
    box-shadow: 0 0 0 3px rgba(107,26,56,0.1) !important;
    background: #FFFFFF !important;
}

/* Selectboxes */
div[data-testid="stSelectbox"] > div > div {
    background: #F5F2E8 !important;
    border: 1px solid #C8BFB0 !important;
    color: #1C1008 !important;
    border-radius: 6px !important;
    font-size: 14px !important;
    font-family: 'Inter', sans-serif !important;
}
div[data-testid="stSelectbox"] > div > div:hover {
    border-color: #6B1A38 !important;
}

/* Sliders */
div[data-testid="stSlider"] [data-baseweb="slider"] div[role="slider"] {
    background: #6B1A38 !important;
    border-color: #6B1A38 !important;
}
div[data-testid="stSlider"] [data-baseweb="slider"] [data-testid="stTickBarMin"],
div[data-testid="stSlider"] [data-baseweb="slider"] [data-testid="stTickBarMax"] {
    color: #9C8878 !important;
    font-size: 12px !important;
}

/* ─── BUTTONS ────────────────────────────────────────────────────────────── */
.stButton > button {
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    letter-spacing: 0.02em !important;
    background: #3B0A24 !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 7px !important;
    height: 48px !important;
    transition: background 0.2s ease !important;
}
.stButton > button:hover {
    background: #6B1A38 !important;
}

div[data-testid="stDownloadButton"] button {
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    font-weight: 600 !important;
    background: #FFFFFF !important;
    color: #3B0A24 !important;
    border: 2px solid #3B0A24 !important;
    border-radius: 7px !important;
    height: 48px !important;
    transition: all 0.2s ease !important;
}
div[data-testid="stDownloadButton"] button:hover {
    background: #3B0A24 !important;
    color: #FFFFFF !important;
}

/* ─── METRIC CARDS ───────────────────────────────────────────────────────── */
.metrics {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-bottom: 20px;
}
.mc {
    background: #FFFFFF;
    border: 1px solid #D8CEBF;
    border-top: 3px solid #6B1A38;
    border-radius: 8px;
    padding: 18px 16px 14px;
}
.mc.green { border-top-color: #2E7D52; }
.mc.amber { border-top-color: #8B5E00; }
.mc.red   { border-top-color: #9B2020; }
.mc-lbl {
    font-size: 11px;
    font-weight: 500;
    color: #9C8878;
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
.mc-val {
    font-family: 'Source Serif 4', serif;
    font-size: 26px;
    font-weight: 700;
    color: #1C1008;
    line-height: 1;
    margin-bottom: 4px;
}
.mc-unit { font-size: 11px; color: #9C8878; }
.mc.green .mc-val { color: #2E7D52; }
.mc.amber .mc-val { color: #8B5E00; }
.mc.red   .mc-val { color: #9B2020; }

/* ─── STATUS STRIP ───────────────────────────────────────────────────────── */
.s-strip {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 28px;
    border: 1px solid;
}
.s-strip.green { background: #E8F4EE; border-color: #9ECAB3; }
.s-strip.amber { background: #FDF4DC; border-color: #E0C070; }
.s-strip.red   { background: #FAEAEA; border-color: #E0A0A0; }
.s-pill {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    padding: 4px 14px;
    border-radius: 20px;
    white-space: nowrap;
    margin-top: 2px;
    border: 1px solid;
    flex-shrink: 0;
}
.s-pill.green { color: #2E7D52; background: #C8EDD9; border-color: #9ECAB3; }
.s-pill.amber { color: #7A4E00; background: #FCEAA0; border-color: #E0C070; }
.s-pill.red   { color: #8B1A1A; background: #F5CECE; border-color: #E0A0A0; }
.s-msg { font-size: 14px; font-weight: 400; line-height: 1.6; }
.s-msg.green { color: #1A4F32; }
.s-msg.amber { color: #5A3500; }
.s-msg.red   { color: #6B1010; }

/* ─── AGENT PANELS ───────────────────────────────────────────────────────── */
.ap {
    background: #FFFFFF;
    border: 1px solid #D8CEBF;
    border-radius: 8px;
    overflow: hidden;
    margin-bottom: 14px;
}
.ap-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 13px 20px;
    background: #FAF8F2;
    border-bottom: 1px solid #EDE8DE;
}
.ap-left { display: flex; align-items: center; gap: 10px; }
.ap-phase {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    color: #6B1A38;
    background: #F5E8EE;
    border: 1px solid #C4748C;
    border-radius: 4px;
    padding: 3px 10px;
}
.ap-title {
    font-size: 14px;
    font-weight: 600;
    color: #1C1008;
}
.ap-done {
    font-size: 11px;
    font-weight: 500;
    color: #2E7D52;
    display: flex;
    align-items: center;
    gap: 5px;
}
.done-dot { width: 7px; height: 7px; border-radius: 50%; background: #2E7D52; }
.ap-body {
    padding: 20px 22px;
    font-size: 14px;
    font-weight: 400;
    line-height: 1.8;
    color: #2A1E14;
}

/* Audit panel variants */
.ap.safe-panel   { border-color: #9ECAB3; }
.ap.safe-panel   .ap-head { background: #E8F4EE; border-color: #9ECAB3; }
.ap.flag-panel   { border-color: #E0A0A0; }
.ap.flag-panel   .ap-head { background: #FAEAEA; border-color: #E0A0A0; }
.ap-body.safe    { color: #1A4F32; }
.ap-body.flagged { color: #6B1010; }

.verdict {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.04em;
    text-transform: uppercase;
    padding: 4px 13px;
    border-radius: 4px;
    border: 1px solid;
}
.verdict.safe    { color: #2E7D52; background: #C8EDD9; border-color: #9ECAB3; }
.verdict.flagged { color: #8B1A1A; background: #F5CECE; border-color: #E0A0A0; }

/* ─── ARCHITECTURE CARDS (empty state) ──────────────────────────────────── */
.arch-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin-top: 20px;
}
.arch-card {
    background: #FFFFFF;
    border: 1px solid #D8CEBF;
    border-radius: 8px;
    padding: 24px 20px;
}
.arch-num {
    font-family: 'Source Serif 4', serif;
    font-size: 40px;
    font-weight: 700;
    color: #EDE8DE;
    line-height: 1;
    margin-bottom: 10px;
}
.arch-ttl { font-size: 14px; font-weight: 600; color: #1C1008; margin-bottom: 8px; }
.arch-dsc { font-size: 13px; font-weight: 400; color: #5C4A3A; line-height: 1.65; }
.arch-tag {
    display: inline-block;
    margin-top: 14px;
    font-size: 11px;
    font-weight: 500;
    color: #6B1A38;
    background: #F5E8EE;
    border: 1px solid #C4748C;
    border-radius: 4px;
    padding: 3px 10px;
}

/* ─── UTILITIES ──────────────────────────────────────────────────────────── */
.divider { height: 1px; background: #D8CEBF; margin: 28px 0; }
.gap-sm  { height: 12px; }
.gap-md  { height: 24px; }

.err-box {
    background: #FAEAEA;
    border: 1px solid #E0A0A0;
    border-radius: 8px;
    padding: 14px 18px;
    font-size: 14px;
    color: #6B1010;
}

div[data-testid="stSpinner"] p {
    font-size: 14px !important;
    color: #5C4A3A !important;
}

div.stMarkdown p {
    font-size: 14px;
    line-height: 1.7;
    color: #2A1E14;
}

.exp-title { font-size: 15px; font-weight: 600; color: #1C1008; margin-bottom: 4px; }
.exp-desc  { font-size: 13px; font-weight: 400; color: #9C8878; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# LOAD MODEL
# ─────────────────────────────────────────────────────────────────────────────
try:
    from model_logic import score
    with open('label_encoders.json', 'r') as f:
        encoders = json.load(f)
except Exception:
    st.markdown("""
    <div class="err-box" style="margin: 40px 56px;">
        <strong>System Error:</strong> Ensure <code>model_logic.py</code>
        and <code>label_encoders.json</code> are present in the working directory.
    </div>
    """, unsafe_allow_html=True)
    st.stop()

from agent_graph import clinical_agent_app


# ─────────────────────────────────────────────────────────────────────────────
# TOP NAV BAR  — full-bleed dark maroon band
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="topbar">
    <div class="topbar-brand">
        <div class="topbar-logo">
            <svg viewBox="0 0 14 14" fill="none" xmlns="http://www.w3.org/2000/svg">
                <rect x="6" y="1" width="2" height="12" rx="1" fill="white"/>
                <rect x="1" y="6" width="12" height="2" rx="1" fill="white"/>
                <rect x="3.5" y="2" width="1.5" height="3.5" rx="0.75" fill="white" opacity="0.45"/>
                <rect x="9" y="8.5" width="1.5" height="3.5" rx="0.75" fill="white" opacity="0.45"/>
            </svg>
        </div>
        <span class="topbar-name">PNAS</span>
        <div class="topbar-divider"></div>
        <span class="topbar-full">Pediatric Nutritional Assessment System</span>
    </div>
    <span class="topbar-version">Clinical Support · v2.0</span>
</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# HERO — full-bleed white band, content capped at 960px
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
  <div class="hero-inner">
    <span class="hero-tag">Neuro-Symbolic AI Framework</span>
    <div class="hero-title">Pediatric <em>Nutritional</em> Assessment Platform</div>
    <div class="hero-subtitle">
        An integrated clinical tool combining deterministic machine learning with
        self-auditing multi-agent AI — designed to support field workers and NGO staff
        in assessing pediatric nutritional risk with geo-specific, budget-aware recommendations.
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
# MAIN CONTENT WRAPPER — centred, with side padding
# ─────────────────────────────────────────────────────────────────────────────
st.markdown('<div class="wrap">', unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SECTION 01 — PATIENT INTAKE FORM
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="gap-md"></div>
<div class="sec">
    <span class="sec-num">01</span>
    <span class="sec-title">Patient Intake Form</span>
    <div class="sec-line"></div>
</div>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    st.markdown("""
    <div class="form-card">
        <div class="form-card-head">
            <div class="fc-icon">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <circle cx="7" cy="4" r="2.8" stroke="#6B1A38" stroke-width="1.3"/>
                    <path d="M1.5 13c0-3.038 2.462-5.5 5.5-5.5s5.5 2.462 5.5 5.5"
                          stroke="#6B1A38" stroke-width="1.3" stroke-linecap="round"/>
                </svg>
            </div>
            <span class="fc-label">Physical Metrics</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    age          = st.number_input("Age (in years)", min_value=0, max_value=15, value=5)
    gender_input = st.selectbox("Gender", ["Male", "Female"])
    weight       = st.slider("Weight (kg)", min_value=2.0, max_value=50.0, value=16.65, step=0.05)
    height       = st.slider("Height (cm)", min_value=40.0, max_value=150.0, value=95.0, step=0.5)

with col2:
    st.markdown("""
    <div class="form-card">
        <div class="form-card-head">
            <div class="fc-icon">
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path d="M7 1v12M1 7h12" stroke="#6B1A38" stroke-width="1.3" stroke-linecap="round"/>
                    <circle cx="7" cy="7" r="5.8" stroke="#6B1A38" stroke-width="1.3"/>
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
                <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
                    <path d="M7 1L2 3.8v3c0 3 2.3 5.3 5 5.7 2.7-.4 5-2.7 5-5.7v-3L7 1z"
                          stroke="#6B1A38" stroke-width="1.3" stroke-linejoin="round"/>
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
# RESULTS / EMPTY STATE
# ─────────────────────────────────────────────────────────────────────────────
if analyze_btn:

    # ML inference
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

    clr = {"Healthy": "green", "At Risk": "amber", "Malnourished": "red"}.get(ml_prediction, "amber")

    # ── SECTION 02 — Diagnostic Summary ──────────────────────────────────────
    st.markdown("""
    <div class="sec">
        <span class="sec-num">02</span>
        <span class="sec-title">Diagnostic Summary</span>
        <div class="sec-line"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="metrics">
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
        msg = ("ML evaluation indicates the patient is within "
               "<strong>healthy nutritional parameters</strong>. "
               "No immediate intervention required; continue with lifestyle maintenance.")
    elif ml_prediction == "At Risk":
        msg = ("ML evaluation has flagged <strong>elevated nutritional risk</strong>. "
               "Targeted dietary and socio-economic interventions are recommended without delay.")
    else:
        msg = ("ML evaluation has detected <strong>acute malnourishment</strong>. "
               "Immediate multi-modal clinical and dietary intervention is strongly advised.")

    st.markdown(f"""
    <div class="s-strip {clr}">
        <span class="s-pill {clr}">{ml_prediction}</span>
        <span class="s-msg {clr}">{msg}</span>
    </div>
    """, unsafe_allow_html=True)

    # Multi-agent pipeline
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

    with st.spinner("Running clinical AI agents — this may take a moment..."):
        final_state = clinical_agent_app.invoke(initial_state)
        messages    = final_state.get("messages", [])

    if len(messages) < 3:
        st.markdown(
            '<div class="err-box"><strong>System Failure:</strong> '
            'The AI pipeline did not complete all three stages.</div>',
            unsafe_allow_html=True)
        st.stop()

    explainer_msg = messages[-3].content
    unicef_msg    = messages[-2].content
    audit_msg     = messages[-1].content

    # ── SECTION 03 — Agent Outputs ────────────────────────────────────────────
    st.markdown("""
    <div class="divider"></div>
    <div class="sec">
        <span class="sec-num">03</span>
        <span class="sec-title">Clinical AI Evaluation</span>
        <div class="sec-line"></div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="ap">
        <div class="ap-head">
            <div class="ap-left">
                <span class="ap-phase">Phase 01</span>
                <span class="ap-title">Clinical Analysis — Explainer Agent</span>
            </div>
            <div class="ap-done"><div class="done-dot"></div>Complete</div>
        </div>
        <div class="ap-body">{explainer_msg}</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="ap">
        <div class="ap-head">
            <div class="ap-left">
                <span class="ap-phase">Phase 02</span>
                <span class="ap-title">Socio-Economic Intervention — Policy Agent</span>
            </div>
            <div class="ap-done"><div class="done-dot"></div>Complete</div>
        </div>
        <div class="ap-body">{unicef_msg}</div>
    </div>
    """, unsafe_allow_html=True)

    is_safe  = "VERIFIED SAFE" in audit_msg.upper()
    ap_cls   = "safe-panel" if is_safe else "flag-panel"
    body_cls = "safe"       if is_safe else "flagged"
    vrd_cls  = "safe"       if is_safe else "flagged"
    vrd_lbl  = "Verified Safe" if is_safe else "Flagged — Requires Doctor Review"

    st.markdown(f"""
    <div class="ap {ap_cls}">
        <div class="ap-head">
            <div class="ap-left">
                <span class="ap-phase">Phase 03</span>
                <span class="ap-title">Medical Guardrail — CMO Safety Audit</span>
            </div>
            <span class="verdict {vrd_cls}">{vrd_lbl}</span>
        </div>
        <div class="ap-body {body_cls}">{audit_msg}</div>
    </div>
    """, unsafe_allow_html=True)

    # ── SECTION 04 — Report Export ────────────────────────────────────────────
    st.markdown("""
    <div class="divider"></div>
    <div class="sec">
        <span class="sec-num">04</span>
        <span class="sec-title">Download Report</span>
        <div class="sec-line"></div>
    </div>
    """, unsafe_allow_html=True)

    pdf_bytes = generate_pdf_report(
        patient_dict, bmi, ml_prediction,
        explainer_msg, unicef_msg, audit_msg
    )

    dl1, dl2 = st.columns([3, 1], gap="medium")
    with dl1:
        st.markdown("""
        <div style="padding: 10px 0 6px;">
            <div class="exp-title">Clinical Assessment Report (PDF)</div>
            <div class="exp-desc">
                Includes patient data, ML diagnosis, AI-generated intervention plan, and safety audit verdict.
            </div>
        </div>
        """, unsafe_allow_html=True)
    with dl2:
        st.markdown('<div style="padding-top: 10px;"></div>', unsafe_allow_html=True)
        st.download_button(
            label="Download PDF",
            data=pdf_bytes,
            file_name=f"PNAS_Report_{ml_prediction.lower().replace(' ', '_')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

# ─────────────────────────────────────────────────────────────────────────────
# EMPTY STATE — System Overview
# ─────────────────────────────────────────────────────────────────────────────
else:
    st.markdown("""
    <div class="sec">
        <span class="sec-num">02</span>
        <span class="sec-title">System Overview</span>
        <div class="sec-line"></div>
    </div>
    <p style="font-size: 14px; color: #5C4A3A; line-height: 1.7; margin-bottom: 4px;">
        System ready. Fill in the Patient Intake Form above and click
        <strong>Initialize Clinical Assessment</strong> to begin.
    </p>
    <div class="arch-grid">
        <div class="arch-card">
            <div class="arch-num">01</div>
            <div class="arch-ttl">Deterministic ML Model</div>
            <div class="arch-dsc">
                A Decision Tree model calculates the child's nutritional risk
                from anthropometric and dietary data, with no external dependencies.
            </div>
            <span class="arch-tag">Decision Tree · m2cgen</span>
        </div>
        <div class="arch-card">
            <div class="arch-num">02</div>
            <div class="arch-ttl">Multi-Agent AI Analysis</div>
            <div class="arch-dsc">
                Specialised AI agents produce hyper-local, budget-specific interventions
                guided by UNICEF pediatric nutrition standards.
            </div>
            <span class="arch-tag">LangGraph · Gemini 2.5</span>
        </div>
        <div class="arch-card">
            <div class="arch-num">03</div>
            <div class="arch-ttl">CMO Safety Guardrail</div>
            <div class="arch-dsc">
                A dedicated critic agent acting as Chief Medical Officer audits
                all recommendations for safety and budget viability before output.
            </div>
            <span class="arch-tag">Critic Agent · Safety Audit</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# Close wrap
st.markdown('</div>', unsafe_allow_html=True)
