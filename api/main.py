"""
api/main.py — FastAPI REST API for the AI Business Operator
Exposes endpoints to run agent tasks, view history, and download reports.
"""
from __future__ import annotations
import os
import sys
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from loguru import logger

from memory.knowledge_base import BusinessOperator
from config.settings import settings

# ─── App Setup ────────────────────────────────────────────────────────────────

app = FastAPI(
    title="AI Business Operator",
    description="Autonomous multi-agent AI system for business research, analysis, and content generation",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory task store (use Redis for production)
task_store: Dict[str, Dict[str, Any]] = {}

# Initialize operator
operator = BusinessOperator(output_dir=settings.REPORTS_DIR)


# ─── Pydantic Models ──────────────────────────────────────────────────────────

class TaskRequest(BaseModel):
    task: str
    mode: Optional[str] = "auto"  # auto | research | analysis | content | report


class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str


class TaskResult(BaseModel):
    task_id: str
    status: str
    task: str
    elapsed_time: float
    final_report: str
    research_output: str
    analysis_output: str
    chart_paths: List[str]
    report_path: str
    pdf_path: str
    sources_count: int
    word_count: int
    agent_log: List[Dict]
    errors: List[str]
    created_at: str


# ─── Background Task Runner ───────────────────────────────────────────────────

def run_task_background(task_id: str, task: str, mode: str):
    """Execute the agent pipeline in the background."""
    try:
        task_store[task_id]["status"] = "running"
        logger.info(f"[API] Starting task {task_id}: {task[:50]}...")

        result = operator.run(task)

        task_store[task_id].update({
            "status": "completed",
            "result": result,
            "completed_at": datetime.now().isoformat(),
        })
        logger.info(f"[API] Task {task_id} completed in {result['elapsed_time']}s")

    except Exception as e:
        logger.error(f"[API] Task {task_id} failed: {e}")
        task_store[task_id].update({
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.now().isoformat(),
        })


# ─── Endpoints ────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "version": "1.0.0",
        "status": "online",
        "agents": ["PlannerAgent", "ResearchAgent", "AnalysisAgent", "CodeAgent", "ContentAgent", "MemoryAgent"],
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/tasks", response_model=TaskResponse)
def create_task(request: TaskRequest, background_tasks: BackgroundTasks):
    """
    Submit a new business task to the agent pipeline.
    Returns a task_id immediately; use GET /tasks/{task_id} to poll for results.
    """
    import uuid
    task_id = str(uuid.uuid4())[:8]

    task_store[task_id] = {
        "task_id": task_id,
        "task": request.task,
        "mode": request.mode,
        "status": "queued",
        "created_at": datetime.now().isoformat(),
        "result": None,
        "error": None,
    }

    background_tasks.add_task(run_task_background, task_id, request.task, request.mode)

    return TaskResponse(
        task_id=task_id,
        status="queued",
        message=f"Task queued. Poll GET /tasks/{task_id} for results.",
    )


@app.post("/tasks/sync")
def run_task_sync(request: TaskRequest):
    """
    Run a task synchronously (blocks until complete).
    Good for testing; use /tasks (async) for production.
    """
    try:
        result = operator.run(request.task)
        return {"status": "completed", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/tasks/{task_id}")
def get_task(task_id: str):
    """Get the status and result of a task."""
    if task_id not in task_store:
        raise HTTPException(status_code=404, detail="Task not found")

    entry = task_store[task_id]

    if entry["status"] in ("queued", "running"):
        return {"task_id": task_id, "status": entry["status"], "task": entry["task"]}

    if entry["status"] == "failed":
        return {"task_id": task_id, "status": "failed", "error": entry.get("error")}

    result = entry.get("result", {})
    return {
        "task_id": task_id,
        "status": "completed",
        "task": entry["task"],
        "created_at": entry["created_at"],
        "completed_at": entry.get("completed_at"),
        **result,
    }


@app.get("/tasks")
def list_tasks():
    """List all tasks with their statuses."""
    return [
        {
            "task_id": v["task_id"],
            "task": v["task"][:80],
            "status": v["status"],
            "created_at": v["created_at"],
        }
        for v in task_store.values()
    ]


@app.delete("/tasks/{task_id}")
def delete_task(task_id: str):
    if task_id not in task_store:
        raise HTTPException(status_code=404, detail="Task not found")
    del task_store[task_id]
    return {"message": f"Task {task_id} deleted"}


@app.get("/reports")
def list_reports():
    """List all generated report files."""
    reports_dir = Path(settings.REPORTS_DIR)
    if not reports_dir.exists():
        return []
    files = []
    for f in sorted(reports_dir.iterdir(), reverse=True):
        if f.suffix in (".md", ".pdf", ".png"):
            files.append({
                "name": f.name,
                "type": f.suffix[1:],
                "size_kb": round(f.stat().st_size / 1024, 1),
                "modified": datetime.fromtimestamp(f.stat().st_mtime).isoformat(),
                "download_url": f"/reports/download/{f.name}",
            })
    return files


@app.get("/reports/download/{filename}")
def download_report(filename: str):
    """Download a report file."""
    file_path = Path(settings.REPORTS_DIR) / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(str(file_path), filename=filename)


@app.get("/memory/stats")
def memory_stats():
    """Get vector memory statistics."""
    from agents.memory_agent import MemoryAgent
    agent = MemoryAgent()
    stats = agent.get_stats()
    return stats


@app.delete("/memory/clear")
def clear_memory():
    """Clear the vector memory store."""
    from tools.vector_store import VectorStore
    store = VectorStore()
    store.clear()
    return {"message": "Memory cleared"}


# ─── Run ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower(),
    )
