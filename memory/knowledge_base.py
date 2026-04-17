"""
memory/knowledge_base.py — LangGraph-based Multi-Agent Orchestrator

This is the central "AI Operating System" that:
1. Receives a task from the user
2. Routes it through the agent pipeline using LangGraph state machine
3. Passes context between agents
4. Returns a complete result with report, charts, and analysis

Graph flow:
  START → memory_retrieve → planner → research → analysis → code → content → memory_store → END
"""
from __future__ import annotations
import os
import time
from datetime import datetime
from pathlib import Path
from typing import TypedDict, Annotated, Optional, List, Dict, Any
from loguru import logger

try:
    from langgraph.graph import StateGraph, START, END
    LANGGRAPH_AVAILABLE = True
except ImportError:
    LANGGRAPH_AVAILABLE = False
    logger.warning("LangGraph not installed — using sequential fallback pipeline")

from agents import (
    PlannerAgent,
    ResearchAgent,
    AnalysisAgent,
    CodeAgent,
    ContentAgent,
    MemoryAgent,
)


# ─── State Schema ──────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    task: str
    output_dir: str
    plan: Dict[str, Any]
    memory_context: str
    research_output: str
    analysis_output: str
    chart_paths: List[str]
    chart_data: Dict[str, Any]
    final_report: str
    report_path: str
    pdf_path: str
    sources_count: int
    word_count: int
    errors: List[str]
    agent_log: List[Dict[str, Any]]
    start_time: float


# ─── Agent Node Functions ──────────────────────────────────────────────────────

def _log_step(state: AgentState, agent_name: str, output: str) -> List[Dict]:
    log = list(state.get("agent_log", []))
    log.append({
        "agent": agent_name,
        "timestamp": datetime.now().isoformat(),
        "output_preview": output[:200],
    })
    return log


def node_memory_retrieve(state: AgentState) -> AgentState:
    logger.info("[Orchestrator] Step 1: Memory retrieval")
    agent = MemoryAgent()
    result = agent.run(state["task"], {"action": "retrieve"})
    return {
        **state,
        "memory_context": result.get("output", ""),
        "agent_log": _log_step(state, "MemoryAgent", result.get("output", "")),
    }


def node_planner(state: AgentState) -> AgentState:
    logger.info("[Orchestrator] Step 2: Planning")
    agent = PlannerAgent()

    # Enrich task with memory context if available
    enriched_task = state["task"]
    if state.get("memory_context"):
        enriched_task += f"\n\n[Relevant past research available in memory]"

    result = agent.run(enriched_task)
    return {
        **state,
        "plan": result.get("plan", {}),
        "agent_log": _log_step(state, "PlannerAgent", result.get("output", "")),
    }


def node_research(state: AgentState) -> AgentState:
    logger.info("[Orchestrator] Step 3: Research")
    agent = ResearchAgent()
    result = agent.run(state["task"], {"plan": state.get("plan", {})})

    # Combine with memory context
    research = result.get("output", "")
    if state.get("memory_context"):
        research = f"[Memory Context]\n{state['memory_context']}\n\n[Fresh Research]\n{research}"

    return {
        **state,
        "research_output": research,
        "sources_count": result.get("sources_count", 0),
        "agent_log": _log_step(state, "ResearchAgent", research),
    }


def node_analysis(state: AgentState) -> AgentState:
    logger.info("[Orchestrator] Step 4: Analysis")
    agent = AnalysisAgent()
    result = agent.run(state["task"], {
        "research_output": state.get("research_output", ""),
        "plan": state.get("plan", {}),
    })
    return {
        **state,
        "analysis_output": result.get("output", ""),
        "chart_data": result.get("chart_data", {}),
        "agent_log": _log_step(state, "AnalysisAgent", result.get("output", "")),
    }


def node_code(state: AgentState) -> AgentState:
    logger.info("[Orchestrator] Step 5: Code / Chart generation")
    agent = CodeAgent()
    result = agent.run(state["task"], {
        "chart_data": state.get("chart_data", {}),
        "analysis_output": state.get("analysis_output", ""),
        "plan": state.get("plan", {}),
        "output_dir": state.get("output_dir", "./reports"),
    })
    return {
        **state,
        "chart_paths": result.get("chart_paths", []),
        "agent_log": _log_step(state, "CodeAgent", result.get("output", "")),
    }


def node_content(state: AgentState) -> AgentState:
    logger.info("[Orchestrator] Step 6: Content / Report generation")
    agent = ContentAgent()
    result = agent.run(state["task"], {
        "plan": state.get("plan", {}),
        "research_output": state.get("research_output", ""),
        "analysis_output": state.get("analysis_output", ""),
        "chart_paths": state.get("chart_paths", []),
        "output_dir": state.get("output_dir", "./reports"),
    })
    return {
        **state,
        "final_report": result.get("output", ""),
        "report_path": result.get("report_path", ""),
        "pdf_path": result.get("pdf_path", ""),
        "word_count": result.get("word_count", 0),
        "agent_log": _log_step(state, "ContentAgent", result.get("output", "")),
    }


