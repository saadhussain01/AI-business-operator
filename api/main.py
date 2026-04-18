"""
api/main.py — FastAPI REST API for the AI Business Operator
Serves the React frontend and exposes agent pipeline endpoints.
"""
from __future__ import annotations
import sys
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict, Any

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from loguru import logger

from config.settings import settings

app = FastAPI(
    title="AI Business Operator",
    description="Autonomous multi-agent AI system",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory task store
task_store: Dict[str, Dict[str, Any]] = {}


class TaskRequest(BaseModel):
    task: str
    mode: Optional[str] = "auto"
    gemini_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    provider: Optional[str] = "gemini"
    model: Optional[str] = "gemini-2.0-flash"


class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str


def run_task_background(task_id: str, task: str, provider: str, api_key: str, model: str):
    import os
    # Set keys for this run
    if provider == "gemini":
        os.environ["GEMINI_API_KEY"] = api_key
        os.environ["GEMINI_MODEL"] = model
        os.environ["LLM_PROVIDER"] = "gemini"
    else:
        os.environ["ANTHROPIC_API_KEY"] = api_key
        os.environ["LLM_PROVIDER"] = "anthropic"

    # Reload settings
    import importlib
    import config.settings as cs
    importlib.reload(cs)
    from config.settings import settings as s
    s.GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    s.GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
    s.LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "gemini")

    try:
        task_store[task_id]["status"] = "running"
        from memory.knowledge_base import BusinessOperator
        operator = BusinessOperator(output_dir=settings.REPORTS_DIR)
        result = operator.run(task)
        task_store[task_id].update({
            "status": "completed",
            "result": result,
            "completed_at": datetime.now().isoformat(),
        })
        logger.info(f"[API] Task {task_id} done in {result['elapsed_time']}s")
    except Exception as e:
        logger.error(f"[API] Task {task_id} failed: {e}")
        task_store[task_id].update({
            "status": "failed",
            "error": str(e),
            "completed_at": datetime.now().isoformat(),
        })


@app.get("/api/health")
def health():
    return {
        "status": "online",
        "version": "1.0.0",
        "agents": ["Planner", "Research", "Analysis", "Code", "Content", "Memory"],
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/api/tasks", response_model=TaskResponse)
def create_task(req: TaskRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())[:8]
    api_key = req.gemini_api_key or req.anthropic_api_key or ""
    provider = req.provider or "gemini"
    model = req.model or "gemini-2.0-flash"

    task_store[task_id] = {
        "task_id": task_id,
        "task": req.task,
        "status": "queued",
        "created_at": datetime.now().isoformat(),
        "result": None,
        "error": None,
    }

    background_tasks.add_task(run_task_background, task_id, req.task, provider, api_key, model)

    return TaskResponse(
        task_id=task_id,
        status="queued",
        message=f"Task queued. Poll GET /api/tasks/{task_id} for results.",
    )


@app.post("/api/tasks/sync")
def run_task_sync(req: TaskRequest):
    import os
    if req.gemini_api_key:
        os.environ["GEMINI_API_KEY"] = req.gemini_api_key
        os.environ["GEMINI_MODEL"] = req.model or "gemini-2.0-flash"
        os.environ["LLM_PROVIDER"] = "gemini"
    elif req.anthropic_api_key:
        os.environ["ANTHROPIC_API_KEY"] = req.anthropic_api_key
        os.environ["LLM_PROVIDER"] = "anthropic"

    import importlib
    import config.settings as cs
    importlib.reload(cs)
    from config.settings import settings as s
    s.GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")
    s.GEMINI_MODEL = os.environ.get("GEMINI_MODEL", "gemini-2.0-flash")
    s.LLM_PROVIDER = os.environ.get("LLM_PROVIDER", "gemini")

    try:
        from memory.knowledge_base import BusinessOperator
        operator = BusinessOperator(output_dir=settings.REPORTS_DIR)
        result = operator.run(req.task)
        return {"status": "completed", **result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/tasks/{task_id}")
def get_task(task_id: str):
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


@app.get("/api/tasks")
def list_tasks():
    return [
        {"task_id": v["task_id"], "task": v["task"][:80],
         "status": v["status"], "created_at": v["created_at"]}
        for v in task_store.values()
    ]


@app.get("/api/reports")
def list_reports():
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
                "download_url": f"/api/reports/download/{f.name}",
            })
    return files


@app.get("/api/reports/download/{filename}")
def download_report(filename: str):
    file_path = Path(settings.REPORTS_DIR) / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(str(file_path), filename=filename)


@app.get("/api/memory/stats")
def memory_stats():
    from agents.memory_agent import MemoryAgent
    agent = MemoryAgent()
    return agent.get_stats()


# Serve React build if it exists
react_build = Path(__file__).parent.parent / "frontend" / "dist"
if react_build.exists():
    app.mount("/", StaticFiles(directory=str(react_build), html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host=settings.APP_HOST, port=settings.APP_PORT,
                reload=settings.DEBUG, log_level=settings.LOG_LEVEL.lower())
