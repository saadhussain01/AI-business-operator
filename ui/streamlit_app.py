"""
ui/streamlit_app.py — Streamlit Web UI for AI Business Operator

Run with:
    streamlit run ui/streamlit_app.py
"""
from __future__ import annotations
import sys
import time
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st
from loguru import logger

st.set_page_config(
    page_title="AI Business Operator",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    .main-title {
        font-size: 2rem; font-weight: 700;
        background: linear-gradient(135deg, #1a1a2e, #16213e, #0f3460);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .subtitle { color: #6b7280; font-size: 1rem; margin-bottom: 1.5rem; }
    .agent-card {
        background: #f8fafc; border: 1px solid #e2e8f0;
        border-radius: 10px; padding: 1rem; text-align: center;
        transition: all 0.3s;
    }
    .agent-active { border-color: #3b82f6 !important; background: #eff6ff !important; }
    .agent-done   { border-color: #22c55e !important; background: #f0fdf4 !important; }
    .stat-card {
        background: #f1f5f9; border-radius: 8px;
        padding: 0.75rem 1rem; text-align: center;
    }
    .stat-val  { font-size: 1.6rem; font-weight: 700; color: #1a1a2e; }
    .stat-label { font-size: 0.75rem; color: #64748b; margin-top: 2px; }
    .step-done    { color: #16a34a; }
    .step-running { color: #2563eb; animation: blink 1s infinite; }
    .step-pending { color: #94a3b8; }
    @keyframes blink { 0%,100%{opacity:1} 50%{opacity:0.4} }
    .gemini-badge {
        background: #e8f5e9; color: #2e7d32;
        border-radius: 6px; padding: 3px 8px;
        font-size: 0.75rem; font-weight: 600;
        border: 1px solid #a5d6a7;
    }
</style>
""", unsafe_allow_html=True)

# ─── Sidebar ──────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown("## ⚙️ Configuration")

    llm_provider = st.selectbox(
        "LLM Provider",
        ["Gemini (Free)", "Anthropic Claude"],
        index=0,
        help="Gemini is free — get your key at aistudio.google.com"
    )

    if llm_provider == "Gemini (Free)":
        api_key = st.text_input(
            "Gemini API Key",
            type="password",
            placeholder="AIza...",
            help="Free at https://aistudio.google.com/apikey",
        )
        gemini_model = st.selectbox(
            "Gemini Model",
            ["gemini-1.5-flash", "gemini-1.5-pro", "gemini-2.0-flash-exp"],
            index=0,
            help="gemini-1.5-flash is fastest and free",
        )
        if api_key:
            import os
            os.environ["GEMINI_API_KEY"] = api_key
            os.environ["GEMINI_MODEL"] = gemini_model
            os.environ["LLM_PROVIDER"] = "gemini"
        st.markdown(
            '<span class="gemini-badge">✓ FREE — No cost</span>',
            unsafe_allow_html=True,
        )
        st.caption("Get free key → [aistudio.google.com](https://aistudio.google.com/apikey)")
    else:
        api_key = st.text_input(
            "Anthropic API Key",
            type="password",
            placeholder="sk-ant-...",
        )
        if api_key:
            import os
            os.environ["ANTHROPIC_API_KEY"] = api_key
            os.environ["LLM_PROVIDER"] = "anthropic"

    st.markdown("---")
    st.markdown("## 🔧 Agent Settings")
    enable_memory = st.toggle("Enable Memory", value=True)
    enable_charts = st.toggle("Generate Charts", value=True)
    enable_pdf = st.toggle("Generate PDF Report", value=True)

    st.markdown("---")
    st.markdown("## 📋 Quick Tasks")
    quick_tasks = {
        "🚗 Tesla EV Competitors": "Analyze competitors of Tesla in the EV market and generate a business report with market share analysis",
        "🏥 Healthcare AI Startups": "Research AI startups in the healthcare sector and identify the top 5 investment opportunities",
        "🤖 LLM Company Comparison": "Compare Google Gemini, Anthropic Claude, Meta AI, and Mistral as competitors in the LLM space",
        "📱 LinkedIn Marketing Posts": "Generate 5 LinkedIn marketing posts promoting an AI-powered business analytics SaaS product",
        "🛒 E-Commerce Trends 2025": "Analyze current e-commerce market trends and predict key growth sectors for 2025",
        "💊 Pharma Market Analysis": "Analyze the global pharmaceutical market and identify top growth opportunities",
    }

    for label, task_text in quick_tasks.items():
        if st.button(label, use_container_width=True):
            st.session_state["task_input"] = task_text

    st.markdown("---")
    st.markdown("**AI Business Operator v1.0**")
    st.markdown("Powered by LangGraph + Gemini (Free)")

# ─── Main Area ────────────────────────────────────────────────────────────────

st.markdown('<div class="main-title">🤖 AI Business Operator</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Autonomous multi-agent system · Powered by Google Gemini (Free)</div>', unsafe_allow_html=True)

col1, col2, col3, col4 = st.columns(4)
with col1:
    tasks_run = st.session_state.get("tasks_run", 0)
    st.markdown(f'<div class="stat-card"><div class="stat-val">{tasks_run}</div><div class="stat-label">Tasks Run</div></div>', unsafe_allow_html=True)
with col2:
    st.markdown('<div class="stat-card"><div class="stat-val">6</div><div class="stat-label">Active Agents</div></div>', unsafe_allow_html=True)
with col3:
    reports_count = len(list(Path("./reports").glob("*.md"))) if Path("./reports").exists() else 0
    st.markdown(f'<div class="stat-card"><div class="stat-val">{reports_count}</div><div class="stat-label">Reports Generated</div></div>', unsafe_allow_html=True)
with col4:
    st.markdown('<div class="stat-card"><div class="stat-val">FREE</div><div class="stat-label">Gemini API Cost</div></div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

task_value = st.session_state.get("task_input", "")
task = st.text_area(
    "📝 Enter your business task",
    value=task_value,
    height=100,
    placeholder="Example: Analyze competitors of Tesla in the EV market and generate a comprehensive business report...",
    key="task_textarea",
)

col_mode, col_run = st.columns([3, 1])
with col_mode:
    mode = st.radio(
        "Task mode:",
        ["Auto", "Market Research", "Competitor Analysis", "Content Creation", "Business Report"],
        horizontal=True,
    )
with col_run:
    st.markdown("<br>", unsafe_allow_html=True)
    run_clicked = st.button("🚀 Run Agents", type="primary", use_container_width=True)

st.markdown("### 🔄 Agent Pipeline")
agent_cols = st.columns(6)
agent_info = [
    ("🗺️", "Planner", "Breaks task into steps"),
    ("🔍", "Research", "Searches the web"),
    ("📊", "Analysis", "Finds patterns"),
    ("⚙️", "Code", "Generates charts"),
    ("✍️", "Content", "Writes report"),
    ("🧠", "Memory", "Stores knowledge"),
]
agent_placeholders = []
for col, (icon, name, desc) in zip(agent_cols, agent_info):
    with col:
        ph = st.empty()
        ph.markdown(f'<div class="agent-card"><div style="font-size:1.5rem">{icon}</div><b>{name}</b><br><small style="color:#94a3b8">{desc}</small><br><small class="step-pending">● idle</small></div>', unsafe_allow_html=True)
        agent_placeholders.append((ph, icon, name, desc))

st.markdown("---")

tab_report, tab_analysis, tab_research, tab_charts, tab_log = st.tabs([
    "📄 Report", "📊 Analysis", "🔍 Research", "📈 Charts", "📋 Agent Log"
])

if run_clicked and task.strip():
    if not api_key:
        provider_name = "Gemini" if "Gemini" in llm_provider else "Anthropic"
        st.error(f"⚠️ Please enter your {provider_name} API key in the sidebar first.")
        if "Gemini" in llm_provider:
            st.info("🆓 Get a FREE Gemini API key at https://aistudio.google.com/apikey")
        st.stop()

    from config.settings import settings
    from memory.knowledge_base import BusinessOperator

    st.session_state["tasks_run"] = st.session_state.get("tasks_run", 0) + 1

    progress_bar = st.progress(0, text="Initializing agents...")
    status_text = st.empty()

    agent_steps = ["Planner", "Research", "Analysis", "Code", "Content", "Memory"]
    pct_per_step = 100 // len(agent_steps)

    def update_agent(idx: int, state: str):
        ph, icon, name, desc = agent_placeholders[idx]
        css_class = "agent-active" if state == "active" else "agent-done"
        dot_class = "step-running" if state == "active" else "step-done"
        dot_label = "● working..." if state == "active" else "✓ done"
        ph.markdown(
            f'<div class="agent-card {css_class}"><div style="font-size:1.5rem">{icon}</div><b>{name}</b><br>'
            f'<small style="color:#94a3b8">{desc}</small><br>'
            f'<small class="{dot_class}">{dot_label}</small></div>',
            unsafe_allow_html=True,
        )

    try:
        operator = BusinessOperator(output_dir="./reports")

        for i in range(6):
            ph, icon, name, desc = agent_placeholders[i]
            ph.markdown(
                f'<div class="agent-card"><div style="font-size:1.5rem">{icon}</div><b>{name}</b><br>'
                f'<small style="color:#94a3b8">{desc}</small><br>'
                f'<small class="step-pending">● queued</small></div>',
                unsafe_allow_html=True,
            )

        status_text.info("🚀 Pipeline started — Gemini agents working...")
        update_agent(0, "active")
        progress_bar.progress(5, text="Planner Agent: decomposing task...")

        result = operator.run(task)

        for i, agent_name in enumerate(agent_steps):
            update_agent(i, "done")
            progress_bar.progress(min(100, (i + 1) * pct_per_step), text=f"{agent_name} Agent: complete ✓")
            time.sleep(0.15)

        progress_bar.progress(100, text="All agents complete ✅")
        status_text.success(
            f"✅ Task completed in {result['elapsed_time']}s · "
            f"{result.get('sources_count', 0)} sources · "
            f"{result.get('word_count', 0)} words · "
            f"Powered by Gemini (FREE)"
        )

        st.session_state["last_result"] = result

    except Exception as e:
        st.error(f"❌ Pipeline error: {e}")
        logger.exception(e)
        st.stop()

result = st.session_state.get("last_result")

with tab_report:
    if result:
        st.markdown(f"**Task:** {result['task']}")
        st.markdown(
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M')} · "
            f"**Time:** {result['elapsed_time']}s · "
            f"**Words:** {result.get('word_count', '—')} · "
            f"**Model:** Gemini"
        )
        st.divider()
        report_text = result.get("final_report", "")
        if report_text:
            st.markdown(report_text)
        else:
            st.info("No report generated yet.")

        if result.get("report_path") and Path(result["report_path"]).exists():
            with open(result["report_path"]) as f:
                st.download_button("⬇️ Download Markdown Report", f.read(), file_name=Path(result["report_path"]).name)

        if result.get("pdf_path") and Path(result["pdf_path"]).exists():
            with open(result["pdf_path"], "rb") as f:
                st.download_button("⬇️ Download PDF Report", f.read(),
                                   file_name=Path(result["pdf_path"]).name, mime="application/pdf")
    else:
        st.info("👆 Enter a task above and click **Run Agents** to generate a report.")

with tab_analysis:
    if result:
        analysis = result.get("analysis_output", "")
        if analysis:
            st.markdown(analysis)
        else:
            st.info("No analysis data available.")
    else:
        st.info("Analysis results will appear here after running a task.")

with tab_research:
    if result:
        research = result.get("research_output", "")
        if research:
            st.markdown(research)
            st.caption(f"Sources searched: {result.get('sources_count', 0)}")
        else:
            st.info("No research data available.")
    else:
        st.info("Research findings will appear here after running a task.")

with tab_charts:
    if result:
        chart_paths = result.get("chart_paths", [])
        if chart_paths:
            cols = st.columns(min(len(chart_paths), 2))
            for i, path in enumerate(chart_paths):
                if Path(path).exists():
                    with cols[i % 2]:
                        st.image(path, use_container_width=True)
        else:
            st.info("No charts were generated for this task.")
    else:
        st.info("Charts will appear here after running a task.")

with tab_log:
    if result:
        agent_log = result.get("agent_log", [])
        if agent_log:
            for entry in agent_log:
                ts = entry.get("timestamp", "")[:19]
                agent = entry.get("agent", "")
                preview = entry.get("output_preview", "")[:120]
                st.markdown(f"**`{ts}`** · **{agent}** — {preview}...")
        errors = result.get("errors", [])
        if errors:
            st.error("Errors encountered:")
            for e in errors:
                st.code(e)
    else:
        st.info("Agent activity log will appear here after running a task.")

st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#94a3b8; font-size:0.8rem'>"
    "AI Business Operator · Built with LangGraph, FastAPI, Streamlit · Powered by Google Gemini (Free)"
    "</div>",
    unsafe_allow_html=True,
)
