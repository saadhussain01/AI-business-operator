from __future__ import annotations
import json, re
from typing import Dict, Any, List
from .base_agent import BaseAgent

CODE_SYSTEM = """You are the Code Agent. Write Python matplotlib code to generate charts.
Rules:
- matplotlib is imported as plt, numpy as np, seaborn as sns, pandas as pd
- Call plt.show() after each chart (it gets captured as PNG)
- Make charts professional: titles, axis labels, good colors
- Do NOT use plt.savefig() — use plt.show()
- Output ONLY valid Python code, no markdown, no explanation."""

class CodeAgent(BaseAgent):
    name = "CodeAgent"
    description = "Generates and executes Python chart code"

    def run(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        context    = context or {}
        chart_data = context.get("chart_data", {})
        analysis   = context.get("analysis_output", "")
        plan       = context.get("plan", {})
        output_dir = context.get("output_dir", "./reports")
        charts     = chart_data.get("charts", [])
        self._log(f"Generating code for {len(charts)} chart(s)…")

        if charts:
            code = self._code_from_data(charts)
        else:
            code = self._code_from_llm(task, analysis, plan.get("chart_suggestions", []))

        chart_paths = []
        if code.strip():
            try:
                from tools.python_executor import execute_python
                _, chart_paths = execute_python(code, output_dir=output_dir)
                self._log(f"Charts saved: {chart_paths}")
            except Exception as e:
                self._log(f"Execution error: {e}")

        return {
            "agent": self.name,
            "output": f"Generated {len(chart_paths)} chart(s)",
            "chart_paths": chart_paths,
        }

    def _code_from_data(self, charts: List[Dict]) -> str:
        try:
            from tools.python_executor import generate_chart_code
            parts = []
            for c in charts:
                parts.append(generate_chart_code(
                    chart_type=c.get("type", "bar"),
                    data={"labels": c.get("labels", []), "values": c.get("values", [])},
                    title=c.get("title", "Analysis Chart"),
                ))
            return "\n\n".join(parts)
        except Exception:
            return ""

    def _code_from_llm(self, task: str, analysis: str, suggestions: List) -> str:
        prompt = (
            f"Task: {task}\nChart suggestions: {json.dumps(suggestions)}\n"
            f"Analysis (extract numbers):\n{analysis[:1500]}\n\n"
            "Write Python matplotlib code for 2-3 professional charts."
        )
        code = self._call_llm(CODE_SYSTEM, prompt, max_tokens=900, temperature=0.1)
        return re.sub(r"```python|```", "", code).strip()
