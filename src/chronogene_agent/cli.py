
from __future__ import annotations

import argparse
from pathlib import Path

from .data_loader import load_tables
from .model import train_baseline, load_model, predict_subject, get_target_scores
from .report import generate_markdown_report, save_report_files, top_mechanisms
from .mechanisms import MECHANISM_LABELS

def cmd_validate(args):
    data = load_tables(args.data_dir)
    print("Validation OK.")
    for key, df in data.tables.items():
        print(f"{key}: {df.shape[0]} rows x {df.shape[1]} cols")

def cmd_train(args):
    data = load_tables(args.data_dir)
    result = train_baseline(data.tables, args.model_path)
    print("Training complete.")
    print(result)

def cmd_report(args):
    data = load_tables(args.data_dir)
    if args.use_target:
        scores = get_target_scores(data.tables, args.subject_id)
        mae = None
    else:
        bundle = load_model(args.model_path)
        scores = predict_subject(data.tables, bundle, args.subject_id)
        mae = bundle.get("mae")
    md = generate_markdown_report(data, args.subject_id, scores, mae=mae)
    json_obj = {
        "subject_id": args.subject_id,
        "synthetic_demo_only": True,
        "mechanism_scores": scores,
        "top_mechanisms": [
            {"mechanism": m, "label": MECHANISM_LABELS[m], "score": s}
            for m, s in top_mechanisms(scores, 3)
        ],
    }
    save_report_files(md, args.out, json_obj, args.json_out)
    print(f"Report written to {args.out}")
    if args.json_out:
        print(f"JSON written to {args.json_out}")

def build_parser():
    p = argparse.ArgumentParser(prog="chronogene-agent")
    sub = p.add_subparsers(dest="command", required=True)

    q = sub.add_parser("validate")
    q.add_argument("--data-dir", default="data")
    q.set_defaults(func=cmd_validate)

    q = sub.add_parser("train")
    q.add_argument("--data-dir", default="data")
    q.add_argument("--model-path", default="models/baseline_model.joblib")
    q.set_defaults(func=cmd_train)

    q = sub.add_parser("report")
    q.add_argument("--data-dir", default="data")
    q.add_argument("--model-path", default="models/baseline_model.joblib")
    q.add_argument("--subject-id", default="CG0039")
    q.add_argument("--out", default="reports/CG0039_report.md")
    q.add_argument("--json-out", default="reports/CG0039_report.json")
    q.add_argument("--use-target", action="store_true")
    q.set_defaults(func=cmd_report)

    return p

def main():
    parser = build_parser()
    args = parser.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
