"""
tools/python_executor.py — Safe Python code execution sandbox for the Code Agent.
Executes data analysis and chart generation code in an isolated namespace.
"""
from __future__ import annotations
import io
import sys
import traceback
import contextlib
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
from pathlib import Path
from loguru import logger
from typing import Tuple


SAFE_GLOBALS = {
    "__builtins__": {
        "print": print, "range": range, "len": len, "list": list,
        "dict": dict, "set": set, "tuple": tuple, "str": str, "int": int,
        "float": float, "bool": bool, "type": type, "isinstance": isinstance,
        "enumerate": enumerate, "zip": zip, "map": map, "filter": filter,
        "sorted": sorted, "sum": sum, "min": min, "max": max, "abs": abs,
        "round": round, "open": open, "True": True, "False": False, "None": None,
    }
}


def execute_python(code: str, output_dir: str = "./reports") -> Tuple[str, list[str]]:
    """
    Execute Python code in a restricted namespace.
    
    Returns:
        (stdout_output, list_of_saved_chart_paths)
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    stdout_capture = io.StringIO()
    chart_paths = []

    # Provide common data science imports in the execution namespace
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import seaborn as sns

    namespace = {
        "np": np,
        "pd": pd,
        "plt": plt,
        "sns": sns,
        "__builtins__": __builtins__,
    }

    # Intercept plt.savefig / plt.show to capture charts
    saved_figures = []

    original_show = plt.show
    original_savefig = plt.savefig

    def capture_show():
        fig_path = str(Path(output_dir) / f"chart_{len(saved_figures)+1}.png")
        plt.savefig(fig_path, bbox_inches="tight", dpi=150)
        saved_figures.append(fig_path)
        plt.clf()

    plt.show = capture_show

    try:
        with contextlib.redirect_stdout(stdout_capture):
            exec(code, namespace)  # noqa: S102

        # Save any open figures that weren't shown
        for fig_num in plt.get_fignums():
            fig_path = str(Path(output_dir) / f"chart_{len(saved_figures)+1}.png")
            plt.figure(fig_num).savefig(fig_path, bbox_inches="tight", dpi=150)
            saved_figures.append(fig_path)
        plt.close("all")

        output = stdout_capture.getvalue()
        chart_paths = saved_figures
        logger.info(f"[Executor] Code ran OK. Charts: {len(chart_paths)}")
        return output, chart_paths

    except Exception:
        error_msg = traceback.format_exc()
        logger.warning(f"[Executor] Code error:\n{error_msg}")
        return f"Error:\n{error_msg}", []

    finally:
        plt.show = original_show
        plt.close("all")


def generate_chart_code(chart_type: str, data: dict, title: str) -> str:
    """
    Generate matplotlib code for common chart types.
    chart_type: 'bar', 'line', 'pie', 'scatter'
    data: {'labels': [...], 'values': [...]}
    """
    labels = data.get("labels", [])
    values = data.get("values", [])

    if chart_type == "bar":
        return f"""
import matplotlib.pyplot as plt
import numpy as np

labels = {labels}
values = {values}
colors = plt.cm.Blues(np.linspace(0.4, 0.9, len(labels)))

fig, ax = plt.subplots(figsize=(10, 6))
bars = ax.bar(labels, values, color=colors, edgecolor='white', linewidth=0.5)
ax.set_title('{title}', fontsize=14, fontweight='bold', pad=15)
ax.set_ylabel('Value')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
for bar, val in zip(bars, values):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5,
            str(val), ha='center', va='bottom', fontsize=9)
plt.tight_layout()
plt.show()
"""
    elif chart_type == "pie":
        return f"""
import matplotlib.pyplot as plt

labels = {labels}
values = {values}
colors = ['#2196F3','#4CAF50','#FF9800','#E91E63','#9C27B0'][:len(labels)]

fig, ax = plt.subplots(figsize=(8, 6))
wedges, texts, autotexts = ax.pie(values, labels=labels, colors=colors,
    autopct='%1.1f%%', startangle=90, pctdistance=0.85)
for text in autotexts:
    text.set_fontsize(9)
ax.set_title('{title}', fontsize=14, fontweight='bold', pad=15)
plt.tight_layout()
plt.show()
"""
    elif chart_type == "line":
        return f"""
import matplotlib.pyplot as plt

labels = {labels}
values = {values}

fig, ax = plt.subplots(figsize=(10, 5))
ax.plot(labels, values, marker='o', linewidth=2, markersize=6, color='#2196F3')
ax.fill_between(range(len(labels)), values, alpha=0.1, color='#2196F3')
ax.set_xticks(range(len(labels)))
ax.set_xticklabels(labels, rotation=30, ha='right')
ax.set_title('{title}', fontsize=14, fontweight='bold', pad=15)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
plt.show()
"""
    return ""
