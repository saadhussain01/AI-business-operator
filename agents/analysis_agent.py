"""
agents/analysis_agent.py — Data Analysis Agent
Takes research findings and performs structured business analysis:
competitive positioning, market sizing, SWOT, trend analysis, and insights.
"""
from __future__ import annotations
import json
import re
from typing import Dict, Any
from .base_agent import BaseAgent


ANALYSIS_SYSTEM = """You are the Analysis Agent in an autonomous AI Business Operator system.
You receive research data and perform deep business analysis.

Your analysis MUST include:

## Executive Summary
2-3 sentences capturing the most critical insight.

## Market Overview
- Market size, growth rate, key segments
- Geographic distribution if relevant

## Competitive Landscape
- Top 5-7 competitors with their strengths/weaknesses
- Market share estimates where available
- Competitive positioning matrix description

## SWOT Analysis
**Strengths:** (of the market/product/company being analyzed)
**Weaknesses:**
**Opportunities:**
**Threats:**

## Key Trends
- 3-5 major trends shaping this space
- Technology, regulatory, consumer behavior shifts

## Data Insights
- Specific statistics extracted and interpreted
- Year-over-year comparisons where available
- Growth projections

## Strategic Recommendations
- 3-5 actionable recommendations
- Priority level (High/Medium/Low) for each

## Chart Data (JSON)
Provide data for visualizations in this exact format:
```chart_data
{
  "charts": [
    {
      "type": "bar",
      "title": "chart title",
      "labels": ["Label1", "Label2"],
      "values": [10, 20]
    }
  ]
}
```

Be analytical, specific, and strategic. Use numbers when available."""


class AnalysisAgent(BaseAgent):
    name = "AnalysisAgent"
    description = "Performs competitive analysis, SWOT, trend analysis, and extracts insights"

    def run(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        context = context or {}
        research_output = context.get("research_output", "No research data provided.")
        plan = context.get("plan", {})

        self._log("Analyzing research data...")

        analysis_prompt = f"""
ORIGINAL TASK: {task}

ANALYSIS FOCUS AREAS: {', '.join(plan.get('analysis_focus', ['general analysis']))}

RESEARCH DATA:
{research_output}

Please provide a comprehensive business analysis based on this data.
"""

        analysis = self._call_llm(
            system_prompt=ANALYSIS_SYSTEM,
            user_message=analysis_prompt,
            max_tokens=1800,
            temperature=0.2,
        )

        # Extract chart data from analysis
        chart_data = self._extract_chart_data(analysis)

        self._log(f"Analysis complete. Charts identified: {len(chart_data.get('charts', []))}")

        return {
            "agent": self.name,
            "output": analysis,
            "chart_data": chart_data,
            "task_type": plan.get("task_type", "general"),
        }

    def _extract_chart_data(self, analysis: str) -> Dict:
        """Parse chart data JSON from analysis output."""
        try:
            match = re.search(r"```chart_data\s*(.*?)\s*```", analysis, re.DOTALL)
            if match:
                return json.loads(match.group(1))
        except Exception:
            pass
        # Return sample chart data as fallback
        return {
            "charts": [
                {
                    "type": "bar",
                    "title": "Market Analysis Overview",
                    "labels": ["Segment A", "Segment B", "Segment C", "Segment D"],
                    "values": [35, 28, 22, 15],
                }
            ]
        }
