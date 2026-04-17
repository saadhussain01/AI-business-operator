# 🤖 AI Business Operator

An autonomous **multi-agent AI system** that acts as a digital operations assistant for small businesses. It automatically handles market research, competitor analysis, business reporting, marketing content, and trend monitoring — replacing work that typically takes 5–10 hours per week.

---

## 🏗 Architecture

```
User Input (CLI / Streamlit UI / REST API)
         ↓
   AI Business Operator (LangGraph Orchestrator)
         ↓
┌─────────────────────────────────────────────┐
│              Agent Pipeline                 │
│                                             │
│  🧠 Memory Agent  ←──── retrieves context  │
│       ↓                                     │
│  🗺  Planner Agent  ←── breaks into steps  │
│       ↓                                     │
│  🔍 Research Agent  ←── searches the web   │
│       ↓                                     │
│  📊 Analysis Agent  ←── finds patterns     │
│       ↓                                     │
│  ⚙  Code Agent  ←──── generates charts    │
│       ↓                                     │
│  ✍  Content Agent  ←── writes reports     │
│       ↓                                     │
│  🧠 Memory Agent  ←──── stores knowledge  │
└─────────────────────────────────────────────┘
         ↓
   Output: Report (MD + PDF) + Charts + Analysis
```

---

## 📁 Project Structure

```
ai-business-operator/
│
├── agents/
│   ├── base_agent.py          # Base class with LLM integration
│   ├── planner_agent.py       # Task decomposition into structured plans
│   ├── research_agent.py      # Web search + synthesis
│   ├── analysis_agent.py      # SWOT, competitive analysis, insights
│   ├── code_agent.py          # Chart/visualization generation
│   ├── content_agent.py       # Report + marketing content writing
│   └── memory_agent.py        # FAISS vector store read/write
│
├── tools/
│   ├── web_search.py          # DuckDuckGo search (free, no API key)
│   ├── scraper.py             # Web page content extraction
│   ├── python_executor.py     # Safe Python sandbox for chart code
│   └── vector_store.py        # FAISS semantic memory store
│
├── memory/
│   ├── knowledge_base.py      # LangGraph orchestrator (main pipeline)
│   └── vector_store/          # Persisted FAISS index (auto-created)
│
├── api/
│   └── main.py                # FastAPI REST API
│
├── ui/
│   └── streamlit_app.py       # Streamlit web dashboard
│
├── reports/                   # Generated reports and charts (auto-created)
├── config/
│   └── settings.py            # Central configuration
│
├── run.py                     # CLI entry point
├── requirements.txt
└── .env.example
```

---

## 🚀 Quick Start

### 1. Clone and install

```bash
git clone https://github.com/yourname/ai-business-operator
cd ai-business-operator

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### 2. Configure environment

```bash
cp .env.example .env
```

Edit `.env` and set your API key:

```env
# Option A — Google Gemini (FREE — Recommended)
# Get free key at: https://aistudio.google.com/apikey
GEMINI_API_KEY=AIza...
LLM_PROVIDER=gemini

# Option B — Anthropic Claude
ANTHROPIC_API_KEY=sk-ant-...
LLM_PROVIDER=anthropic
```

> **Web search is FREE** — uses DuckDuckGo, no API key required.

### 3. Run

**Option A: Command Line (fastest)**
```bash
python run.py "Analyze competitors of Tesla in the EV market"
```

**Option B: Streamlit Dashboard (recommended)**
```bash
streamlit run ui/streamlit_app.py
```
Then open http://localhost:8501

**Option C: REST API**
```bash
# Start the API server
uvicorn api.main:app --reload --port 8000

# Submit a task
curl -X POST http://localhost:8000/tasks/sync \
  -H "Content-Type: application/json" \
  -d '{"task": "Analyze EV market competitors of Tesla"}'
