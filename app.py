"""
Industry Classification UI  —  streamlit run ui.py
"""

import streamlit as st
import json, os
from prompt import IndustryClassifier
import pandas as pd
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title="Industry Classifier",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Dark Design System ──────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:ital,opsz,wght@0,9..40,300;0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,300&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; color-scheme: dark; }
#MainMenu, footer, header { visibility: hidden; }

/* ─── Base page ─── */
.stApp { background: #0d0f18 !important; }
.block-container { padding: 2rem 2.5rem 3rem !important; max-width: 1400px !important; }

/* ─── Sidebar ─── */
[data-testid="stSidebar"] {
    background: #080a10 !important;
    border-right: 1px solid #1a1e2e !important;
}
[data-testid="stSidebar"] * { color: #8b95b0 !important; }
[data-testid="stSidebar"] h3 { color: #e2e8f8 !important; font-size: 0.95rem !important; font-weight: 600 !important; }
[data-testid="stSidebar"] h5 { color: #5a647a !important; font-size: 0.72rem !important; font-weight: 600 !important; text-transform: uppercase !important; letter-spacing: 0.8px !important; }
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: #131625 !important;
    border: 1px solid #232840 !important;
    color: #c8d4f0 !important;
    border-radius: 8px !important;
    font-size: 0.84rem !important;
}
[data-testid="stSidebar"] label {
    font-size: 0.72rem !important; font-weight: 600 !important;
    text-transform: uppercase !important; letter-spacing: 0.7px !important;
    color: #4a5470 !important;
}
[data-testid="stSidebar"] .stButton > button {
    width: 100% !important; background: #2563eb !important; color: #fff !important;
    border: none !important; border-radius: 8px !important;
    font-weight: 600 !important; font-size: 0.84rem !important;
    box-shadow: 0 4px 14px rgba(37,99,235,0.35) !important;
    transition: all 0.2s !important;
}
[data-testid="stSidebar"] .stButton > button:hover { background: #1d4ed8 !important; box-shadow: 0 4px 20px rgba(37,99,235,0.5) !important; }
[data-testid="stSidebar"] hr { border-color: #1a1e2e !important; margin: 0.8rem 0 !important; }
[data-testid="stSidebar"] [data-testid="stFileUploader"] {
    background: #131625 !important; border: 1px dashed #2a3050 !important;
    border-radius: 8px !important; padding: 0.5rem !important;
}

/* ─── Page header ─── */
.page-header { padding: 0.4rem 0 1.5rem; border-bottom: 1px solid #1a1e2e; margin-bottom: 1.5rem; }
.page-header h1 { font-size: 1.5rem; font-weight: 600; color: #e2e8f8; margin: 0 0 0.2rem; letter-spacing: -0.3px; }
.page-header p  { font-size: 0.84rem; color: #4a5470; margin: 0; }

/* ─── Section labels ─── */
.section-title {
    font-size: 0.7rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.9px; color: #3d4666; margin: 1.2rem 0 0.6rem;
}

/* ─── Stat cards ─── */
.stat-card {
    background: #131625;
    border: 1px solid #1e2438;
    border-radius: 10px;
    padding: 1rem 1.2rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.35), inset 0 1px 0 rgba(255,255,255,0.03);
}
.stat-card .label { font-size: 0.68rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px; color: #3d4666; margin-bottom: 0.35rem; }
.stat-card .value { font-size: 1.35rem; font-weight: 600; color: #c8d4f0; line-height: 1.1; }
.stat-card .value.blue  { color: #60a5fa; }
.stat-card .value.green { color: #4ade80; }
.stat-card .value.amber { color: #fbbf24; }
.stat-card .value.red   { color: #f87171; }

/* ─── Result / info panels ─── */
.result-panel {
    background: #131625;
    border: 1px solid #1e2438;
    border-radius: 10px;
    padding: 1.1rem 1.3rem;
    box-shadow: 0 2px 12px rgba(0,0,0,0.3), inset 0 1px 0 rgba(255,255,255,0.03);
}

/* ─── Badges ─── */
.badge { display: inline-block; padding: 0.2rem 0.65rem; border-radius: 999px; font-size: 0.72rem; font-weight: 600; }
.badge-blue  { background: rgba(37,99,235,0.2);  color: #93c5fd; border: 1px solid rgba(37,99,235,0.3); }
.badge-green { background: rgba(22,163,74,0.18); color: #86efac; border: 1px solid rgba(22,163,74,0.3); }
.badge-amber { background: rgba(217,119,6,0.18); color: #fcd34d; border: 1px solid rgba(217,119,6,0.3); }
.badge-red   { background: rgba(220,38,38,0.18); color: #fca5a5; border: 1px solid rgba(220,38,38,0.3); }
.badge-slate { background: rgba(71,85,105,0.25); color: #94a3b8;  border: 1px solid rgba(71,85,105,0.35); }

/* ─── Industries breakdown rows ─── */
.ind-row { display:flex; align-items:center; gap:0.8rem; padding:0.7rem 0; border-bottom:1px solid #1a1e2e; }
.ind-row:last-child { border-bottom:none; }
.ind-name { font-size:0.85rem; font-weight:500; color:#c8d4f0; flex:1; }
.ind-sub  { font-size:0.75rem; color:#3d4666; font-weight:400; }
.ind-pct  { font-size:0.85rem; font-weight:600; color:#60a5fa; min-width:3rem; text-align:right; }
.pct-bar-bg   { flex:2; background:#1a1e2e; border-radius:4px; height:4px; }
.pct-bar-fill { background: linear-gradient(90deg,#2563eb,#60a5fa); border-radius:4px; height:4px; }

/* ─── Reasoning box ─── */
.reasoning-box {
    background: rgba(37,99,235,0.07);
    border-left: 3px solid #2563eb;
    border-radius: 0 8px 8px 0;
    padding: 0.85rem 1rem;
    font-size: 0.83rem;
    color: #8b95b0;
    line-height: 1.7;
}

/* ─── Product chips ─── */
.chip-list { display:flex; flex-wrap:wrap; gap:0.3rem; margin-top:0.3rem; }
.chip {
    background: #0d0f18;
    color: #4a5470;
    border: 1px solid #1e2438;
    border-radius: 5px;
    padding: 0.15rem 0.45rem;
    font-size: 0.7rem;
    font-family: 'DM Mono', monospace;
}

/* ─── Empty state ─── */
.empty-state { text-align:center; padding:3.5rem 1rem; color:#2a3050; }
.empty-state .icon { font-size:2.2rem; margin-bottom:0.7rem; filter: grayscale(0.4) opacity(0.6); }
.empty-state p { font-size:0.85rem; color:#2a3050; margin:0; }

/* ─── Tabs ─── */
[data-testid="stTabs"] [data-baseweb="tab-list"] {
    background: transparent !important;
    border-bottom: 1px solid #1a1e2e !important;
    gap: 0.1rem;
}
[data-testid="stTabs"] [data-baseweb="tab"] {
    font-size: 0.82rem !important; font-weight: 500 !important;
    padding: 0.55rem 1.1rem !important; color: #3d4666 !important;
    background: transparent !important; border: none !important;
    border-radius: 6px 6px 0 0 !important;
    transition: color 0.15s !important;
}
[data-testid="stTabs"] [data-baseweb="tab"]:hover { color: #8b95b0 !important; }
[data-testid="stTabs"] [aria-selected="true"] { color: #60a5fa !important; border-bottom: 2px solid #2563eb !important; }

/* ─── Textarea — dark code editor look ─── */
.stTextArea > div { border-radius: 8px !important; }
.stTextArea textarea {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.8rem !important;
    line-height: 1.65 !important;
    border-radius: 8px !important;
    border: 1px solid #1e2438 !important;
    background: #080a10 !important;
    color: #7b92c4 !important;
    caret-color: #60a5fa !important;
    padding: 0.9rem 1rem !important;
    box-shadow: inset 0 2px 8px rgba(0,0,0,0.4) !important;
}
.stTextArea textarea::placeholder { color: #232840 !important; }
.stTextArea textarea:focus {
    border-color: #2563eb !important;
    box-shadow: inset 0 2px 8px rgba(0,0,0,0.4), 0 0 0 3px rgba(37,99,235,0.15) !important;
    outline: none !important;
}

/* ─── Buttons ─── */
.stButton > button { border-radius: 8px !important; font-weight: 500 !important; font-size: 0.83rem !important; transition: all 0.2s !important; }
[data-testid="stBaseButton-primary"] {
    background: #2563eb !important; border: none !important; color: #fff !important;
    box-shadow: 0 4px 14px rgba(37,99,235,0.35) !important;
}
[data-testid="stBaseButton-primary"]:hover { background: #1d4ed8 !important; box-shadow: 0 4px 20px rgba(37,99,235,0.5) !important; }
[data-testid="stBaseButton-secondary"] {
    background: #131625 !important; border: 1px solid #1e2438 !important;
    color: #4a5470 !important;
}
[data-testid="stBaseButton-secondary"]:hover { background: #1a1e2e !important; color: #8b95b0 !important; border-color: #2a3050 !important; }

/* ─── Slider ─── */
[data-testid="stSlider"] [data-baseweb="slider"] [role="slider"] { background: #2563eb !important; }

/* ─── Progress bar ─── */
[data-testid="stProgress"] > div > div { background: linear-gradient(90deg,#2563eb,#60a5fa) !important; border-radius: 4px !important; }
[data-testid="stProgress"] > div { background: #1a1e2e !important; border-radius: 4px !important; }

/* ─── Alerts ─── */
[data-testid="stAlert"] { border-radius: 8px !important; font-size: 0.83rem !important; }
div[data-testid="stAlert"][class*="success"] { background: rgba(22,163,74,0.1) !important; border-color: rgba(22,163,74,0.3) !important; color: #86efac !important; }
div[data-testid="stAlert"][class*="error"]   { background: rgba(220,38,38,0.1) !important;  border-color: rgba(220,38,38,0.3) !important;  color: #fca5a5 !important; }
div[data-testid="stAlert"][class*="warning"] { background: rgba(217,119,6,0.1) !important;  border-color: rgba(217,119,6,0.3) !important;  color: #fcd34d !important; }
div[data-testid="stAlert"][class*="info"]    { background: rgba(37,99,235,0.1) !important;  border-color: rgba(37,99,235,0.3) !important;  color: #93c5fd !important; }

/* ─── Expander ─── */
[data-testid="stExpander"] {
    background: #131625 !important;
    border: 1px solid #1e2438 !important;
    border-radius: 8px !important;
    box-shadow: 0 2px 8px rgba(0,0,0,0.2) !important;
}
[data-testid="stExpander"] summary { font-size: 0.83rem !important; font-weight: 500 !important; color: #5a647a !important; }
[data-testid="stExpander"] summary:hover { color: #8b95b0 !important; }

/* ─── Dataframe — NUCLEAR OPTION: Force visible text ─── */
[data-testid="stDataFrame"] {
    border-radius: 10px !important;
    overflow: hidden !important;
    border: 1px solid #1e2438 !important;
    background: #0d0f18 !important;
}

/* Target ALL possible text elements with maximum specificity */
[data-testid="stDataFrame"] *,
[data-testid="stDataFrame"] div,
[data-testid="stDataFrame"] span,
[data-testid="stDataFrame"] p,
[data-testid="stDataFrame"] td,
[data-testid="stDataFrame"] th,
[data-testid="stDataFrame"] [role="cell"],
[data-testid="stDataFrame"] [role="columnheader"],
[data-testid="stDataFrame"] [class*="cell"],
[data-testid="stDataFrame"] [class*="Cell"],
[data-testid="stDataFrame"] [data-testid*="cell"] {
    color: #c9d8f0 !important;
    background: transparent !important;
}

/* Headers - darker text */
[data-testid="stDataFrame"] thead *,
[data-testid="stDataFrame"] th,
[data-testid="stDataFrame"] [role="columnheader"] {
    background: #131625 !important;
    color: #6b7a99 !important;
    font-size: 0.72rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.6px !important;
    font-weight: 600 !important;
}

/* Table structure */
[data-testid="stDataFrame"] table {
    background: #0d0f18 !important;
}

[data-testid="stDataFrame"] tbody {
    background: #0d0f18 !important;
}

[data-testid="stDataFrame"] tr {
    background: #0d0f18 !important;
}

[data-testid="stDataFrame"] td {
    background: #0d0f18 !important;
    color: #c9d8f0 !important;
    border-bottom: 1px solid #1a1e2e !important;
    font-size: 0.83rem !important;
    padding: 0.6rem 0.8rem !important;
}

/* Hover */
[data-testid="stDataFrame"] tr:hover,
[data-testid="stDataFrame"] tr:hover td,
[data-testid="stDataFrame"] tr:hover * {
    background: #161b27 !important;
    color: #e8edf8 !important;
}

/* Selected/Active cells */
[data-testid="stDataFrame"] [aria-selected="true"],
[data-testid="stDataFrame"] [aria-selected="true"] *,
[data-testid="stDataFrame"] .selected,
[data-testid="stDataFrame"] .active {
    background: #1c2235 !important;
    color: #e8edf8 !important;
}

/* ─── Caption ─── */
[data-testid="stCaptionContainer"] p { color: #2a3050 !important; font-size: 0.78rem !important; }

/* ─── Divider ─── */
hr { border-color: #1a1e2e !important; }

/* ─── Scrollbar ─── */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: #0d0f18; }
::-webkit-scrollbar-thumb { background: #1e2438; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #2a3050; }
</style>
""", unsafe_allow_html=True)

# ── Session state ────────────────────────────────────────────────────────────
for k, v in [("classifier", None), ("results", []), ("loaded_data", []),
             ("current_result", None), ("test_org", "")]:
    if k not in st.session_state:
        st.session_state[k] = v

# Auto-initialize classifier if OPENAI_API_KEY env var exists (only once)
if "auto_init_done" not in st.session_state:
    st.session_state.auto_init_done = False

if not st.session_state.auto_init_done and os.getenv("OPENAI_API_KEY"):
    try:
        st.session_state.classifier = IndustryClassifier(model="gpt-4o-mini")
        st.session_state.auto_init_done = True
    except:
        pass  # silent fail, user can manually init if env var is invalid

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏭 Industry Classifier")
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("##### Configuration")

    # Only show API key input if env var is NOT set
    env_key_exists = bool(os.getenv("OPENAI_API_KEY"))
    
    if env_key_exists:
        st.markdown(
            '<p style="font-size:0.78rem;color:#4a5470;line-height:1.5;">API key loaded from environment variable.</p>',
            unsafe_allow_html=True
        )
        api_key = os.getenv("OPENAI_API_KEY")
    else:
        api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...", value="")
    
    model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o"],
                         help="gpt-4o-mini — fast & cheap  |  gpt-4o — highest accuracy")

    # Only show init button if not auto-initialized OR if manually entering key
    if not env_key_exists or not st.session_state.classifier:
        if st.button("Initialize Classifier", type="primary"):
            if api_key:
                try:
                    st.session_state.classifier = IndustryClassifier(api_key=api_key, model=model)
                    st.success(f"Ready — {model}")
                except Exception as e:
                    st.error(str(e))
            else:
                st.warning("Enter your API key first.")
    else:
        # Show current model and allow model switching
        if st.button("Switch Model", type="primary"):
            try:
                st.session_state.classifier = IndustryClassifier(api_key=api_key, model=model)
                st.success(f"Switched to {model}")
            except Exception as e:
                st.error(str(e))
                st.success(f"Ready — {model}")
            except Exception as e:
                st.error(str(e))
        else:
            st.warning("Enter your API key first.")

    dot_col = "#4ade80" if st.session_state.classifier else "#f87171"
    dot_txt = "Classifier active" if st.session_state.classifier else "Not initialized"
    st.markdown(f'<p style="font-size:0.75rem;color:{dot_col};margin-top:0.2rem;font-weight:500;">● {dot_txt}</p>', unsafe_allow_html=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("##### Data Input")
    uploaded_file = st.file_uploader("Upload JSON file", type=["json"])
    if uploaded_file:
        try:
            st.session_state.loaded_data = json.load(uploaded_file)
            st.success(f"{len(st.session_state.loaded_data):,} organizations loaded")
        except Exception as e:
            st.error(f"Parse error: {e}")

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<p style="font-size:0.75rem;color:#2a3050;line-height:1.65;">Classify organizations into industries using OpenAI GPT based on their product portfolio.</p>', unsafe_allow_html=True)

# ── Page header ───────────────────────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <h1>Industry Classification</h1>
    <p>Analyze product portfolios and classify organizations into industry segments using AI</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Single Classification", "Batch Processing", "Results Analysis"])


# ════════════════════════════════════════════════════════════
#  TAB 1 — Single Classification
# ════════════════════════════════════════════════════════════
with tab1:
    left, right = st.columns([1, 1], gap="large")

    with left:
        st.markdown('<p class="section-title">Organization JSON Input</p>', unsafe_allow_html=True)

        if st.button("Load sample data", key="load_sample"):
            sample = {
                "_id": "sample_001", "orgName": "Sample Printing Co.", "countryCode": "US",
                "product_names": [
                    {"productName": "UV Cyan Ink",      "unit": "Kg"},
                    {"productName": "Offset Magenta",   "unit": "Kg"},
                    {"productName": "UV Varnish",        "unit": "L"},
                    {"productName": "Flexo Black Ink",  "unit": "Kg"},
                    {"productName": "Printing Blanket", "unit": "m"},
                ],
            }
            st.session_state.test_org = json.dumps(sample, indent=2)

        org_json_input = st.text_area(
            label="JSON", height=340,
            value=st.session_state.test_org,
            label_visibility="collapsed",
            placeholder='{\n  "_id": "...",\n  "orgName": "...",\n  "product_names": [...]\n}',
        )

        if st.button("Classify Organization →", type="primary", use_container_width=True, key="classify_single"):
            if not st.session_state.classifier:
                st.error("Initialize the classifier in the sidebar first.")
            else:
                try:
                    org_data = json.loads(org_json_input)
                    with st.spinner("Classifying…"):
                        st.session_state.current_result = st.session_state.classifier.classify_organization(org_data)
                    st.success("Classification complete.")
                except json.JSONDecodeError:
                    st.error("Invalid JSON — check your input format.")
                except Exception as e:
                    st.error(str(e))

    with right:
        st.markdown('<p class="section-title">Classification Result</p>', unsafe_allow_html=True)

        res = st.session_state.current_result
        if not res:
            st.markdown('<div class="empty-state"><div class="icon">🔍</div><p>Results will appear here after classification.</p></div>', unsafe_allow_html=True)
        elif "error" in res.get("classification", {}):
            st.error(res["classification"]["error"])
        else:
            clf = res.get("classification", {})

            # Stat cards row
            c1, c2, c3 = st.columns(3)
            def _stat(col, label, value, cls=""):
                col.markdown(f'<div class="stat-card"><div class="label">{label}</div><div class="value {cls}">{value}</div></div>', unsafe_allow_html=True)

            _stat(c1, "Organization", res.get("orgName", "—"))
            _stat(c2, "Country", res.get("countryCode") or "—")
            conf = res.get("confidenceScore", clf.get("confidenceScore", 0))
            _stat(c3, "Confidence", f"{conf:.0%}", "green" if conf >= 0.85 else ("amber" if conf >= 0.65 else "red"))

            # Summary strip
            st.markdown('<p class="section-title" style="margin-top:1.2rem;">Summary</p>', unsafe_allow_html=True)
            is_multi = clf.get("isMultiIndustry", False)
            btype    = res.get("operationType", clf.get("operationType", "—"))
            primary  = res.get("primaryIndustry", clf.get("primaryIndustry", "—"))
            multi_b  = '<span class="badge badge-amber">Multi-Industry</span>' if is_multi else '<span class="badge badge-slate">Single Industry</span>'
            st.markdown(f"""
<div class="result-panel" style="display:flex;gap:1.2rem;flex-wrap:wrap;align-items:center;padding:0.9rem 1.2rem;">
  <div>
    <div style="font-size:0.65rem;color:#2a3050;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:4px;font-weight:600;">Primary Industry</div>
    <span style="font-size:0.95rem;font-weight:600;color:#c8d4f0;">{primary}</span>
  </div>
  <div style="width:1px;background:#1e2438;height:32px;flex-shrink:0;"></div>
  <div>
    <div style="font-size:0.65rem;color:#2a3050;text-transform:uppercase;letter-spacing:0.8px;margin-bottom:4px;font-weight:600;">Operation Type</div>
    <span class="badge badge-blue">{btype}</span>
  </div>
  <div style="width:1px;background:#1e2438;height:32px;flex-shrink:0;"></div>
  <div>{multi_b}</div>
</div>
""", unsafe_allow_html=True)

            # Industries breakdown
            st.markdown('<p class="section-title">Industries Breakdown</p>', unsafe_allow_html=True)
            rows_html = ""
            for ind in clf.get("industries", []):
                pct   = ind.get("percentage", 0)
                chips = "".join(f'<span class="chip">{p}</span>' for p in ind.get("sampleProducts", []))
                rows_html += f"""
<div class="ind-row">
  <div style="flex:3;min-width:0;">
    <div class="ind-name">{ind.get('industry','—')} <span class="ind-sub">/ {ind.get('subCategory','—')}</span></div>
    <div class="chip-list">{chips}</div>
  </div>
  <div style="flex:2;padding:0 0.7rem;">
    <div class="pct-bar-bg"><div class="pct-bar-fill" style="width:{pct}%;"></div></div>
  </div>
  <div class="ind-pct">{pct}%</div>
</div>"""
            st.markdown(f'<div class="result-panel" style="padding:0.3rem 1.2rem;">{rows_html}</div>', unsafe_allow_html=True)

            # Reasoning
            st.markdown('<p class="section-title">AI Reasoning</p>', unsafe_allow_html=True)
            st.markdown(f'<div class="reasoning-box">{res.get("AIreasoning", clf.get("reasoning","—"))}</div>', unsafe_allow_html=True)

            # Raw JSON with proper formatting and copy button
            with st.expander("View raw JSON"):
                json_str = json.dumps(res, indent=2, ensure_ascii=False)
                st.code(json_str, language="json", line_numbers=False)
                st.download_button(
                    label="📋 Copy JSON",
                    data=json_str,
                    file_name=f"classification_{res.get('_id', 'result')}.json",
                    mime="application/json",
                    key=f"copy_json_{res.get('_id')}"
                )


# ════════════════════════════════════════════════════════════
#  TAB 2 — Batch Processing
# ════════════════════════════════════════════════════════════
with tab2:
    if not st.session_state.loaded_data:
        st.markdown('<div class="empty-state"><div class="icon">📁</div><p>Upload a JSON file in the sidebar to begin batch processing.</p></div>', unsafe_allow_html=True)
    else:
        total_orgs = len(st.session_state.loaded_data)
        cl, cr = st.columns([3, 1], gap="large")
        with cl:
            st.markdown('<p class="section-title">Select batch size</p>', unsafe_allow_html=True)
            max_items = st.slider("orgs", min_value=1, max_value=min(total_orgs, 100),
                                  value=min(5, total_orgs), label_visibility="collapsed")
            st.caption(f"Processing **{max_items}** of **{total_orgs:,}** loaded organizations")
        with cr:
            st.markdown('<p class="section-title">&nbsp;</p>', unsafe_allow_html=True)
            run_batch = st.button("Run Batch →", type="primary", use_container_width=True, key="run_batch")

        if run_batch:
            if not st.session_state.classifier:
                st.error("Initialize the classifier in the sidebar first.")
            else:
                progress_bar  = st.progress(0)
                status_ph     = st.empty()
                batch_results = []
                for i, org in enumerate(st.session_state.loaded_data[:max_items]):
                    name = org.get("orgName", "Unknown")
                    status_ph.caption(f"Processing {i+1} / {max_items} — {name}")
                    try:
                        batch_results.append(st.session_state.classifier.classify_organization(org))
                    except Exception as e:
                        batch_results.append({"orgName": name,
                                              "classification": {"error": str(e)}})
                    progress_bar.progress((i + 1) / max_items)
                st.session_state.results = batch_results
                status_ph.empty()
                st.success(f"Batch complete — {len(batch_results)} organizations classified.")

        if st.session_state.results:
            results = st.session_state.results
            good = [r for r in results if "error" not in r.get("classification", {})]
            errs = [r for r in results if "error"     in r.get("classification", {})]

            st.markdown("<hr>", unsafe_allow_html=True)
            st.markdown('<p class="section-title">Batch Summary</p>', unsafe_allow_html=True)

            multi_n  = sum(1 for r in good if r["classification"].get("isMultiIndustry"))
            avg_conf = sum(r.get("confidenceScore", r.get("classification", {}).get("confidenceScore", 0)) for r in good) / len(good) if good else 0
            s1, s2, s3, s4 = st.columns(4)
            def _sc(col, lbl, val, cls=""):
                col.markdown(f'<div class="stat-card"><div class="label">{lbl}</div><div class="value {cls}">{val}</div></div>', unsafe_allow_html=True)
            _sc(s1, "Processed",      f"{len(results):,}")
            _sc(s2, "Successful",     f"{len(good):,}",  "green")
            _sc(s3, "Multi-Industry", f"{multi_n:,}",    "blue")
            _sc(s4, "Avg Confidence", f"{avg_conf:.0%}", "green" if avg_conf >= 0.85 else "amber")

            st.markdown('<p class="section-title" style="margin-top:1.4rem;">Results Table</p>', unsafe_allow_html=True)
            rows = []
            for r in results:
                clf = r.get("classification", {})
                rows.append({
                    "Organization":    r.get("orgName", "—"),
                    "Primary Industry": r.get("primaryIndustry", clf.get("primaryIndustry", "Error" if "error" in clf else "—")),
                    "Operation Type":  r.get("operationType", clf.get("operationType", "—")),
                    "Multi-Industry":  "Yes" if clf.get("isMultiIndustry") else "No",
                    "Confidence":      f'{r.get("confidenceScore", clf.get("confidenceScore",0)):.0%}' if "error" not in clf else "—",
                })
            st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)

            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.download_button("Download results (JSON)",
                               data=json.dumps(results, ensure_ascii=False, indent=2),
                               file_name=f"classification_{ts}.json", mime="application/json")

            if errs:
                with st.expander(f"⚠ {len(errs)} failed classification(s)"):
                    for r in errs:
                        st.markdown(f"**{r.get('orgName','Unknown')}** — `{r['classification'].get('error','Unknown error')}`")


# ════════════════════════════════════════════════════════════
#  TAB 3 — Results Analysis
# ════════════════════════════════════════════════════════════
with tab3:
    results = [r for r in st.session_state.results if "error" not in r.get("classification", {})]

    if not results:
        st.markdown('<div class="empty-state"><div class="icon">📈</div><p>Run a batch classification to see analysis charts.</p></div>', unsafe_allow_html=True)
    else:
        # Dark chart theme — plot_bgcolor lives ONLY in LAYOUT, never repeated
        COLORS = ["#2563eb","#3b82f6","#60a5fa","#93c5fd","#1d4ed8","#7c3aed"]
        BG = "#131625"
        LAYOUT = dict(
            paper_bgcolor=BG,
            plot_bgcolor=BG,
            font=dict(family="DM Sans", size=11, color="#4a5470"),
            margin=dict(t=30, b=20, l=10, r=10),
        )

        ch1, ch2 = st.columns([3, 2], gap="large")

        with ch1:
            st.markdown('<p class="section-title">Primary Industry Distribution</p>', unsafe_allow_html=True)
            ind_count = {}
            for r in results:
                k = r.get("primaryIndustry", r.get("classification", {}).get("primaryIndustry", "Unknown"))
                ind_count[k] = ind_count.get(k, 0) + 1
            df_ind = pd.DataFrame(sorted(ind_count.items(), key=lambda x: x[1], reverse=True), columns=["Industry","Count"])
            fig_bar = px.bar(df_ind, x="Count", y="Industry", orientation="h",
                             color="Count", color_continuous_scale=["#1e2438","#2563eb"])
            fig_bar.update_layout(**LAYOUT,
                                  showlegend=False,
                                  coloraxis_showscale=False,
                                  yaxis=dict(autorange="reversed", tickfont=dict(size=11), gridcolor="#1a1e2e", color="#4a5470"),
                                  xaxis=dict(gridcolor="#1a1e2e", color="#4a5470"),
                                  height=min(56*len(df_ind)+60, 380))
            fig_bar.update_traces(marker_line_width=0)
            st.plotly_chart(fig_bar, use_container_width=True)

        with ch2:
            st.markdown('<p class="section-title">Operation Type Breakdown</p>', unsafe_allow_html=True)
            bt_count = {}
            for r in results:
                k = r.get("operationType", r["classification"].get("operationType", "Unknown"))
                bt_count[k] = bt_count.get(k, 0) + 1
            fig_pie = go.Figure(go.Pie(
                labels=list(bt_count.keys()), values=list(bt_count.values()),
                hole=0.58, marker=dict(colors=COLORS, line=dict(color="#0d0f18", width=3)),
                textfont=dict(size=10, color="#4a5470"),
                hovertemplate="%{label}<br>%{value} orgs (%{percent})<extra></extra>",
            ))
            fig_pie.update_layout(**LAYOUT,
                                  height=290,
                                  showlegend=True,
                                  legend=dict(font=dict(size=10, color="#4a5470"), bgcolor="rgba(0,0,0,0)"))
            st.plotly_chart(fig_pie, use_container_width=True)

        ch3, ch4 = st.columns(2, gap="large")

        with ch3:
            st.markdown('<p class="section-title">Confidence Score Distribution</p>', unsafe_allow_html=True)
            confs = [r.get("confidenceScore", r.get("classification", {}).get("confidenceScore", 0)) for r in results]
            fig_hist = px.histogram(x=confs, nbins=15, color_discrete_sequence=["#2563eb"])
            fig_hist.update_layout(**LAYOUT,
                                   height=240,
                                   xaxis=dict(tickformat=".0%", gridcolor="#1a1e2e", color="#4a5470"),
                                   yaxis=dict(gridcolor="#1a1e2e", color="#4a5470"),
                                   bargap=0.1)
            fig_hist.update_traces(marker_line_width=0)
            st.plotly_chart(fig_hist, use_container_width=True)

        with ch4:
            st.markdown('<p class="section-title">Single vs Multi-Industry</p>', unsafe_allow_html=True)
            multi_n  = sum(1 for r in results if r["classification"].get("isMultiIndustry"))
            single_n = len(results) - multi_n
            fig_sm = go.Figure(go.Bar(
                x=["Single Industry","Multi-Industry"], y=[single_n, multi_n],
                marker_color=["#2563eb","#7c3aed"], width=[0.45, 0.45],
            ))
            fig_sm.update_layout(**LAYOUT,
                                 height=240,
                                 yaxis=dict(gridcolor="#1a1e2e", color="#4a5470"),
                                 xaxis=dict(color="#4a5470"),
                                 showlegend=False)
            fig_sm.update_traces(marker_line_width=0)
            st.plotly_chart(fig_sm, use_container_width=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<p class="section-title">Top Industries — Organization Detail</p>', unsafe_allow_html=True)

        for industry, count in sorted(ind_count.items(), key=lambda x: x[1], reverse=True)[:6]:
            with st.expander(f"{industry}  ·  {count} org{'s' if count != 1 else ''}"):
                for o in [r for r in results if r.get("primaryIndustry", r.get("classification", {}).get("primaryIndustry")) == industry][:8]:
                    c2       = o["classification"]
                    conf_val = o.get("confidenceScore", c2.get("confidenceScore", 0))
                    conf_col = "#4ade80" if conf_val >= 0.85 else ("#fbbf24" if conf_val >= 0.65 else "#f87171")
                    st.markdown(
                        f'<div style="display:flex;justify-content:space-between;align-items:center;'
                        f'padding:0.5rem 0;border-bottom:1px solid #1a1e2e;font-size:0.83rem;">'
                        f'<span style="color:#8b95b0;font-weight:500;">{o.get("orgName","—")}</span>'
                        f'<span style="display:flex;gap:0.6rem;align-items:center;">'
                        f'<span class="badge badge-slate">{o.get("operationType", c2.get("operationType","—"))}</span>'
                        f'<span style="font-size:0.76rem;font-weight:600;color:{conf_col};">{conf_val:.0%}</span>'
                        f'</span></div>',
                        unsafe_allow_html=True,
                    )