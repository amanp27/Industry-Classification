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

# ─────────────────────────────────────────────
#  Page bootstrap
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Industry Classifier",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  Design system via CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2rem 2.5rem 3rem; max-width: 1400px; }

[data-testid="stSidebar"] { background: #0f1117; border-right: 1px solid #1e2130; }
[data-testid="stSidebar"] * { color: #c9d1e0 !important; }
[data-testid="stSidebar"] .stTextInput input,
[data-testid="stSidebar"] .stSelectbox > div > div {
    background: #1a1d2e !important; border: 1px solid #2a2f45 !important;
    color: #e8ecf4 !important; border-radius: 8px !important; font-size: 0.85rem !important;
}
[data-testid="stSidebar"] .stButton > button {
    width: 100%; background: #2563eb !important; color: white !important;
    border: none !important; border-radius: 8px !important;
    padding: 0.55rem 1rem !important; font-weight: 600 !important;
    font-size: 0.85rem !important; letter-spacing: 0.3px;
}
[data-testid="stSidebar"] label {
    font-size: 0.78rem !important; font-weight: 500 !important;
    text-transform: uppercase !important; letter-spacing: 0.6px !important;
    color: #6b7a99 !important;
}
[data-testid="stSidebar"] hr { border-color: #1e2130 !important; }

.page-header { padding: 0.5rem 0 1.8rem; border-bottom: 1px solid #e5e9f2; margin-bottom: 1.8rem; }
.page-header h1 { font-size: 1.55rem; font-weight: 600; color: #0f172a; margin: 0 0 0.2rem; letter-spacing: -0.3px; }
.page-header p  { font-size: 0.88rem; color: #64748b; margin: 0; font-weight: 400; }

.stat-card { background: #ffffff; border: 1px solid #e5e9f2; border-radius: 12px; padding: 1.1rem 1.25rem; }
.stat-card .label { font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.7px; color: #94a3b8; margin-bottom: 0.35rem; }
.stat-card .value { font-size: 1.45rem; font-weight: 600; color: #0f172a; line-height: 1; }
.stat-card .value.blue  { color: #2563eb; }
.stat-card .value.green { color: #16a34a; }
.stat-card .value.amber { color: #d97706; }
.stat-card .value.red   { color: #dc2626; }

.section-title { font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.8px; color: #94a3b8; margin: 1.4rem 0 0.7rem; }

.result-panel { background: #f8fafc; border: 1px solid #e5e9f2; border-radius: 12px; padding: 1.4rem 1.6rem; }

.badge { display: inline-block; padding: 0.22rem 0.7rem; border-radius: 999px; font-size: 0.75rem; font-weight: 600; letter-spacing: 0.3px; }
.badge-blue  { background:#dbeafe; color:#1d4ed8; }
.badge-green { background:#dcfce7; color:#15803d; }
.badge-amber { background:#fef3c7; color:#b45309; }
.badge-red   { background:#fee2e2; color:#b91c1c; }
.badge-slate { background:#f1f5f9; color:#475569; }

.ind-row { display:flex; align-items:center; gap:0.8rem; padding:0.75rem 0; border-bottom:1px solid #f1f5f9; }
.ind-row:last-child { border-bottom:none; }
.ind-name { font-size:0.88rem; font-weight:500; color:#1e293b; flex:1; }
.ind-sub  { font-size:0.78rem; color:#64748b; }
.ind-pct  { font-size:0.88rem; font-weight:600; color:#2563eb; min-width:3rem; text-align:right; }
.pct-bar-bg   { flex:2; background:#e2e8f0; border-radius:4px; height:6px; }
.pct-bar-fill { background:#2563eb; border-radius:4px; height:6px; }

.reasoning-box { background:#eff6ff; border-left:3px solid #2563eb; border-radius:0 8px 8px 0; padding:0.9rem 1.1rem; font-size:0.86rem; color:#334155; line-height:1.6; margin-top:0.5rem; }

.chip-list { display:flex; flex-wrap:wrap; gap:0.4rem; margin-top:0.4rem; }
.chip { background:#f1f5f9; color:#475569; border-radius:6px; padding:0.2rem 0.55rem; font-size:0.75rem; font-family:'DM Mono',monospace; }

.empty-state { text-align:center; padding:3rem 1rem; color:#94a3b8; }
.empty-state .icon { font-size:2.5rem; margin-bottom:0.8rem; }
.empty-state p { font-size:0.88rem; margin:0; }

[data-testid="stTabs"] [data-baseweb="tab-list"] { gap:0.2rem; border-bottom:1px solid #e5e9f2; background:transparent; }
[data-testid="stTabs"] [data-baseweb="tab"] { font-size:0.83rem !important; font-weight:500 !important; padding:0.5rem 1rem !important; border-radius:6px 6px 0 0 !important; color:#64748b !important; background:transparent !important; border:none !important; }
[data-testid="stTabs"] [aria-selected="true"] { color:#2563eb !important; border-bottom:2px solid #2563eb !important; }

.stTextArea textarea { font-family:'DM Mono',monospace !important; font-size:0.8rem !important; border-radius:8px !important; border-color:#e5e9f2 !important; background:#fafbfc !important; }

.stButton > button { border-radius:8px !important; font-weight:500 !important; font-size:0.84rem !important; }
[data-testid="stBaseButton-primary"] { background:#2563eb !important; border-color:#2563eb !important; }

hr { border-color:#e5e9f2 !important; }
[data-testid="stAlert"] { border-radius:8px !important; font-size:0.85rem !important; }
[data-testid="stDataFrame"] { border-radius:10px; overflow:hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  Session state
# ─────────────────────────────────────────────
for k, v in [("classifier", None), ("results", []), ("loaded_data", []),
             ("current_result", None), ("test_org", "")]:
    if k not in st.session_state:
        st.session_state[k] = v

# ─────────────────────────────────────────────
#  Sidebar
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏭 Industry Classifier")
    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown("##### Configuration")
    api_key = st.text_input("OpenAI API Key", type="password", placeholder="sk-...",
                             value=os.getenv("OPENAI_API_KEY", ""))
    model = st.selectbox("Model", ["gpt-4o-mini", "gpt-4o"],
                         help="gpt-4o-mini — fast & cheap  |  gpt-4o — highest accuracy")

    if st.button("Initialize Classifier", type="primary"):
        if api_key:
            try:
                st.session_state.classifier = IndustryClassifier(api_key=api_key, model=model)
                st.success(f"Ready — {model}")
            except Exception as e:
                st.error(str(e))
        else:
            st.warning("Enter your API key first.")

    if st.session_state.classifier:
        st.markdown('<p style="font-size:0.78rem;color:#22c55e;margin-top:0.3rem;">● Classifier active</p>', unsafe_allow_html=True)
    else:
        st.markdown('<p style="font-size:0.78rem;color:#ef4444;margin-top:0.3rem;">● Not initialized</p>', unsafe_allow_html=True)

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
    st.markdown('<p style="font-size:0.78rem;color:#6b7a99;line-height:1.6;">Classify organizations into industries using OpenAI GPT based on their product portfolio. Supports single-org testing and bulk batch processing.</p>', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  Page header
# ─────────────────────────────────────────────
st.markdown("""
<div class="page-header">
    <h1>Industry Classification</h1>
    <p>Analyze product portfolios and classify organizations into industry segments using AI</p>
</div>
""", unsafe_allow_html=True)

tab1, tab2, tab3 = st.tabs(["Single Classification", "Batch Processing", "Results Analysis"])


# ══════════════════════════════════════════════
#  TAB 1 — Single Classification
# ══════════════════════════════════════════════
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
            label="JSON",
            height=320,
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

            # Org stats
            c1, c2, c3 = st.columns(3)
            def _stat(col, label, value, cls=""):
                col.markdown(f'<div class="stat-card"><div class="label">{label}</div><div class="value {cls}">{value}</div></div>', unsafe_allow_html=True)

            _stat(c1, "Organization ID", res.get("_id", "—"))
            _stat(c2, "Country", res.get("countryCode") or "—")
            conf = clf.get("confidenceScore", 0)
            conf_cls = "green" if conf >= 0.85 else ("amber" if conf >= 0.65 else "red")
            _stat(c3, "Confidence", f"{conf:.0%}", conf_cls)

            # Summary badges
            st.markdown('<p class="section-title" style="margin-top:1.2rem;">Summary</p>', unsafe_allow_html=True)
            is_multi  = clf.get("isMultiIndustry", False)
            btype     = clf.get("businessType", "—")
            primary   = clf.get("primaryIndustry", "—")
            multi_badge = '<span class="badge badge-amber">Multi-Industry</span>' if is_multi else '<span class="badge badge-slate">Single Industry</span>'
            st.markdown(f"""
<div class="result-panel" style="display:flex;gap:1rem;flex-wrap:wrap;align-items:center;padding:0.9rem 1.2rem;">
  <div>
    <div style="font-size:0.68rem;color:#94a3b8;text-transform:uppercase;letter-spacing:0.6px;margin-bottom:3px;">Primary Industry</div>
    <span style="font-size:0.95rem;font-weight:600;color:#0f172a;">{primary}</span>
  </div>
  <div style="width:1px;background:#e5e9f2;height:30px;"></div>
  <div>
    <div style="font-size:0.68rem;color:#94a3b8;text-transform:uppercase;letter-spacing:0.6px;margin-bottom:3px;">Business Type</div>
    <span class="badge badge-blue">{btype}</span>
  </div>
  <div style="width:1px;background:#e5e9f2;height:30px;"></div>
  <div>{multi_badge}</div>
</div>
""", unsafe_allow_html=True)

            # Industries breakdown
            st.markdown('<p class="section-title">Industries Breakdown</p>', unsafe_allow_html=True)
            industries_html = ""
            for ind in clf.get("industries", []):
                pct   = ind.get("percentage", 0)
                chips = "".join(f'<span class="chip">{p}</span>' for p in ind.get("sampleProducts", []))
                industries_html += f"""
<div class="ind-row">
  <div style="flex:3;min-width:0;">
    <div class="ind-name">{ind.get('industry','—')} <span class="ind-sub">/ {ind.get('subCategory','—')}</span></div>
    <div class="chip-list">{chips}</div>
  </div>
  <div style="flex:2;padding:0 0.6rem;">
    <div class="pct-bar-bg"><div class="pct-bar-fill" style="width:{pct}%;"></div></div>
  </div>
  <div class="ind-pct">{pct}%</div>
</div>"""
            st.markdown(f'<div class="result-panel" style="padding:0.4rem 1.2rem;">{industries_html}</div>', unsafe_allow_html=True)

            # Reasoning
            st.markdown('<p class="section-title">AI Reasoning</p>', unsafe_allow_html=True)
            st.markdown(f'<div class="reasoning-box">{clf.get("reasoning","—")}</div>', unsafe_allow_html=True)

            with st.expander("View raw JSON"):
                st.json(res)


# ══════════════════════════════════════════════
#  TAB 2 — Batch Processing
# ══════════════════════════════════════════════
with tab2:
    if not st.session_state.loaded_data:
        st.markdown('<div class="empty-state"><div class="icon">📁</div><p>Upload a JSON file in the sidebar to begin batch processing.</p></div>', unsafe_allow_html=True)
    else:
        total_orgs = len(st.session_state.loaded_data)
        ctrl_left, ctrl_right = st.columns([3, 1], gap="large")

        with ctrl_left:
            st.markdown('<p class="section-title">Select batch size</p>', unsafe_allow_html=True)
            max_items = st.slider("Organizations to process", min_value=1,
                                  max_value=min(total_orgs, 100),
                                  value=min(5, total_orgs), label_visibility="collapsed")
            st.caption(f"Processing **{max_items}** of **{total_orgs:,}** loaded organizations")

        with ctrl_right:
            st.markdown('<p class="section-title">&nbsp;</p>', unsafe_allow_html=True)
            run_batch = st.button("Run Batch →", type="primary", use_container_width=True, key="run_batch")

        if run_batch:
            if not st.session_state.classifier:
                st.error("Initialize the classifier in the sidebar first.")
            else:
                progress_bar = st.progress(0)
                status_ph    = st.empty()
                batch_results = []
                for i, org in enumerate(st.session_state.loaded_data[:max_items]):
                    name = org.get("orgName", "Unknown")
                    status_ph.caption(f"Processing {i+1} / {max_items} — {name}")
                    try:
                        batch_results.append(st.session_state.classifier.classify_organization(org))
                    except Exception as e:
                        batch_results.append({"_id": org.get("_id"), "orgName": name,
                                              "countryCode": org.get("countryCode"),
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
            avg_conf = sum(r["classification"].get("confidenceScore", 0) for r in good) / len(good) if good else 0

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
                    "ID":               r.get("_id", "—"),
                    "Organization":     r.get("orgName", "—"),
                    "Country":          r.get("countryCode") or "—",
                    "Primary Industry": clf.get("primaryIndustry", "Error" if "error" in clf else "—"),
                    "Business Type":    clf.get("businessType", "—"),
                    "Multi-Industry":   "Yes" if clf.get("isMultiIndustry") else "No",
                    "Confidence":       f'{clf.get("confidenceScore", 0):.0%}' if "error" not in clf else "—",
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


# ══════════════════════════════════════════════
#  TAB 3 — Results Analysis
# ══════════════════════════════════════════════
with tab3:
    results = [r for r in st.session_state.results if "error" not in r.get("classification", {})]

    if not results:
        st.markdown('<div class="empty-state"><div class="icon">📈</div><p>Run a batch classification to see analysis charts.</p></div>', unsafe_allow_html=True)
    else:
        CHART_COLORS = ["#2563eb", "#3b82f6", "#60a5fa", "#93c5fd", "#bfdbfe"]
        LAYOUT = dict(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                      font=dict(family="DM Sans", size=12, color="#334155"),
                      margin=dict(t=40, b=20, l=20, r=20))

        ch1, ch2 = st.columns([3, 2], gap="large")

        with ch1:
            st.markdown('<p class="section-title">Primary Industry Distribution</p>', unsafe_allow_html=True)
            ind_count = {}
            for r in results:
                k = r["classification"].get("primaryIndustry", "Unknown")
                ind_count[k] = ind_count.get(k, 0) + 1
            df_ind = pd.DataFrame(sorted(ind_count.items(), key=lambda x: x[1], reverse=True), columns=["Industry", "Count"])
            fig_bar = px.bar(df_ind, x="Count", y="Industry", orientation="h",
                             color="Count", color_continuous_scale=["#bfdbfe", "#2563eb"])
            fig_bar.update_layout(**LAYOUT, showlegend=False, coloraxis_showscale=False,
                                  yaxis=dict(autorange="reversed", tickfont=dict(size=11)),
                                  xaxis=dict(gridcolor="#f1f5f9"),
                                  height=min(60 * len(df_ind) + 60, 380))
            fig_bar.update_traces(marker_line_width=0)
            st.plotly_chart(fig_bar, use_container_width=True)

        with ch2:
            st.markdown('<p class="section-title">Business Type Breakdown</p>', unsafe_allow_html=True)
            bt_count = {}
            for r in results:
                k = r["classification"].get("businessType", "Unknown")
                bt_count[k] = bt_count.get(k, 0) + 1
            fig_pie = go.Figure(go.Pie(labels=list(bt_count.keys()), values=list(bt_count.values()),
                                       hole=0.55, marker=dict(colors=CHART_COLORS, line=dict(color="#fff", width=2)),
                                       textfont=dict(size=11),
                                       hovertemplate="%{label}<br>%{value} orgs (%{percent})<extra></extra>"))
            fig_pie.update_layout(**LAYOUT, height=300, showlegend=True, legend=dict(font=dict(size=11)))
            st.plotly_chart(fig_pie, use_container_width=True)

        ch3, ch4 = st.columns(2, gap="large")

        with ch3:
            st.markdown('<p class="section-title">Confidence Score Distribution</p>', unsafe_allow_html=True)
            confs = [r["classification"].get("confidenceScore", 0) for r in results]
            fig_hist = px.histogram(x=confs, nbins=15, color_discrete_sequence=["#2563eb"])
            fig_hist.update_layout(**LAYOUT, xaxis_title="Confidence Score", yaxis_title="Count",
                                   xaxis=dict(tickformat=".0%", gridcolor="#f1f5f9"),
                                   yaxis=dict(gridcolor="#f1f5f9"), height=260, bargap=0.08)
            fig_hist.update_traces(marker_line_width=0)
            st.plotly_chart(fig_hist, use_container_width=True)

        with ch4:
            st.markdown('<p class="section-title">Single vs Multi-Industry</p>', unsafe_allow_html=True)
            multi_n  = sum(1 for r in results if r["classification"].get("isMultiIndustry"))
            single_n = len(results) - multi_n
            fig_sm = go.Figure(go.Bar(x=["Single Industry", "Multi-Industry"], y=[single_n, multi_n],
                                      marker_color=["#2563eb", "#f59e0b"], width=[0.4, 0.4]))
            fig_sm.update_layout(**LAYOUT, yaxis=dict(gridcolor="#f1f5f9"), height=260, showlegend=False)
            fig_sm.update_traces(marker_line_width=0)
            st.plotly_chart(fig_sm, use_container_width=True)

        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown('<p class="section-title">Top Industries — Organization Detail</p>', unsafe_allow_html=True)

        for industry, count in sorted(ind_count.items(), key=lambda x: x[1], reverse=True)[:6]:
            with st.expander(f"{industry}  ·  {count} organization{'s' if count != 1 else ''}"):
                for o in [r for r in results if r["classification"].get("primaryIndustry") == industry][:8]:
                    c2 = o["classification"]
                    conf_val = c2.get("confidenceScore", 0)
                    conf_col = "#16a34a" if conf_val >= 0.85 else ("#d97706" if conf_val >= 0.65 else "#dc2626")
                    st.markdown(
                        f'<div style="display:flex;justify-content:space-between;align-items:center;padding:0.5rem 0;border-bottom:1px solid #f1f5f9;font-size:0.84rem;">'
                        f'<span style="color:#1e293b;font-weight:500;">{o.get("orgName","—")}</span>'
                        f'<span style="display:flex;gap:0.6rem;align-items:center;">'
                        f'<span class="badge badge-slate">{c2.get("businessType","—")}</span>'
                        f'<span style="font-size:0.78rem;font-weight:600;color:{conf_col};">{conf_val:.0%}</span>'
                        f'</span></div>',
                        unsafe_allow_html=True,
                    )