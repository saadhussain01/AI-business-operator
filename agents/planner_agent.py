"""
agents/planner_agent.py — Planner Agent
Decomposes high-level business tasks into structured execution plans
that the other agents follow step by step.
"""
from __future__ import annotations
import json
import re
from typing import Dict, Any, List
from .base_agent import BaseAgent


PLANNER_SYSTEM = """You are the Planner Agent in an autonomous AI Business Operator system.
Your job is to break down a user's business task into a clear, ordered execution plan.

You MUST respond with valid JSON in this exact format:
{
  "task_summary": "One-sentence description of the task",
  "task_type": "market_research | competitor_analysis | content_creation | business_report | trend_analysis",
  "search_queries": ["query1", "query2", "query3"],
  "analysis_focus": ["focus_area_1", "focus_area_2"],
  "output_format": "report | post | dashboard | summary",
  "steps": [
    {"step": 1, "agent": "research", "action": "What to research"},
    {"step": 2, "agent": "analysis", "action": "What to analyze"},
    {"step": 3, "agent": "code", "action": "What charts to generate"},
    {"step": 4, "agent": "content", "action": "What to write"}
  ],
  "chart_suggestions": [
    {"type": "bar|line|pie", "title": "Chart title", "data_to_collect": "description"}
  ]
}

Be specific and actionable. Generate 3-5 targeted search queries.
Respond ONLY with the JSON object, no other text."""


class PlannerAgent(BaseAgent):
    name = "PlannerAgent"
    description = "Breaks business tasks into structured execution plans"

    def run(self, task: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        self._log(f"Planning task: '{task[:60]}...'")

        response = self._call_llm(
            system_prompt=PLANNER_SYSTEM,
            user_message=f"Task: {task}",
            max_tokens=800,
            temperature=0.2,
        )

        plan = self._parse_plan(response)
        self._log(f"Plan created: {plan.get('task_type')} with {len(plan.get('steps', []))} steps")

        return {
            "agent": self.name,
            "output": response,
            "plan": plan,
            "task": task,
        }

    def _parse_plan(self, response: str) -> Dict[str, Any]:
        """Parse the LLM's JSON response into a plan dict."""
        try:
            # Strip markdown code fences if present
            clean = re.sub(r"```json|```", "", response).strip()
            return json.loads(clean)
        except Exception:
            # Fallback: build a generic plan
            return {
                "task_summary": "Business research and analysis task",
                "task_type": "market_research",
                "search_queries": [response[:100]],
                "analysis_focus": ["market overview", "key players"],
                "output_format": "report",
                "steps": [
                    {"step": 1, "agent": "research", "action": "Search for relevant data"},
                    {"step": 2, "agent": "analysis", "action": "Analyze findings"},
                    {"step": 3, "agent": "content", "action": "Generate report"},
                ],
                "chart_suggestions": [],
            }
