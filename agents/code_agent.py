"""
agents/code_agent.py — Code Execution Agent
Generates Python code to create charts and visualizations from
structured data provided by the Analysis Agent, then executes it safely.
"""
from __future__ import annotations
import json
import re
from typing import Dict, Any, List
from .base_agent import BaseAgent
from tools.python_executor import execute_python, generate_chart_code


CODE_SYSTEM = """You are the Code Agent in an autonomous AI Business Operator system.
You write Python code to generate professional data visualizations using matplotlib and seaborn.

Rules:
- Use matplotlib and seaborn (already imported as plt, sns)
- numpy is available as np, pandas as pd
- Call plt.show() after each chart (it will be captured as an image file)
- Create professional, labeled charts with:
  * Clear titles and axis labels
  * Color schemes (use Blues, viridis, or custom professional colors)
  * Proper formatting and tight_layout()
- Generate multiple charts if data warrants it
- Write clean, executable Python code ONLY
- Do NOT use plt.savefig() — use plt.show() to capture

Respond with ONLY valid Python code. No markdown, no explanations."""


class CodeAgent(BaseAgent):
    name = "CodeAgent"
    description = "Generates and executes Python code for data visualization and analysis"

    def run(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        context = context or {}
        chart_data = context.get("chart_data", {})
        analysis_output = context.get("analysis_output", "")
        plan = context.get("plan", {})
        output_dir = context.get("output_dir", "./reports")

        charts = chart_data.get("charts", [])
        chart_suggestions = plan.get("chart_suggestions", [])

        self._log(f"Generating code for {len(charts)} charts...")

        chart_paths = []

        # Generate code from chart data extracted by Analysis Agent
        if charts:
            code_parts = []
            for chart in charts:
                code = generate_chart_code(
                    chart_type=chart.get("type", "bar"),
                    data={"labels": chart.get("labels", []), "values": chart.get("values", [])},
                    title=chart.get("title", "Analysis Chart"),
                )
                code_parts.append(code)

            full_code = "\n\n".join(code_parts)
        else:
            # Ask LLM to generate chart code from analysis text
            self._log("No structured chart data — generating code from analysis text")
            full_code = self._generate_code_from_analysis(task, analysis_output, chart_suggestions)

        # Execute the generated code
        if full_code.strip():
            self._log("Executing chart generation code...")
            stdout, paths = execute_python(full_code, output_dir=output_dir)
            chart_paths = paths
            self._log(f"Charts generated: {len(chart_paths)}")
            if stdout:
                self._log(f"Output: {stdout[:200]}")
        else:
            stdout = ""

        return {
            "agent": self.name,
            "output": f"Generated {len(chart_paths)} chart(s): {', '.join(chart_paths)}",
            "chart_paths": chart_paths,
            "code_executed": full_code[:500] + "..." if len(full_code) > 500 else full_code,
            "execution_output": stdout,
        }

    def _generate_code_from_analysis(
        self, task: str, analysis: str, suggestions: List[Dict]
    ) -> str:
        """Ask the LLM to write chart code based on analysis findings."""
        suggestions_str = json.dumps(suggestions, indent=2) if suggestions else "auto-determine appropriate charts"

        prompt = f"""
Task: {task}

Chart suggestions from planner:
{suggestions_str}

Analysis data (extract numbers for charts):
{analysis[:2000]}

Write Python matplotlib code to create 2-3 professional charts based on any 
numerical data found in the analysis. If specific numbers aren't available,
create illustrative comparative charts with reasonable estimated values.
Make charts visually professional with proper titles, labels, and colors.
"""
        code = self._call_llm(
            system_prompt=CODE_SYSTEM,
            user_message=prompt,
            max_tokens=1000,
            temperature=0.1,
        )
        # Strip markdown code fences
        code = re.sub(r"```python|```", "", code).strip()
        return code
