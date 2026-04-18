from __future__ import annotations
import time
from datetime import datetime
from pathlib import Path
from typing import TypedDict, List, Dict, Any
from loguru import logger

try:
    from langgraph.graph import StateGraph, START, END
    LANGGRAPH_OK = True
except ImportError:
    LANGGRAPH_OK = False

from agents import PlannerAgent, ResearchAgent, AnalysisAgent, CodeAgent, ContentAgent, MemoryAgent

class AgentState(TypedDict):
    task: str; output_dir: str; plan: Dict; memory_context: str
    research_output: str; analysis_output: str; chart_paths: List[str]
    chart_data: Dict; final_report: str; report_path: str; pdf_path: str
    sources_count: int; word_count: int; errors: List[str]
    agent_log: List[Dict]; start_time: float

def _log(state: AgentState, agent: str, out: str) -> List[Dict]:
    return [*state.get("agent_log", []),
            {"agent": agent, "timestamp": datetime.now().isoformat(), "output_preview": out[:200]}]

def node_memory_retrieve(s: AgentState) -> AgentState:
    r = MemoryAgent().run(s["task"], {"action": "retrieve"})
    return {**s, "memory_context": r.get("output",""), "agent_log": _log(s,"MemoryAgent",r.get("output",""))}

def node_planner(s: AgentState) -> AgentState:
    r = PlannerAgent().run(s["task"])
    return {**s, "plan": r.get("plan",{}), "agent_log": _log(s,"PlannerAgent",r.get("output",""))}

def node_research(s: AgentState) -> AgentState:
    r = ResearchAgent().run(s["task"], {"plan": s.get("plan",{})})
    research = r.get("output","")
    if s.get("memory_context"):
        research = f"[Memory Context]\n{s['memory_context']}\n\n[Fresh Research]\n{research}"
    return {**s, "research_output": research, "sources_count": r.get("sources_count",0),
            "agent_log": _log(s,"ResearchAgent",research)}

def node_analysis(s: AgentState) -> AgentState:
    r = AnalysisAgent().run(s["task"], {"research_output": s.get("research_output",""), "plan": s.get("plan",{})})
    return {**s, "analysis_output": r.get("output",""), "chart_data": r.get("chart_data",{}),
            "agent_log": _log(s,"AnalysisAgent",r.get("output",""))}

def node_code(s: AgentState) -> AgentState:
    r = CodeAgent().run(s["task"], {"chart_data": s.get("chart_data",{}),
        "analysis_output": s.get("analysis_output",""), "plan": s.get("plan",{}), "output_dir": s.get("output_dir","./reports")})
    return {**s, "chart_paths": r.get("chart_paths",[]), "agent_log": _log(s,"CodeAgent",r.get("output",""))}

def node_content(s: AgentState) -> AgentState:
    r = ContentAgent().run(s["task"], {"plan": s.get("plan",{}), "research_output": s.get("research_output",""),
        "analysis_output": s.get("analysis_output",""), "chart_paths": s.get("chart_paths",[]),
        "output_dir": s.get("output_dir","./reports")})
    return {**s, "final_report": r.get("output",""), "report_path": r.get("report_path",""),
            "pdf_path": r.get("pdf_path",""), "word_count": r.get("word_count",0),
            "agent_log": _log(s,"ContentAgent",r.get("output",""))}

def node_memory_store(s: AgentState) -> AgentState:
    MemoryAgent().run(s["task"], {"action":"store", "research_output": s.get("research_output",""),
        "analysis_output": s.get("analysis_output",""), "final_report": s.get("final_report","")})
    return {**s, "agent_log": _log(s,"MemoryAgent[store]","Knowledge stored")}

def build_graph():
    g = StateGraph(AgentState)
    for name, fn in [("mem_get",node_memory_retrieve),("plan",node_planner),("research",node_research),
                     ("analysis",node_analysis),("code",node_code),("content",node_content),("mem_put",node_memory_store)]:
        g.add_node(name, fn)
    g.add_edge(START,"mem_get"); g.add_edge("mem_get","plan"); g.add_edge("plan","research")
    g.add_edge("research","analysis"); g.add_edge("analysis","code"); g.add_edge("code","content")
    g.add_edge("content","mem_put"); g.add_edge("mem_put",END)
    return g.compile()

def _initial(task: str, output_dir: str) -> AgentState:
    return {"task":task,"output_dir":output_dir,"plan":{},"memory_context":"",
            "research_output":"","analysis_output":"","chart_paths":[],"chart_data":{},
            "final_report":"","report_path":"","pdf_path":"","sources_count":0,
            "word_count":0,"errors":[],"agent_log":[],"start_time":time.time()}

def _run_sequential(task: str, output_dir: str) -> AgentState:
    s = _initial(task, output_dir)
    for fn in [node_memory_retrieve,node_planner,node_research,node_analysis,node_code,node_content,node_memory_store]:
        try: s = fn(s)
        except Exception as e:
            logger.error(f"[Seq] {fn.__name__}: {e}")
            s["errors"].append(f"{fn.__name__}: {e}")
    return s

class BusinessOperator:
    def __init__(self, output_dir: str = "./reports"):
        self.output_dir = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)
        self.graph = build_graph() if LANGGRAPH_OK else None
        logger.info(f"[BusinessOperator] {'LangGraph' if self.graph else 'Sequential'} pipeline ready")

    def run(self, task: str) -> Dict[str, Any]:
        logger.info(f"[BusinessOperator] Task: {task}")
        start = time.time()
        s = _initial(task, self.output_dir)
        final = self.graph.invoke(s) if self.graph else _run_sequential(task, self.output_dir)
        elapsed = round(time.time() - start, 2)
        logger.info(f"[BusinessOperator] Done in {elapsed}s")
        return {
            "task": task, "elapsed_time": elapsed,
            "final_report": final.get("final_report",""), "research_output": final.get("research_output",""),
            "analysis_output": final.get("analysis_output",""), "chart_paths": final.get("chart_paths",[]),
            "report_path": final.get("report_path",""), "pdf_path": final.get("pdf_path",""),
            "plan": final.get("plan",{}), "sources_count": final.get("sources_count",0),
            "word_count": final.get("word_count",0), "agent_log": final.get("agent_log",[]),
            "errors": final.get("errors",[]),
        }
