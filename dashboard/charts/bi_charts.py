from pathlib import Path
import matplotlib

matplotlib.use("Agg")  # headless backend for Flask

import matplotlib.pyplot as plt


# Match your theme.css palette
BG = "#07130B"        # --bg
PANEL = "#0B1E12"     # --panel
BORDER = "#1D4A35"    # subtle border/grid
TEXT = "#F5FFF8"      # strong text
MUTED = "#CDE8DA"     # muted
BAR = "#2F80ED"       # blue bars like your reference
ACCENT = "#35FF8A"    # green accent


def ensure_plot_dir(static_dir: Path) -> Path:
    plot_dir = static_dir / "plots"
    plot_dir.mkdir(parents=True, exist_ok=True)
    return plot_dir


def _apply_theme(ax):
    ax.set_facecolor(PANEL)
    ax.figure.set_facecolor(BG)

    ax.tick_params(colors=TEXT, labelsize=9)
    ax.xaxis.label.set_color(TEXT)
    ax.yaxis.label.set_color(TEXT)
    ax.title.set_color(TEXT)

    for spine in ax.spines.values():
        spine.set_color(BORDER)
        spine.set_linewidth(1)

    ax.grid(True, axis="x", color=BORDER, alpha=0.35)
    ax.set_axisbelow(True)


def chart_top_materials(rows, out_path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    materials = [r["recommended_material"] for r in rows]
    counts = [int(r["cnt"]) for r in rows]

    # Reverse for better top-down ranking
    materials = materials[::-1]
    counts = counts[::-1]

    fig, ax = plt.subplots(figsize=(14, 8), dpi=150)

    # Dark theme background
    fig.patch.set_facecolor("#061a10")
    ax.set_facecolor("#061a10")

    bars = ax.barh(materials, counts, color="#3b82f6")

    # Title + axis
    ax.set_title("Top Recommended Materials (Count)", color="white")
    ax.set_xlabel("Count", color="white")

    ax.tick_params(axis="x", colors="white")
    ax.tick_params(axis="y", colors="white")

    # Improve readability
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#35FF8A")
    ax.spines["bottom"].set_color("#35FF8A")

    # 🔥 CRITICAL FIX FOR CUT TEXT
    plt.subplots_adjust(left=0.35, right=0.95, top=0.90, bottom=0.15)

    plt.savefig(out_path, bbox_inches="tight", pad_inches=0.3)
    plt.close()


def chart_avg_cost_by_category(by_category, outpath: Path):
    cats = [x["product_category"] for x in by_category]
    vals = [float(x["avg_cost"] or 0) for x in by_category]

    fig, ax = plt.subplots(figsize=(8.5, 4.3))
    _apply_theme(ax)

    ax.bar(cats, vals, color=BAR, edgecolor=ACCENT, linewidth=1.1)
    ax.set_title("Average Predicted Cost (INR) by Category")
    ax.set_ylabel("Avg Cost (INR)")
    ax.tick_params(axis="x", rotation=18)

    plt.tight_layout()
    plt.savefig(outpath, dpi=180, facecolor=BG)
    plt.close(fig)

def chart_avg_co2_by_category(rows, out_path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    categories = [r["product_category"] for r in rows]
    values = [float(r["avg_co2"] or 0) for r in rows]

    # Match size of cost chart
    fig, ax = plt.subplots(figsize=(12, 5), dpi=150)

    # 🔥 Dark background like cost chart
    fig.patch.set_facecolor("#061a10")      # outer background
    ax.set_facecolor("#061a10")             # inner plot background

    # Bars
    ax.bar(categories, values, color="#3b82f6")

    # Titles and labels (WHITE)
    ax.set_title("Average Predicted CO₂ (kg) by Category", color="white")
    ax.set_ylabel("Avg CO₂ (kg)", color="white")

    # Axis styling
    ax.tick_params(axis="x", colors="white", rotation=20)
    ax.tick_params(axis="y", colors="white")

    # Remove top/right spines
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Make remaining spines greenish (like theme)
    ax.spines["left"].set_color("#35FF8A")
    ax.spines["bottom"].set_color("#35FF8A")

    plt.tight_layout()
    plt.savefig(out_path, bbox_inches="tight", pad_inches=0.2)
    plt.close()