```

---

## 🤖 The 6 Agents

### 1. 🗺 Planner Agent
Decomposes your task into a structured JSON execution plan:
- Search queries to run
- Analysis focus areas  
- Chart suggestions
- Output format selection

### 2. 🔍 Research Agent
Searches the web using DuckDuckGo:
- Runs multiple targeted queries from the plan
- Searches for recent news
- Deep-scrapes top results for fuller context
- Synthesizes findings with LLM

### 3. 📊 Analysis Agent
Performs structured business analysis:
- Executive summary
- Competitive landscape (top players, positioning)
- SWOT analysis
- Key trends and data insights
- Strategic recommendations
- Extracts chart data for the Code Agent

### 4. ⚙ Code Agent
Generates and executes Python visualization code:
- Bar charts, line charts, pie charts
- Uses matplotlib + seaborn
- Runs in a safe sandbox
- Saves PNG chart files

### 5. ✍ Content Agent
Produces final documents:
- Full business report (Markdown + PDF)
- Marketing posts (LinkedIn, blog)
- Professional formatting with reportlab

### 6. 🧠 Memory Agent
Manages persistent knowledge:
- Stores completed research in FAISS vector store
- Retrieves relevant past research for new tasks
- Semantic similarity search (sentence-transformers)

---

## 📊 Example Use Cases

### Market Research
```bash
python run.py "Research the AI startup ecosystem in healthcare for 2025"
```
**Output:** Market trends, startup list, investment stats, growth predictions

### Competitor Analysis
```bash
python run.py "Compare OpenAI, Anthropic, and Google DeepMind"
```
**Output:** Feature comparison, market positioning, SWOT, strategic insights

### Marketing Content
```bash
python run.py "Generate LinkedIn posts promoting a B2B SaaS analytics platform"
```
**Output:** 5 ready-to-publish LinkedIn posts with hooks, hashtags, and CTAs

### Business Report
```bash
python run.py "Analyze the global e-commerce market and predict 2025 growth sectors"
```
**Output:** Full PDF report with executive summary, analysis, charts, recommendations

---

## 🌐 REST API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | System info |
| GET | `/health` | Health check |
| POST | `/tasks` | Submit task (async) |
| POST | `/tasks/sync` | Run task (blocking) |
| GET | `/tasks/{id}` | Get task result |
| GET | `/tasks` | List all tasks |
| GET | `/reports` | List reports |
| GET | `/reports/download/{filename}` | Download report |
| GET | `/memory/stats` | Memory statistics |
| DELETE | `/memory/clear` | Clear memory |

**Interactive API docs:** http://localhost:8000/docs

---

## ⏰ Scheduling (Automated Daily Research)

```bash
# Run every day at 9:00 AM
python run.py --schedule "Generate daily EV market briefing" --time "09:00"
```

The system will automatically:
1. Run the full agent pipeline
2. Save the report to `./reports/`
3. Sleep until the next run

---

## 🔧 Interactive REPL Mode

```bash
python run.py --interactive
```

Run tasks one after another in a conversational loop. Type `history` to see past tasks.

---

## 🧱 Tech Stack

| Layer | Technology |
|-------|-----------|
| Agent Orchestration | LangGraph |
| LLM | Google Gemini (free) / Anthropic Claude |
| Web Search | DuckDuckGo (free) |
| Vector Memory | FAISS + sentence-transformers |
| Data Analysis | pandas, numpy, matplotlib, seaborn |
| REST API | FastAPI + uvicorn |
| Web UI | Streamlit |
| PDF Generation | reportlab |
| Config | python-dotenv |
| Logging | loguru, rich |

---

## 💼 Resume Description

```
Developed an Autonomous AI Business Operating System using LangGraph for 
multi-agent orchestration. The system employs 6 specialized agents 
(Planner, Research, Analysis, Code, Content, Memory) that autonomously 
perform market research, competitive analysis, and business report 
generation. Built with FastAPI backend, Streamlit dashboard, FAISS vector 
memory, and DuckDuckGo web search integration. Capable of replacing 5–10 
hours per week of manual business research work.
```

---

## 📄 License

MIT License — free to use, modify, and distribute.
#   A I - b u s i n e s s - o p e r a t o r  
 