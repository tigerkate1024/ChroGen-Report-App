
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from chronogene_agent.data_loader import load_tables, get_subject_payload
from chronogene_agent.model import train_baseline, get_target_scores, predict_subject
from chronogene_agent.report import (
    top_mechanisms,
    confidence_label,
    evidence_dataframe,
    ingredient_matches,
    generate_markdown_report,
)
from chronogene_agent.features import build_feature_table
from chronogene_agent.mechanisms import (
    MECHANISM_COLUMNS,
    MECHANISM_LABELS,
    MECHANISM_SHORT,
    FOLLOW_UP_METRICS,
)

st.set_page_config(page_title="ChronoGene Agent", page_icon="🧬", layout="wide", initial_sidebar_state="expanded")

CSS = """
<style>
:root {
  --ink: #152018;
  --muted: #6D756D;
  --green: #123D2A;
  --gold: #B9975B;
  --line: rgba(18, 61, 42, 0.12);
}
[data-testid="stAppViewContainer"] {
  background:
    radial-gradient(circle at top left, rgba(185,151,91,0.17), transparent 28rem),
    radial-gradient(circle at top right, rgba(18,61,42,0.13), transparent 26rem),
    linear-gradient(180deg, #FBF8F0 0%, #F3EFE4 100%);
}
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #10271D 0%, #193A2B 100%);
}
[data-testid="stSidebar"] * { color: #F6F1E7 !important; }
.main-title {
  font-size: 2.85rem;
  line-height: 1.03;
  letter-spacing: -0.05em;
  font-weight: 760;
  margin-bottom: 0.25rem;
  color: var(--ink);
}
.sub-title {
  color: var(--muted);
  font-size: 1.06rem;
  margin-bottom: 1.0rem;
}
.badge {
  display: inline-block;
  padding: 0.30rem 0.72rem;
  border-radius: 999px;
  background: rgba(18,61,42,0.08);
  border: 1px solid rgba(18,61,42,0.12);
  color: #123D2A;
  font-weight: 650;
  font-size: 0.86rem;
  margin-right: 0.35rem;
}
.gold-badge {
  background: rgba(185,151,91,0.13);
  border: 1px solid rgba(185,151,91,0.22);
  color: #7A5F2B;
}
.card {
  background: rgba(255,255,255,0.72);
  border: 1px solid var(--line);
  border-radius: 22px;
  padding: 1.15rem 1.15rem;
  box-shadow: 0 18px 48px rgba(22,33,24,0.065);
  backdrop-filter: blur(8px);
  min-height: 120px;
}
.metric-label {
  color: var(--muted);
  font-size: 0.82rem;
  font-weight: 650;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  margin-bottom: 0.35rem;
}
.metric-value {
  font-size: 1.52rem;
  font-weight: 760;
  color: var(--ink);
  line-height: 1.12;
}
.metric-note {
  color: var(--muted);
  font-size: 0.86rem;
  margin-top: 0.35rem;
}
.section-title {
  font-size: 1.35rem;
  font-weight: 760;
  color: var(--ink);
  margin-top: 0.25rem;
  margin-bottom: 0.55rem;
  letter-spacing: -0.02em;
}
.warning-box {
  background: rgba(185,151,91,0.12);
  border: 1px solid rgba(185,151,91,0.28);
  border-radius: 18px;
  padding: 0.85rem 1rem;
  color: #5F4A20;
}
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def load_cached(data_dir: str):
    return load_tables(data_dir)

@st.cache_resource(show_spinner=False)
def train_cached(data_dir: str):
    data = load_cached(data_dir)
    result = train_baseline(data.tables, ROOT / "models" / "ui_cached_model.joblib")
    import joblib
    bundle = joblib.load(ROOT / "models" / "ui_cached_model.joblib")
    return bundle, result

def agent_chat(question: str, scores: dict[str, float], payload: dict) -> str:
    top = top_mechanisms(scores, 3)
    q = question.lower().strip()
    if "为什么" in q or "why" in q or "机制" in q:
        mech, score = top[0]
        ev = evidence_dataframe(payload, mech).head(4)
        bullets = "\n".join([f"- {r['Evidence']}：{r['Value']}（{r['Interpretation']}）" for _, r in ev.iterrows()])
        return f"当前最强机制是 **{MECHANISM_LABELS[mech]}**（{score:.1f}/100）。主要证据包括：\n\n{bullets}\n\n这只是 synthetic demo 解释，不构成医学判断。"
    if "复测" in q or "12" in q or "follow" in q:
        items = []
        for mech, _ in top:
            items.extend(FOLLOW_UP_METRICS.get(mech, [])[:2])
        return "建议 12 周后优先复测：" + "、".join(dict.fromkeys(items)) + "。"
    if "成分" in q or "ingredient" in q:
        return "成分匹配应基于机制指纹，而不是直接按症状推荐。当前 demo 可以看 Ingredient Matching 页。"
    top_text = "、".join([f"{MECHANISM_LABELS[m]}({s:.0f})" for m, s in top])
    return f"这个 subject 当前 top 3 机制是：{top_text}。你可以问：为什么是这个机制、12周复测什么、哪些成分机制上更匹配。"

with st.sidebar:
    st.markdown("## 🧬 ChronoGene")
    st.markdown("**Mechanism Intelligence Console**")
    st.markdown("---")
    data_dir = st.text_input("Data folder", "data")
    try:
        data = load_cached(data_dir)
        st.success("Data loaded")
    except Exception as e:
        st.error(str(e))
        st.stop()

    subject_ids = data.tables["participants"]["subject_id"].astype(str).tolist()
    default_idx = subject_ids.index("CG0039") if "CG0039" in subject_ids else 0
    subject_id = st.selectbox("Subject", subject_ids, index=default_idx)
    mode = st.radio(
        "Score source",
        ["Use target scores (demo ground truth)", "Use baseline model prediction"],
        index=0,
    )
    st.markdown("---")
    st.markdown("### Data modules")
    for label, key in {
        "Face/Skin": "face_skin",
        "Lifestyle": "lifestyle",
        "Skin Genome": "genome",
        "Skin scRNA": "skin_scrna",
        "Oral Epithelial": "oral_epi",
        "Oral Microbiome": "oral_microbiome",
    }.items():
        st.markdown(f"✅ {label}: `{len(data.tables[key])}` rows")
    st.caption("Synthetic demo only. Not for diagnosis, treatment, or clinical decision-making.")

if mode.startswith("Use target"):
    scores = get_target_scores(data.tables, subject_id)
    mae = None
else:
    bundle, result = train_cached(data_dir)
    scores = predict_subject(data.tables, bundle, subject_id)
    mae = bundle.get("mae")

payload = get_subject_payload(data, subject_id)
participant = payload["participants"]
face = payload["face_skin"]
top3 = top_mechanisms(scores, 3)
conf_label, conf_score = confidence_label(participant.get("data_completeness", 0.7), mae)

st.markdown('<div class="main-title">ChronoGene Agent</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Multimodal aging mechanism intelligence for a 39-year-old female synthetic demo profile.</div>', unsafe_allow_html=True)
st.markdown(
    '<span class="badge">39F Synthetic Profile</span>'
    '<span class="badge">Mechanism Vector</span>'
    '<span class="badge gold-badge">Evidence Chain</span>'
    '<span class="badge gold-badge">12-Week Loop</span>',
    unsafe_allow_html=True,
)
st.markdown("")
st.markdown('<div class="warning-box">⚠️ <b>Synthetic demo only.</b> This UI is for product and engineering prototyping. It does not provide diagnosis, treatment, or medical advice.</div>', unsafe_allow_html=True)
st.markdown("")

c1, c2, c3, c4 = st.columns(4)
with c1:
    st.markdown(f"""
    <div class="card">
      <div class="metric-label">Dominant Mechanism</div>
      <div class="metric-value">{MECHANISM_LABELS[top3[0][0]]}</div>
      <div class="metric-note">{top3[0][1]:.1f}/100</div>
    </div>
    """, unsafe_allow_html=True)
with c2:
    st.markdown(f"""
    <div class="card">
      <div class="metric-label">Confidence</div>
      <div class="metric-value">{conf_label}</div>
      <div class="metric-note">{conf_score:.1f}/100 · completeness {participant.get("data_completeness")}</div>
    </div>
    """, unsafe_allow_html=True)
with c3:
    apparent = face.get("apparent_facial_age", np.nan)
    actual = participant.get("age", np.nan)
    gap = float(apparent) - float(actual)
    st.markdown(f"""
    <div class="card">
      <div class="metric-label">Facial Age Gap</div>
      <div class="metric-value">{gap:+.1f} yrs</div>
      <div class="metric-note">actual {actual} · apparent {apparent}</div>
    </div>
    """, unsafe_allow_html=True)
with c4:
    score_mode = "Target" if mode.startswith("Use target") else "Model"
    mae_note = f"MAE {mae:.2f}" if mae is not None else "MAE NA"
    st.markdown(f"""
    <div class="card">
      <div class="metric-label">Score Mode</div>
      <div class="metric-value">{score_mode}</div>
      <div class="metric-note">{mae_note}</div>
    </div>
    """, unsafe_allow_html=True)

tab_overview, tab_evidence, tab_matching, tab_followup, tab_chat = st.tabs(
    ["Overview", "Evidence Chain", "Ingredient Matching", "12-Week Loop", "Agent Chat"]
)

with tab_overview:
    left, right = st.columns([1.05, 0.95])
    score_df = pd.DataFrame({
        "Mechanism": [MECHANISM_LABELS[m] for m in MECHANISM_COLUMNS],
        "Short": [MECHANISM_SHORT[m] for m in MECHANISM_COLUMNS],
        "Score": [scores[m] for m in MECHANISM_COLUMNS],
    }).sort_values("Score", ascending=False)

    with left:
        st.markdown('<div class="section-title">Mechanism Vector</div>', unsafe_allow_html=True)
        fig = px.bar(
            score_df, x="Score", y="Mechanism", orientation="h", range_x=[0,100],
            text="Score", color="Score", color_continuous_scale=["#123D2A","#B9975B","#A54E2A"],
        )
        fig.update_layout(height=500, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False, yaxis={"categoryorder":"total ascending"})
        fig.update_traces(texttemplate="%{text:.1f}", textposition="outside")
        st.plotly_chart(fig, use_container_width=True)

    with right:
        st.markdown('<div class="section-title">Mechanism Radar</div>', unsafe_allow_html=True)
        fig = go.Figure()
        fig.add_trace(go.Scatterpolar(
            r=[scores[m] for m in MECHANISM_COLUMNS],
            theta=[MECHANISM_SHORT[m] for m in MECHANISM_COLUMNS],
            fill="toself",
            line=dict(width=3),
        ))
        fig.update_layout(height=500, polar=dict(radialaxis=dict(visible=True, range=[0,100])), showlegend=False, margin=dict(l=30,r=30,t=30,b=30), paper_bgcolor="rgba(0,0,0,0)")
        st.plotly_chart(fig, use_container_width=True)

    st.markdown('<div class="section-title">Subject Snapshot</div>', unsafe_allow_html=True)
    cols = st.columns(6)
    for col, (label, value) in zip(cols, [
        ("Age", participant.get("age")),
        ("Sex", participant.get("sex")),
        ("BMI", participant.get("BMI")),
        ("Sleep", payload["lifestyle"].get("sleep_hours")),
        ("Stress", payload["lifestyle"].get("stress_score_0_100")),
        ("UV", payload["lifestyle"].get("uv_exposure_score_0_100")),
    ]):
        with col:
            st.metric(label, value)

with tab_evidence:
    st.markdown('<div class="section-title">Top Mechanism Evidence Chain</div>', unsafe_allow_html=True)
    for mech, sc in top3:
        st.markdown(f"### {MECHANISM_LABELS[mech]} · {sc:.1f}/100")
        st.dataframe(evidence_dataframe(payload, mech), use_container_width=True, hide_index=True)
        with st.expander("Interpretation note"):
            st.write("真实产品中必须区分真实检测值、模型补全值、模型推断值和低置信假设。")

with tab_matching:
    st.markdown('<div class="section-title">Ingredient Mechanism Matching</div>', unsafe_allow_html=True)
    st.caption("This is not a recommendation engine. It is a demo of matching user mechanism state to ingredient perturbation fingerprints.")
    match_df = ingredient_matches(data.tables, scores)
    st.dataframe(match_df, use_container_width=True, hide_index=True)
    fig = px.bar(
        match_df.head(6).sort_values("Match score"),
        x="Match score", y="Ingredient", orientation="h", color="Match score",
        color_continuous_scale=["#123D2A","#B9975B","#A54E2A"],
    )
    fig.update_layout(height=360, margin=dict(l=10,r=10,t=10,b=10), paper_bgcolor="rgba(0,0,0,0)", coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

with tab_followup:
    st.markdown('<div class="section-title">12-Week Validation Loop</div>', unsafe_allow_html=True)
    rows = []
    for mech, score in top3:
        for metric in FOLLOW_UP_METRICS.get(mech, []):
            rows.append({
                "Mechanism": MECHANISM_LABELS[mech],
                "Current score": score,
                "12-week metric": metric,
                "Purpose": "Validate whether the mechanism signal moves in the expected direction",
            })
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    st.markdown("### Timeline")
    st.dataframe(pd.DataFrame([
        {"Week":"0", "Node":"Baseline", "Action":"Full multimodal capture + mechanism vector"},
        {"Week":"4", "Node":"Adherence Check", "Action":"Lifestyle / product adherence + subjective feedback"},
        {"Week":"8", "Node":"Early Signal", "Action":"Face/skin feature recheck + symptom trend"},
        {"Week":"12", "Node":"Adjustment", "Action":"Repeat key metrics, update mechanism vector and intervention plan"},
    ]), use_container_width=True, hide_index=True)

with tab_chat:
    st.markdown('<div class="section-title">Agent Chat Demo</div>', unsafe_allow_html=True)
    st.caption("This is a local rule-based demo. It does not call an LLM.")
    question = st.text_input("Ask about this subject", placeholder="比如：为什么判断我是氧化压力？12周复测什么？")
    if question:
        st.markdown(agent_chat(question, scores, payload))

    st.markdown("### Export")
    md_report = generate_markdown_report(data, subject_id, scores, mae)
    json_report = {
        "subject_id": subject_id,
        "synthetic_demo_only": True,
        "mode": mode,
        "mechanism_scores": scores,
        "top_mechanisms": [{"mechanism": m, "label": MECHANISM_LABELS[m], "score": s} for m, s in top3],
        "confidence": {"label": conf_label, "score": conf_score},
        "note": "Not for clinical use.",
    }
    d1, d2 = st.columns(2)
    with d1:
        st.download_button("Download Markdown Report", data=md_report, file_name=f"{subject_id}_chronogene_report.md", mime="text/markdown")
    with d2:
        st.download_button("Download JSON", data=json.dumps(json_report, ensure_ascii=False, indent=2), file_name=f"{subject_id}_chronogene_report.json", mime="application/json")
