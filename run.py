"""
run.py — CLI for AI Business Operator

Usage:
    python run.py "Analyze Tesla EV competitors"
    python run.py "Research healthcare AI" --verbose
    python run.py --interactive
    python run.py --schedule "Daily market brief" --time "09:00"
"""
from __future__ import annotations
import sys, argparse, json, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.markdown import Markdown
from loguru import logger

console = Console()

def banner():
    console.print(Panel.fit(
        "[bold blue]🤖 AI Business Operator[/bold blue]\n"
        "[dim]Autonomous Multi-Agent Business Intelligence · Powered by Gemini (Free)[/dim]",
        border_style="blue"))

def run_task(task: str, verbose: bool = False) -> dict:
    from memory.knowledge_base import BusinessOperator
    console.print(f"\n[bold]Task:[/bold] {task}\n")

    agents = ["🗺  Planner","🔍 Research","📊 Analysis","⚙  Code","✍  Content","🧠 Memory"]
    with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
                  BarColumn(), TextColumn("{task.percentage:>3.0f}%"), console=console) as prog:
        p = prog.add_task("Running pipeline...", total=len(agents))
        operator = BusinessOperator(output_dir="./reports")
        result = operator.run(task)
        for ag in agents:
            prog.advance(p); prog.update(p, description=f"[green]{ag} ✓[/green]"); time.sleep(0.05)

    t = Table(title="Results", show_header=True, header_style="bold blue")
    t.add_column("Metric", style="cyan"); t.add_column("Value", style="white")
    t.add_row("Status",    "[green]✅ Completed[/green]")
    t.add_row("Time",      f"{result.get('elapsed_time','—')}s")
    t.add_row("Sources",   str(result.get("sources_count", 0)))
    t.add_row("Words",     str(result.get("word_count", 0)))
    t.add_row("Charts",    str(len(result.get("chart_paths", []))))
    t.add_row("Report",    result.get("report_path", "—"))
    t.add_row("PDF",       result.get("pdf_path", "—") or "—")
    console.print(t)

    if verbose:
        console.print("\n[bold]Report Preview[/bold]")
        rpt = result.get("final_report", "")
        console.print(Markdown(rpt[:2000] + ("..." if len(rpt) > 2000 else "")))

    if result.get("errors"):
        console.print("\n[red]Errors:[/red]")
        for e in result["errors"]: console.print(f"  [red]•[/red] {e}")

    return result

def run_interactive():
    banner()
    console.print("[dim]Type your task and press Enter. 'quit' to exit.\n[/dim]")
    history = []
    while True:
        try:
            task = console.input("[bold blue]Task>[/bold blue] ").strip()
            if task.lower() in ("quit","exit","q"): break
            if not task: continue
            if task == "history":
                [console.print(f"  {i+1}. {h}") for i, h in enumerate(history)]; continue
            run_task(task); history.append(task)
        except KeyboardInterrupt:
            console.print("\n[dim]Interrupted[/dim]")

def schedule_task(task: str, run_time: str):
    import schedule
    console.print(f"[bold]Scheduling[/bold] '{task}' at {run_time} daily")
    schedule.every().day.at(run_time).do(lambda: run_task(task))
    console.print(f"[green]✅ Scheduled. Press Ctrl+C to stop.[/green]")
    while True:
        schedule.run_pending(); time.sleep(30)

def main():
    parser = argparse.ArgumentParser(description="AI Business Operator CLI")
    parser.add_argument("task", nargs="?", help="Business task to run")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--interactive", "-i", action="store_true")
    parser.add_argument("--schedule", "-s", metavar="TASK")
    parser.add_argument("--time", "-t", metavar="HH:MM", default="09:00")
    parser.add_argument("--output", "-o", metavar="FILE")
    args = parser.parse_args()

    banner()
    if args.interactive:          run_interactive()
    elif args.schedule:           schedule_task(args.schedule, args.time)
    elif args.task:
        result = run_task(args.task, verbose=args.verbose)
        if args.output:
            with open(args.output, "w") as f:
                json.dump({k:v for k,v in result.items() if k != "agent_log"}, f, indent=2, default=str)
            console.print(f"\n[green]Saved to {args.output}[/green]")
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
