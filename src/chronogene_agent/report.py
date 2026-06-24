
from __future__ import annotations

from pathlib import Path
from typing import Any
import json
import numpy as np
import pandas as pd

from .data_loader import MultiModalData, get_subject_payload
from .mechanisms import MECHANISM_COLUMNS, MECHANISM_LABELS, EVIDENCE_RULES, FOLLOW_UP_METRICS

def top_mechanisms(scores: dict[str, float], k: int = 3):
    return sorted(scores.items(), key=lambda x: x[1], reverse=True)[:k]

def confidence_label(completeness: float, mae: float | None = None):
    base = 58 + 40 * float(completeness)
    if mae is not None:
        base -= min(12, max(0, (mae - 4) * 0.7))
    base = float(np.clip(base, 35, 96))
    if base >= 82:
        return "High", base
    if base >= 67:
        return "Medium", base
    return "Low", base

def get_value(payload: dict[str, Any], table: str, field: str):
    if table == "skin_scrna":
        rows = payload.get("skin_scrna", [])
        if not rows:
            return None
        df = pd.DataFrame(rows)
        if field not in df.columns:
            return None
        return float(df[field].mean())
    if table not in payload:
        return None
    return payload[table].get(field)

def interpret_value(field: str, value: Any) -> str:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return "missing"
    if isinstance(value, str):
        return value
    low_is_risk = {
        "sunscreen_adherence_0_100",
        "sleep_hours",
        "exercise_minutes_per_week",
        "skincare_consistency_0_100",
        "OXPHOS_mitochondrial_score",
        "collagen_synthesis_score",
        "lipid_barrier_ceramide_score",
        "autophagy_lysosome_score",
        "epithelial_barrier_tight_junction_score",
        "alpha_diversity_shannon",
    }
    try:
        v = float(value)
    except Exception:
        return str(value)
    if field in low_is_risk:
        if v < 35:
            return "low / risk signal"
        if v > 70:
            return "favorable"
        return "mid-range"
    if v >= 70:
        return "high / active signal"
    if v >= 45:
        return "mid-range"
    return "low"

def evidence_dataframe(payload: dict[str, Any], mechanism: str) -> pd.DataFrame:
    rows = []
    for table, field, desc in EVIDENCE_RULES.get(mechanism, []):
        value = get_value(payload, table, field)
        rows.append({
            "Modality": table,
            "Evidence": desc,
            "Feature": field,
            "Value": round(value, 2) if isinstance(value, float) else value,
            "Interpretation": interpret_value(field, value),
        })
    return pd.DataFrame(rows)

def ingredient_matches(tables: dict[str, pd.DataFrame], scores: dict[str, float]) -> pd.DataFrame:
    ingredients = tables["ingredients"].copy()
    rows = []
    normalized = {m: scores[m] / 100.0 for m in MECHANISM_COLUMNS}
    for _, r in ingredients.iterrows():
        match_score = 0.0
        impact_details = []
        for m in MECHANISM_COLUMNS:
            delta_col = f"delta_{m}"
            if delta_col in ingredients.columns:
                delta = float(r[delta_col])
                contribution = max(0.0, -delta) * normalized[m]
                match_score += contribution
                if contribution > 0.035:
                    impact_details.append(f"{MECHANISM_LABELS[m]} ({contribution:.2f})")
        rows.append({
            "Ingredient": r.get("ingredient_id"),
            "Primary axis": r.get("primary_axis"),
            "Match score": round(match_score * 100, 1),
            "Evidence level": r.get("evidence_level"),
            "Safety confidence": r.get("safety_confidence"),
            "Main matched mechanisms": "; ".join(impact_details[:3]),
        })
    return pd.DataFrame(rows).sort_values("Match score", ascending=False)

def generate_markdown_report(data: MultiModalData, subject_id: str, scores: dict[str, float], mae: float | None = None) -> str:
    payload = get_subject_payload(data, subject_id)
    participant = payload["participants"]
    conf_label, conf_score = confidence_label(participant.get("data_completeness", 0.7), mae)
    top = top_mechanisms(scores, 3)

    lines = [
        f"# ChronoGene Agent Report｜{subject_id}",
        "",
        "> Synthetic demo only. Not for clinical use.",
        "",
        "## 基本信息",
        f"- 年龄：{participant.get('age')}",
        f"- 性别：{participant.get('sex')}",
        f"- BMI：{participant.get('BMI')}",
        f"- 数据完整度：{participant.get('data_completeness')}",
        f"- 整体置信度：{conf_label} ({conf_score:.1f}/100)",
        "",
        "## 主导衰老机制",
    ]
    for i, (m, s) in enumerate(top, 1):
        lines.append(f"{i}. **{MECHANISM_LABELS[m]}**：{s:.1f}/100")
    lines.append("")
    lines.append("## 多模态证据链")
    for m, s in top:
        lines.append(f"### {MECHANISM_LABELS[m]}｜{s:.1f}/100")
        ev = evidence_dataframe(payload, m)
        for _, r in ev.iterrows():
            lines.append(f"- {r['Evidence']}：`{r['Feature']}` = {r['Value']} ({r['Interpretation']})")
        lines.append("")
        lines.append("12 周复测：" + "、".join(FOLLOW_UP_METRICS.get(m, [])))
        lines.append("")
    lines.append("## 边界")
    lines.append("- 这是 synthetic demo，不是医学诊断。")
    lines.append("- 真实产品必须区分真实检测、模型推断、缺失补全与低置信假设。")
    return "\n".join(lines)

def save_report_files(markdown: str, out_md: str | Path, json_obj: dict | None = None, out_json: str | Path | None = None):
    out_md = Path(out_md)
    out_md.parent.mkdir(parents=True, exist_ok=True)
    out_md.write_text(markdown, encoding="utf-8")
    if out_json and json_obj is not None:
        out_json = Path(out_json)
        out_json.parent.mkdir(parents=True, exist_ok=True)
        out_json.write_text(json.dumps(json_obj, ensure_ascii=False, indent=2), encoding="utf-8")
