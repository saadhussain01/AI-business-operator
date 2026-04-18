from __future__ import annotations
import json, re
from typing import Dict, Any
from .base_agent import BaseAgent

PLANNER_SYSTEM = """You are the Planner Agent in an autonomous AI Business Operator.
Break down the user's business task into a structured execution plan.
Respond ONLY with valid JSON — no markdown fences, no extra text:
{
  "task_summary": "one sentence",
  "task_type": "market_research|competitor_analysis|content_creation|business_report|trend_analysis",
  "search_queries": ["query1","query2","query3"],
  "analysis_focus": ["focus1","focus2"],
  "output_format": "report|post|summary",
  "steps": [
    {"step":1,"agent":"research","action":"what to search"},
    {"step":2,"agent":"analysis","action":"what to analyse"},
    {"step":3,"agent":"code","action":"what charts to make"},
    {"step":4,"agent":"content","action":"what to write"}
  ],
  "chart_suggestions": [
    {"type":"bar|line|pie","title":"title","data_to_collect":"description"}
  ]
}"""

class PlannerAgent(BaseAgent):
    name = "PlannerAgent"
    description = "Decomposes tasks into structured plans"

    def run(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        self._log(f"Planning: '{task[:60]}'")
        response = self._call_llm(PLANNER_SYSTEM, f"Task: {task}", max_tokens=600, temperature=0.1)
        plan = self._parse(response)
        return {"agent": self.name, "output": response, "plan": plan, "task": task}

    def _parse(self, raw: str) -> Dict:
        try:
            clean = re.sub(r"```json|```", "", raw).strip()
            return json.loads(clean)
        except Exception:
            return {
                "task_summary": "Business task", "task_type": "market_research",
                "search_queries": [raw[:80]], "analysis_focus": ["overview"],
                "output_format": "report",
                "steps": [
                    {"step":1,"agent":"research","action":"search for data"},
                    {"step":2,"agent":"analysis","action":"analyse findings"},
                    {"step":3,"agent":"content","action":"write report"},
                ],
                "chart_suggestions": [],
            }
