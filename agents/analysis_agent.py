from __future__ import annotations
import json, re
from typing import Dict, Any
from .base_agent import BaseAgent

ANALYSIS_SYSTEM = """You are the Analysis Agent in an autonomous AI Business Operator.
Perform deep business analysis from research data.

Include:
## Executive Summary
## Market Overview
## Competitive Landscape
## SWOT Analysis
## Key Trends
## Data Insights
## Strategic Recommendations

Then append chart data in this EXACT block (required):
```chart_data
{"charts":[{"type":"bar","title":"title","labels":["A","B","C"],"values":[40,30,20]}]}
```
Use real numbers from research if available, else reasonable estimates."""

class AnalysisAgent(BaseAgent):
    name = "AnalysisAgent"
    description = "SWOT, competitive analysis, trends, insights"

    def run(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        context = context or {}
        research = context.get("research_output", "")
        plan     = context.get("plan", {})
        self._log("Analysing research data…")

        prompt = (
            f"TASK: {task}\n"
            f"FOCUS: {', '.join(plan.get('analysis_focus', ['general']))}\n\n"
            f"RESEARCH DATA:\n{research[:3000]}"
        )
        analysis = self._call_llm(ANALYSIS_SYSTEM, prompt, max_tokens=1800, temperature=0.2)
        chart_data = self._extract_charts(analysis)
        return {"agent": self.name, "output": analysis, "chart_data": chart_data}

    def _extract_charts(self, text: str) -> Dict:
        try:
            m = re.search(r"```chart_data\s*(.*?)\s*```", text, re.DOTALL)
            if m:
                return json.loads(m.group(1))
        except Exception:
            pass
        return {"charts": [{"type": "bar", "title": "Market Overview",
                             "labels": ["Segment A", "Segment B", "Segment C", "Segment D"],
                             "values": [35, 28, 22, 15]}]}