def node_memory_store(state: AgentState) -> AgentState:
    logger.info("[Orchestrator] Step 7: Storing to memory")
    agent = MemoryAgent()
    agent.run(state["task"], {
        "action": "store",
        "research_output": state.get("research_output", ""),
        "analysis_output": state.get("analysis_output", ""),
        "final_report": state.get("final_report", ""),
        "task_type": state.get("plan", {}).get("task_type", "unknown"),
    })
    return {
        **state,
        "agent_log": _log_step(state, "MemoryAgent[store]", "Knowledge stored"),
    }


# ─── Graph Builder ─────────────────────────────────────────────────────────────

def build_graph():
    """Build and compile the LangGraph agent pipeline."""
    graph = StateGraph(AgentState)

    graph.add_node("memory_retrieve", node_memory_retrieve)
    graph.add_node("planner", node_planner)
    graph.add_node("research", node_research)
    graph.add_node("analysis", node_analysis)
    graph.add_node("code", node_code)
    graph.add_node("content", node_content)
    graph.add_node("memory_store", node_memory_store)

    graph.add_edge(START, "memory_retrieve")
    graph.add_edge("memory_retrieve", "planner")
    graph.add_edge("planner", "research")
    graph.add_edge("research", "analysis")
    graph.add_edge("analysis", "code")
    graph.add_edge("code", "content")
    graph.add_edge("content", "memory_store")
    graph.add_edge("memory_store", END)

    return graph.compile()


# ─── Sequential Fallback (no LangGraph) ───────────────────────────────────────

def run_sequential(task: str, output_dir: str = "./reports") -> AgentState:
    """Fallback: run agents sequentially without LangGraph."""
    state: AgentState = {
        "task": task,
        "output_dir": output_dir,
        "plan": {},
        "memory_context": "",
        "research_output": "",
        "analysis_output": "",
        "chart_paths": [],
        "chart_data": {},
        "final_report": "",
        "report_path": "",
        "pdf_path": "",
        "sources_count": 0,
        "word_count": 0,
        "errors": [],
        "agent_log": [],
        "start_time": time.time(),
    }
    for node_fn in [
        node_memory_retrieve,
        node_planner,
        node_research,
        node_analysis,
        node_code,
        node_content,
        node_memory_store,
    ]:
        try:
            state = node_fn(state)
        except Exception as e:
            logger.error(f"[Sequential] Node {node_fn.__name__} failed: {e}")
            state["errors"].append(f"{node_fn.__name__}: {str(e)}")
    return state


# ─── Main Orchestrator API ─────────────────────────────────────────────────────

class BusinessOperator:
    """
    The main interface to the AI Business Operator system.
    Automatically uses LangGraph if available, otherwise falls back to sequential.
    """

    def __init__(self, output_dir: str = "./reports"):
        self.output_dir = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        if LANGGRAPH_AVAILABLE:
            self.graph = build_graph()
            logger.info("[BusinessOperator] LangGraph pipeline ready")
        else:
            self.graph = None
            logger.info("[BusinessOperator] Sequential pipeline ready (install langgraph for graph mode)")

    def run(self, task: str) -> Dict[str, Any]:
        """
        Execute the full multi-agent pipeline for a business task.
        
        Args:
            task: Natural language description of the business task
            
        Returns:
            Dict with keys: final_report, analysis_output, research_output,
                           chart_paths, report_path, pdf_path, elapsed_time,
                           agent_log, plan, sources_count
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"[BusinessOperator] Task: {task}")
        logger.info(f"{'='*60}")

        start = time.time()
        initial_state: AgentState = {
            "task": task,
            "output_dir": self.output_dir,
            "plan": {},
            "memory_context": "",
            "research_output": "",
            "analysis_output": "",
            "chart_paths": [],
            "chart_data": {},
            "final_report": "",
            "report_path": "",
            "pdf_path": "",
            "sources_count": 0,
            "word_count": 0,
            "errors": [],
            "agent_log": [],
            "start_time": start,
        }

        if self.graph:
            final_state = self.graph.invoke(initial_state)
        else:
            final_state = run_sequential(task, self.output_dir)

        elapsed = round(time.time() - start, 2)
        logger.info(f"[BusinessOperator] Completed in {elapsed}s")

        return {
            "task": task,
            "elapsed_time": elapsed,
            "final_report": final_state.get("final_report", ""),
            "research_output": final_state.get("research_output", ""),
            "analysis_output": final_state.get("analysis_output", ""),
            "chart_paths": final_state.get("chart_paths", []),
            "report_path": final_state.get("report_path", ""),
            "pdf_path": final_state.get("pdf_path", ""),
            "plan": final_state.get("plan", {}),
            "sources_count": final_state.get("sources_count", 0),
            "word_count": final_state.get("word_count", 0),
            "agent_log": final_state.get("agent_log", []),
            "errors": final_state.get("errors", []),
        }
