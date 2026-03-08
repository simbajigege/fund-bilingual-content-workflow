#!/usr/bin/env python3
"""
Capture AI2Alpha guru page screenshots by fund code.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, Optional

from playwright.sync_api import sync_playwright


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Capture guru page screenshots.")
    p.add_argument("--fund-code", required=True)
    p.add_argument("--output-dir", required=True)
    p.add_argument("--base-url", default="https://ai2alpha.cn/zh/guru")
    p.add_argument("--timeout-ms", type=int, default=45000)
    p.add_argument("--headless", action="store_true", default=True)
    return p.parse_args()


def clamp_clip(clip: Dict[str, float], page_w: float, page_h: float) -> Optional[Dict[str, float]]:
    x = max(0.0, clip.get("x", 0.0))
    y = max(0.0, clip.get("y", 0.0))
    w = max(1.0, clip.get("width", 1.0))
    h = max(1.0, clip.get("height", 1.0))

    if x >= page_w or y >= page_h:
        return None
    w = min(w, page_w - x)
    h = min(h, page_h - y)
    if w < 2 or h < 2:
        return None
    return {"x": x, "y": y, "width": w, "height": h}


def capture(fund_code: str, output_dir: Path, base_url: str, timeout_ms: int, headless: bool) -> Dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    url = f"{base_url.rstrip('/')}/{fund_code}/"

    result: Dict[str, Any] = {
        "fund_code": fund_code,
        "url": url,
        "files": {},
        "regions": {},
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        context = browser.new_context(viewport={"width": 1920, "height": 2400}, device_scale_factor=1)
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded", timeout=timeout_ms)
        page.wait_for_timeout(3000)

        full_path = output_dir / "full_page.png"
        page.screenshot(path=str(full_path), full_page=True)
        result["files"]["full_page"] = str(full_path)

        geom = page.evaluate(
            """() => {
                const viewW = window.innerWidth;
                const viewH = Math.max(document.body.scrollHeight, document.documentElement.scrollHeight);
                const rectOf = (el) => {
                  const r = el.getBoundingClientRect();
                  return { x: r.left + window.scrollX, y: r.top + window.scrollY, width: r.width, height: r.height };
                };
                const canvases = Array.from(document.querySelectorAll('canvas'))
                  .map(rectOf)
                  .filter(r => r.width > 220 && r.height > 120)
                  .sort((a, b) => a.y - b.y);
                const firstTable = document.querySelector('table');
                const tableRect = firstTable ? rectOf(firstTable) : null;
                const topChart = canvases.length ? canvases[0] : null;
                const bottomChart = canvases.length ? canvases[canvases.length - 1] : null;

                let topOverview = null;
                if (topChart) {
                  let el = document.elementFromPoint(topChart.x + 10, topChart.y + 10);
                  let depth = 0;
                  while (el && depth < 8) {
                    const r = el.getBoundingClientRect();
                    if (r.width > 1000 && r.height > 260) {
                      topOverview = { x: r.left + window.scrollX, y: r.top + window.scrollY, width: r.width, height: r.height };
                      break;
                    }
                    el = el.parentElement;
                    depth += 1;
                  }
                }

                let heatmap = null;
                if (topOverview) {
                  heatmap = {
                    x: topOverview.x,
                    y: topOverview.y,
                    width: topOverview.width * 0.52,
                    height: topOverview.height
                  };
                }
                return { viewW, viewH, topOverview, topChart, bottomChart, tableRect, heatmap };
            }"""
        )

        page_w = float(geom.get("viewW", 1920))
        page_h = float(geom.get("viewH", 3000))

        def shot(name: str, region: Optional[Dict[str, float]]) -> None:
            if not region:
                return
            clip = clamp_clip(region, page_w, page_h)
            if not clip:
                return
            path = output_dir / f"{name}.png"
            page.screenshot(path=str(path), clip=clip)
            result["files"][name] = str(path)
            result["regions"][name] = clip

        shot("top_overview", geom.get("topOverview"))
        shot("heatmap_region", geom.get("heatmap"))
        shot("stacked_chart_region", geom.get("topChart"))
        shot("dual_axis_region", geom.get("bottomChart"))
        shot("holdings_table_region", geom.get("tableRect"))

        context.close()
        browser.close()

    manifest = output_dir / "manifest.json"
    manifest.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    result["manifest"] = str(manifest)
    return result


def main() -> int:
    args = parse_args()
    out = Path(args.output_dir).resolve()
    result = capture(args.fund_code, out, args.base_url, args.timeout_ms, args.headless)
    print(f"[OK] screenshots captured: {result.get('manifest')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
