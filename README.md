# 🤖 AI Business Operator

An autonomous **multi-agent AI system** that does market research, competitor analysis, business reporting, and marketing content generation — all powered by **Google Gemini (free tier)**.

---

## ⚡ Quick Start (3 steps)

```bash
# 1. Clone and enter the project
git clone https://github.com/yourname/ai-business-operator
cd ai-business-operator

# 2. Add your free Gemini API key
cp .env.example .env
# Edit .env → set GEMINI_API_KEY=AIzaSy...
# Get free key at: https://aistudio.google.com/apikey

# 3. Start everything
chmod +x start.sh && ./start.sh      # Mac/Linux
start.bat                             # Windows
```

Open **http://localhost:8000** — the React dashboard is served automatically.

---

## 🏗 Architecture

```
Browser (React UI)
      ↓ REST API
FastAPI Server
      ↓
LangGraph Orchestrator
      ↓
┌─────────────────────────────────────┐
│           Agent Pipeline            │
│  🧠 Memory  → retrieves context     │
│  🗺  Planner → breaks into steps    │
│  🔍 Research → searches the web     │
│  📊 Analysis → SWOT + insights      │
│  ⚙  Code    → generates charts     │
│  ✍  Content → writes report        │
│  🧠 Memory  → stores knowledge      │
└─────────────────────────────────────┘
      ↓
  Markdown + PDF report + PNG charts
```

---

## 📁 Project Structure

```
ai-business-operator/
├── agents/
│   ├── base_agent.py          # LLM integration (Gemini / Anthropic)
│   ├── planner_agent.py       # Task decomposition
│   ├── research_agent.py      # Web search + synthesis
│   ├── analysis_agent.py      # SWOT, competitive analysis
│   ├── code_agent.py          # Chart code generation + execution
│   ├── content_agent.py       # Report + PDF writing
│   └── memory_agent.py        # FAISS vector store
│
├── tools/
│   ├── web_search.py          # DuckDuckGo (free)
│   ├── scraper.py             # Web page extraction
│   ├── python_executor.py     # Safe chart sandbox
│   └── vector_store.py        # FAISS semantic memory
│
├── memory/
│   └── knowledge_base.py      # LangGraph pipeline orchestrator
│
├── api/
│   └── main.py                # FastAPI server (serves React + REST)
│
├── frontend/                  # React + Vite dashboard
│   ├── src/
│   │   ├── App.jsx
│   │   ├── components/
│   │   │   ├── Sidebar.jsx
│   │   │   ├── Header.jsx
│   │   │   ├── TaskInput.jsx
│   │   │   ├── AgentPipeline.jsx
│   │   │   ├── ResultPanel.jsx
│   │   │   ├── HistoryPanel.jsx
│   │   │   └── SettingsModal.jsx
│   │   └── utils/api.js
│   └── dist/                  # Built React app (served by FastAPI)
│
├── reports/                   # Generated .md, .pdf, .png files
├── config/settings.py         # Central config
├── run.py                     # CLI entry point
├── start.sh / start.bat       # One-command launchers
└── .env.example
```

---

## 🤖 The 6 Agents

| Agent | Role |
|-------|------|
| 🗺 Planner | Decomposes task into JSON plan with search queries, focus areas, chart suggestions |
| 🔍 Research | Runs DuckDuckGo searches, scrapes top results, synthesises with Gemini |
| 📊 Analysis | SWOT analysis, competitive landscape, trend extraction, chart data |
| ⚙ Code | Generates + executes matplotlib Python for PNG charts |
| ✍ Content | Writes full Markdown report + PDF with reportlab |
| 🧠 Memory | FAISS vector store — stores past research, retrieves relevant context |

---

## 🌐 REST API

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check |
| POST | `/api/tasks` | Submit task (async) |
| POST | `/api/tasks/sync` | Run task (blocking) |
| GET | `/api/tasks/{id}` | Poll task result |
| GET | `/api/tasks` | List all tasks |
| GET | `/api/reports` | List generated files |
| GET | `/api/reports/download/{file}` | Download report |
| GET | `/api/memory/stats` | Memory stats |

Interactive docs: **http://localhost:8000/docs**

---

## ⚙️ Configuration (.env)

```env
# Required
LLM_PROVIDER=gemini
GEMINI_API_KEY=AIzaSy...          # Free at aistudio.google.com/apikey

# Gemini models (all free tier)
GEMINI_MODEL=gemini-2.0-flash     # Recommended — fastest
# GEMINI_MODEL=gemini-1.5-pro-latest  # Most capable

# Optional fallback
ANTHROPIC_API_KEY=sk-ant-...

# App
APP_PORT=8000
REPORTS_DIR=./reports
MAX_TOKENS_PER_AGENT=2000
ENABLE_WEB_SEARCH=true
ENABLE_MEMORY=true
```

---

## 🖥 React UI Features

- **Task input** with mode selector (Auto / Research / Analysis / Content / Report)
- **Agent pipeline** — 6 animated cards with shimmer effect + progress bar
- **Result tabs** — Report (rendered Markdown), Analysis, Research, Charts, Agent Log
- **Settings modal** — API key entry with show/hide, model picker, connection test
- **History panel** — click any past task to reload it
- **Download** — Markdown and PDF report download buttons
- Keyboard shortcut: **Ctrl+Enter** to run

---

## 💼 Resume Description

```
Developed an Autonomous AI Business Operating System using LangGraph for
multi-agent orchestration. The system employs 6 specialized agents
(Planner, Research, Analysis, Code, Content, Memory) that autonomously
perform market research, competitive analysis, and business report
generation. Built with FastAPI backend, React + Vite dashboard, FAISS
vector memory, DuckDuckGo search integration, and Google Gemini (free tier)
as the LLM provider. Delivers PDF reports and data visualisations from a
single natural-language prompt.
```

---

## 📄 License

MIT — free to use, modify, and distribute.
