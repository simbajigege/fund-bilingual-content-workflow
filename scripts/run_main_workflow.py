#!/usr/bin/env python3
"""
Main skill orchestrator: run analysis subskills and package LLM-ready context.
No hardcoded topic/research/writing generation in script.
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional


def run_command(cmd: List[str], cwd: Path) -> bool:
    print(f"[RUN] {' '.join(cmd)}")
    env = os.environ.copy()
    env["PYTHONUTF8"] = "1"
    env["PYTHONIOENCODING"] = "utf-8"
    result = subprocess.run(cmd, cwd=str(cwd), env=env, check=False)
    if result.returncode != 0:
        print(f"[WARN] command failed: {result.returncode}")
        return False
    return True


def newest_file(directory: Path, pattern: str) -> Optional[Path]:
    files = list(directory.glob(pattern))
    if not files:
        return None
    return sorted(files, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def load_json(path: Optional[Path]) -> Dict[str, Any]:
    if not path or not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def compact_context(heatmap: Dict[str, Any], historical: Dict[str, Any], dual_axis: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "heatmap": {
            "metadata": heatmap.get("metadata", {}),
            "signals": {
                "strong_buy_heavy": heatmap.get("heatmap_signals", {}).get("strong_buy_heavy", [])[:10],
                "strong_sell_heavy": heatmap.get("heatmap_signals", {}).get("strong_sell_heavy", [])[:10],
                "strong_buy_light": heatmap.get("heatmap_signals", {}).get("strong_buy_light", [])[:10],
            },
            "portfolio_score": heatmap.get("portfolio_score", {}),
        },
        "historical": {
            "metadata": historical.get("metadata", {}),
            "stability_analysis": historical.get("stability_analysis", {}),
            "trend_analysis": historical.get("trend_analysis", {}),
            "key_signals": historical.get("key_signals", [])[:20],
            "style_assessment": historical.get("style_assessment", {}),
        },
        "dual_axis": {
            "metadata": dual_axis.get("metadata", {}),
            "selected_stocks": dual_axis.get("key_stocks_selection", {}).get("selected_stocks", [])[:15],
            "profit_analysis": dual_axis.get("dual_axis_analysis", {}).get("profit_analysis", {}),
            "slope_analysis": dual_axis.get("dual_axis_analysis", {}).get("slope_analysis", {}),
            "operation_nodes": dual_axis.get("operation_nodes", {}),
        },
    }


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Run main workflow analysis and build LLM context package.")
    p.add_argument("--fund-code", required=True)
    p.add_argument("--quarters", type=int, default=12)
    p.add_argument("--top-n", type=int, default=8)
    p.add_argument("--output-dir", default="./content_output")
    p.add_argument("--skip-analysis", action="store_true")
    p.add_argument("--capture-screenshots", action="store_true")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    skill_root = Path(__file__).resolve().parents[1]
    workspace_root = skill_root.parent
    fund_root = Path(args.output_dir).resolve() / args.fund_code
    analysis_root = fund_root / "analysis"
    heatmap_dir = analysis_root / "heatmap"
    historical_dir = analysis_root / "historical"
    dual_reports_dir = analysis_root / "dual_axis" / "reports"
    dual_csv_dir = analysis_root / "dual_axis" / "csv_data"
    screenshot_dir = fund_root / "screenshots"
    for d in [heatmap_dir, historical_dir, dual_reports_dir, dual_csv_dir, screenshot_dir]:
        d.mkdir(parents=True, exist_ok=True)

    if not args.skip_analysis:
        run_command(
            [
                sys.executable,
                str(skill_root / "subskills" / "fund-heatmap-analysis" / "scripts" / "fetch_and_analyze.py"),
                "--fund-code",
                args.fund_code,
                "--output-dir",
                str(heatmap_dir),
            ],
            cwd=workspace_root,
        )
        run_command(
            [
                sys.executable,
                str(skill_root / "subskills" / "fund-historical-positions-analysis" / "scripts" / "quick_analysis.py"),
                "--fund-code",
                args.fund_code,
                "--output-dir",
                str(historical_dir),
                "--quarters",
                str(args.quarters),
            ],
            cwd=workspace_root,
        )
        run_command(
            [
                sys.executable,
                str(skill_root / "subskills" / "fund-dual-axis-analysis" / "scripts" / "fetch_and_analyze.py"),
                "--fund-code",
                args.fund_code,
                "--quarters",
                str(args.quarters),
                "--report-dir",
                str(dual_reports_dir),
                "--csv-dir",
                str(dual_csv_dir),
                "--top-n",
                str(args.top_n),
            ],
            cwd=workspace_root,
        )

    heatmap = load_json(newest_file(heatmap_dir, "*_analysis.json"))
    historical = load_json(newest_file(historical_dir, "*_analysis.json"))
    dual_axis = load_json(newest_file(dual_reports_dir, "*_report.json"))
    screenshot_manifest: Dict[str, Any] = {}

    if args.capture_screenshots:
        run_command(
            [
                sys.executable,
                str(skill_root / "subskills" / "fund-screenshot-capture" / "scripts" / "capture_guru_screenshots.py"),
                "--fund-code",
                args.fund_code,
                "--output-dir",
                str(screenshot_dir),
            ],
            cwd=workspace_root,
        )
        screenshot_manifest = load_json(screenshot_dir / "manifest.json")

    context = {
        "fund_code": args.fund_code,
        "paths": {
            "topic_planning_skill": str(skill_root / "subskills" / "fund-topic-planning" / "SKILL.md"),
            "research_deepening_skill": str(skill_root / "subskills" / "fund-research-deepening" / "SKILL.md"),
            "blog_writing_skill": str(skill_root / "subskills" / "fund-blog-writing" / "SKILL.md"),
            "bilingual_output_skill": str(skill_root / "subskills" / "fund-bilingual-output" / "SKILL.md"),
            "screenshot_capture_skill": str(skill_root / "subskills" / "fund-screenshot-capture" / "SKILL.md"),
        },
        "analysis_context": compact_context(heatmap, historical, dual_axis),
        "screenshot_context": screenshot_manifest,
        "next_actions": [
            "Use fund-topic-planning skill to generate topic matrix (LLM direct output).",
            "Use fund-research-deepening skill to build research packets (LLM direct output).",
            "Use fund-blog-writing skill to draft CN long-form post with screenshot placeholders (LLM direct output).",
            "Use fund-bilingual-output skill to produce ZH/EN final markdown outputs.",
            "Use screenshot_context to replace placeholders with real screenshot paths/captions.",
        ],
    }

    context_file = fund_root / "workflow_context.json"
    context_file.write_text(json.dumps(context, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] context package created: {context_file}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
