from __future__ import annotations
import io, contextlib, traceback
from pathlib import Path
from typing import Tuple
from loguru import logger
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

def execute_python(code: str, output_dir: str = "./reports") -> Tuple[str, list]:
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    import numpy as np, pandas as pd, seaborn as sns
    namespace = {"np": np, "pd": pd, "plt": plt, "sns": sns, "__builtins__": __builtins__}
    saved = []

    orig_show = plt.show
    def capture_show():
        p = str(Path(output_dir) / f"chart_{len(saved)+1}.png")
        plt.savefig(p, bbox_inches="tight", dpi=150); saved.append(p); plt.clf()
    plt.show = capture_show

    stdout_buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(stdout_buf):
            exec(code, namespace)  # noqa: S102
        for n in plt.get_fignums():
            p = str(Path(output_dir) / f"chart_{len(saved)+1}.png")
            plt.figure(n).savefig(p, bbox_inches="tight", dpi=150); saved.append(p)
        plt.close("all")
        return stdout_buf.getvalue(), saved
    except Exception:
        plt.close("all")
        return traceback.format_exc(), []
    finally:
        plt.show = orig_show

def generate_chart_code(chart_type: str, data: dict, title: str) -> str:
    labels, values = data.get("labels", []), data.get("values", [])
    if chart_type == "bar":
        return f"""
import matplotlib.pyplot as plt, numpy as np
labels={labels}; values={values}
colors=plt.cm.Blues(np.linspace(0.4,0.9,len(labels)))
fig,ax=plt.subplots(figsize=(10,6))
bars=ax.bar(labels,values,color=colors,edgecolor='white',linewidth=0.5)
ax.set_title('{title}',fontsize=14,fontweight='bold',pad=15)
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
[ax.text(b.get_x()+b.get_width()/2,b.get_height()+0.5,str(v),ha='center',va='bottom',fontsize=9) for b,v in zip(bars,values)]
plt.tight_layout(); plt.show()"""
    elif chart_type == "pie":
        return f"""
import matplotlib.pyplot as plt
labels={labels}; values={values}
colors=['#6c63ff','#4ade80','#f59e0b','#f43f5e','#38bdf8'][:len(labels)]
fig,ax=plt.subplots(figsize=(8,6))
ax.pie(values,labels=labels,colors=colors,autopct='%1.1f%%',startangle=90,pctdistance=0.85)
ax.set_title('{title}',fontsize=14,fontweight='bold'); plt.tight_layout(); plt.show()"""
    else:  # line
        return f"""
import matplotlib.pyplot as plt
labels={labels}; values={values}
fig,ax=plt.subplots(figsize=(10,5))
ax.plot(range(len(labels)),values,marker='o',linewidth=2,markersize=6,color='#6c63ff')
ax.fill_between(range(len(labels)),values,alpha=0.1,color='#6c63ff')
ax.set_xticks(range(len(labels))); ax.set_xticklabels(labels,rotation=30,ha='right')
ax.set_title('{title}',fontsize=14,fontweight='bold')
ax.spines['top'].set_visible(False); ax.spines['right'].set_visible(False)
plt.tight_layout(); plt.show()"""
