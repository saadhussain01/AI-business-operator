#!/usr/bin/env bash
# ============================================================
# AI Business Operator — One-command launcher
# Usage: ./start.sh
# ============================================================
set -e

ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$ROOT"

# ── Colours ──────────────────────────────────────────────────
G='\033[0;32m'; B='\033[0;34m'; Y='\033[1;33m'; R='\033[0;31m'; N='\033[0m'

echo -e "${B}"
echo "  ██████╗ ██╗   ██╗███████╗██╗███╗   ██╗███████╗███████╗███████╗"
echo "  ██╔══██╗██║   ██║██╔════╝██║████╗  ██║██╔════╝██╔════╝██╔════╝"
echo "  ██████╔╝██║   ██║███████╗██║██╔██╗ ██║█████╗  ███████╗███████╗"
echo "  ██╔══██╗██║   ██║╚════██║██║██║╚██╗██║██╔══╝  ╚════██║╚════██║"
echo "  ██████╔╝╚██████╔╝███████║██║██║ ╚████║███████╗███████║███████║"
echo "  ╚═════╝  ╚═════╝ ╚══════╝╚═╝╚═╝  ╚═══╝╚══════╝╚══════╝╚══════╝"
echo -e "${N}"
echo -e "  ${G}AI Business Operator${N} — Powered by Google Gemini (Free)"
echo ""

# ── Check .env ───────────────────────────────────────────────
if [ ! -f ".env" ]; then
    echo -e "${Y}⚠  No .env found — copying from .env.example${N}"
    cp .env.example .env
    echo -e "${R}→  Edit .env and add your GEMINI_API_KEY, then re-run this script.${N}"
    echo -e "   Get a free key at: https://aistudio.google.com/apikey"
    exit 1
fi

# ── Python venv ───────────────────────────────────────────────
if [ ! -d "venv" ]; then
    echo -e "${B}Creating Python virtual environment...${N}"
    python3 -m venv venv
fi
source venv/bin/activate

# ── Install Python deps ────────────────────────────────────────
echo -e "${B}Installing Python dependencies...${N}"
pip install -r requirements.txt -q

# ── Create directories ─────────────────────────────────────────
mkdir -p reports memory/vector_store

# ── Start FastAPI ──────────────────────────────────────────────
echo ""
echo -e "${G}✅ Starting API server on http://localhost:8000${N}"
echo -e "${G}✅ React frontend served at  http://localhost:8000${N}"
echo -e "${G}✅ API docs at               http://localhost:8000/docs${N}"
echo ""
echo -e "${Y}Open http://localhost:8000 in your browser${N}"
echo -e "${Y}Press Ctrl+C to stop${N}"
echo ""

uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
