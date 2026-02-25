#!/usr/bin/env python3
"""Generate a Gantt timeline chart from a kick-off YAML file.

Usage:
    python generate_gantt.py <kickoff.yaml> [output.png]

Output defaults to /tmp/<yaml_stem>_gantt_v<YYYYMMDD_HHMMSS>.png

Examples:
    python generate_gantt.py kickoff.yaml
    python generate_gantt.py kickoff.yaml gantt.png --dpi 300
    python generate_gantt.py kickoff.yaml --width 14 --height 6.5
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import FancyBboxPatch
import yaml


# ---------------------------------------------------------------------------
# Default phase colours (Google-palette inspired)
# ---------------------------------------------------------------------------
PHASE_COLORS = {
    1: "#4285F4",  # blue
    2: "#34A853",  # green
    3: "#FBBC04",  # yellow
    4: "#EA4335",  # red
    5: "#9334E6",  # purple
    6: "#00ACC1",  # teal
}


def load_yaml(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def parse_phases(data: dict) -> list[dict]:
    """Extract timeline phases and enrich with parsed dates."""
    phases = []
    for entry in data.get("timeline", []):
        start = entry.get("target_start", "")
        end = entry.get("target_end", "")
        if not start or not end:
            continue
        phases.append(
            {
                "phase": entry["phase"],
                "description": entry.get("description", f"Phase {entry['phase']}"),
                "start": start,
                "end": end,
                "start_dt": datetime.strptime(start, "%Y-%m-%d"),
                "end_dt": datetime.strptime(end, "%Y-%m-%d"),
                "gate_owner": entry.get("gate_owner", ""),
            }
        )
    return phases


def build_title(data: dict) -> str:
    project = data.get("metadata", {}).get("project_name", "")
    if project:
        return f"{project} — High-Level Timeline"
    return "High-Level Timeline"


def generate_gantt(
    data: dict,
    *,
    output: str = "gantt_timeline.png",
    dpi: int = 200,
    width: float = 14.0,
    height: float = 6.5,
) -> str:
    """Render a Gantt chart and save to *output*. Returns the output path."""
    phases = parse_phases(data)
    if not phases:
        print("Error: No valid timeline phases found in YAML.", file=sys.stderr)
        sys.exit(1)

    title = build_title(data)

    # Compute timeline range — pad by ~5 days on each side, snap to month start
    earliest = min(p["start_dt"] for p in phases)
    latest = max(p["end_dt"] for p in phases)
    timeline_start = earliest.replace(day=1)
    end_month = latest.month + 1 if latest.month < 12 else 1
    end_year = latest.year if latest.month < 12 else latest.year + 1
    timeline_end = latest.replace(year=end_year, month=end_month, day=1)

    # ---- Figure setup ----
    n = len(phases)
    fig, ax = plt.subplots(figsize=(width, height))
    fig.patch.set_facecolor("white")

    bar_height = 0.35
    y_positions = [n - 1 - i for i in range(n)]

    # Alternating row backgrounds
    for i, y in enumerate(y_positions):
        if i % 2 == 0:
            ax.axhspan(y - 0.45, y + 0.45, color="#F8F9FA", zorder=0)

    # ---- Draw phase bars ----
    for i, p in enumerate(phases):
        y = y_positions[i]
        start_num = mdates.date2num(p["start_dt"])
        end_num = mdates.date2num(p["end_dt"])
        duration = end_num - start_num
        color = PHASE_COLORS.get(p["phase"], "#90A4AE")

        bar = FancyBboxPatch(
            (start_num, y - bar_height / 2),
            duration,
            bar_height,
            boxstyle="round,pad=0.02",
            facecolor="#4285F4",
            edgecolor="black",
            linewidth=0.8,
            alpha=0.9,
            zorder=3,
        )
        ax.add_patch(bar)

        # Date label inside bar
        start_str = p["start_dt"].strftime("%b %d")
        end_str = p["end_dt"].strftime("%b %d")
        ax.text(
            start_num + 1.5,
            y,
            f"{start_str} – {end_str}",
            ha="left",
            va="center",
            fontsize=10,
            color="black",
            fontweight="bold",
            zorder=4,
        )

        # Gate diamond marker
        ax.plot(
            end_num,
            y + bar_height / 2 + 0.15,
            marker="D",
            color="black",
            markersize=7,
            markeredgecolor="black",
            markeredgewidth=0.8,
            zorder=5,
        )
        if p["gate_owner"]:
            ax.text(
                end_num,
                y + bar_height / 2 + 0.28,
                p["gate_owner"],
                ha="center",
                va="bottom",
                fontsize=10,
                color="black",
                fontstyle="italic",
                zorder=5,
            )

    # ---- Y-axis: phase labels ----
    ax.set_yticks(y_positions)
    ax.set_yticklabels(
        [f"Ph {p['phase']}: {p['description']}" for p in phases],
        fontsize=12,
        fontweight="medium",
        color="black",
    )

    # ---- X-axis: month grid ----
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.set_xlim(mdates.date2num(timeline_start), mdates.date2num(timeline_end))

    # Month gridlines
    cursor = timeline_start
    while cursor <= timeline_end:
        ax.axvline(
            mdates.date2num(cursor),
            color="#E0E0E0",
            linewidth=0.7,
            linestyle="--",
            zorder=1,
        )
        m = cursor.month + 1 if cursor.month < 12 else 1
        yr = cursor.year if cursor.month < 12 else cursor.year + 1
        cursor = cursor.replace(year=yr, month=m)

    # ---- Legend ----
    from matplotlib.lines import Line2D

    legend_handles = [
        Line2D([0], [0], color="#4285F4", linewidth=8, solid_capstyle="round",
               label="Phase"),
        Line2D([0], [0], marker="D", color="white", markerfacecolor="black",
               markeredgecolor="black", markersize=8, linewidth=0,
               label="Phase Gate"),
    ]

    ax.legend(
        handles=legend_handles,
        loc="upper right",
        fontsize=9,
        frameon=True,
        fancybox=True,
        framealpha=0.9,
        edgecolor="#CCCCCC",
        title="Legend",
        title_fontproperties={"weight": "bold", "size": 10},
    )

    # ---- Style ----
    ax.set_ylim(-0.6, n - 0.3)
    ax.tick_params(axis="x", labelsize=12, colors="black")
    ax.tick_params(axis="y", length=0, pad=10)
    for spine in ("top", "right", "left"):
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color("#CCCCCC")

    plt.tight_layout()
    plt.savefig(output, dpi=dpi, bbox_inches="tight", facecolor="white", edgecolor="none")
    plt.close(fig)
    return output


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(
        description="Generate a Gantt timeline chart from a kick-off YAML file."
    )
    parser.add_argument("yaml_file", help="Path to the kick-off YAML file")
    parser.add_argument(
        "output",
        nargs="?",
        default=None,
        help="Output PNG path (default: <yaml_stem>_gantt.png)",
    )
    parser.add_argument("--dpi", type=int, default=200, help="Image DPI (default: 200)")
    parser.add_argument("--width", type=float, default=14.0, help="Figure width in inches")
    parser.add_argument("--height", type=float, default=6.5, help="Figure height in inches")

    args = parser.parse_args()

    yaml_path = Path(args.yaml_file)
    if not yaml_path.exists():
        print(f"Error: File not found: {yaml_path}", file=sys.stderr)
        sys.exit(1)

    if args.output is None:
        version = datetime.now().strftime("%Y%m%d_%H%M%S")
        args.output = f"/tmp/{yaml_path.stem}_gantt_v{version}.png"

    data = load_yaml(str(yaml_path))
    out = generate_gantt(data, output=args.output, dpi=args.dpi, width=args.width, height=args.height)
    print(f"Gantt chart saved to: {out}")


if __name__ == "__main__":
    main()
