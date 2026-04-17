"""
run.py — Command-line interface for AI Business Operator

Usage:
    python run.py "Analyze Tesla EV competitors"
    python run.py "Research healthcare AI startups" --mode research
    python run.py --interactive
    python run.py --schedule "Daily market report" --cron "09:00"
"""
from __future__ import annotations
import sys
import argparse
import json
import time
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich.table import Table
from rich.markdown import Markdown
from rich import print as rprint
from loguru import logger

console = Console()


def print_banner():
    console.print(Panel.fit(
        "[bold blue]🤖 AI Business Operator[/bold blue]\n"
        "[dim]Autonomous Multi-Agent Business Intelligence System[/dim]",
        border_style="blue",
    ))


def run_task(task: str, verbose: bool = False) -> dict:
    """Run a single task through the agent pipeline."""
    from memory.knowledge_base import BusinessOperator

    console.print(f"\n[bold]Task:[/bold] {task}\n")

    agents = ["🗺  Planner", "🔍 Research", "📊 Analysis", "⚙  Code", "✍  Content", "🧠 Memory"]
    result = {}

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        console=console,
    ) as progress:
        task_progress = progress.add_task("Running agent pipeline...", total=len(agents))

        # Since the pipeline is synchronous, we run it and update progress after
        def on_complete(agent_name):
            progress.advance(task_progress)
            progress.update(task_progress, description=f"[green]{agent_name} complete[/green]")

        operator = BusinessOperator(output_dir="./reports")

        # Patch to show progress (simple approach)
        start = time.time()
        result = operator.run(task)
        elapsed = time.time() - start

        for agent in agents:
            on_complete(agent)
            time.sleep(0.05)

    # Results table
    table = Table(title="Pipeline Results", show_header=True, header_style="bold blue")
    table.add_column("Metric", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Status", "[green]✅ Completed[/green]")
    table.add_row("Time elapsed", f"{result.get('elapsed_time', '—')}s")
    table.add_row("Sources found", str(result.get("sources_count", 0)))
    table.add_row("Report words", str(result.get("word_count", 0)))
    table.add_row("Charts generated", str(len(result.get("chart_paths", []))))
    table.add_row("Report saved", result.get("report_path", "—"))
    table.add_row("PDF saved", result.get("pdf_path", "—") or "—")

    console.print(table)

    if verbose:
        console.print("\n[bold]--- Report Preview ---[/bold]")
        report = result.get("final_report", "")
        console.print(Markdown(report[:2000] + ("..." if len(report) > 2000 else "")))

    errors = result.get("errors", [])
    if errors:
        console.print("\n[red]Errors:[/red]")
        for e in errors:
            console.print(f"  [red]•[/red] {e}")

    return result


def run_interactive():
    """Interactive REPL mode."""
    print_banner()
    console.print("[dim]Type your business task and press Enter. Type 'quit' to exit.\n[/dim]")

    history = []
    while True:
        try:
            task = console.input("[bold blue]Task>[/bold blue] ").strip()
            if task.lower() in ("quit", "exit", "q"):
                console.print("[dim]Goodbye![/dim]")
                break
            if not task:
                continue
            if task.lower() == "history":
                for i, h in enumerate(history, 1):
                    console.print(f"  {i}. {h}")
                continue
            if task.lower() == "help":
                console.print("Commands: history, quit, help")
                console.print("Or just type any business task!")
                continue

            result = run_task(task)
            history.append(task)

        except KeyboardInterrupt:
            console.print("\n[dim]Interrupted. Type 'quit' to exit.[/dim]")


def schedule_task(task: str, run_time: str):
    """Schedule a recurring task."""
    try:
        import schedule

        console.print(f"[bold]Scheduling:[/bold] '{task}' at {run_time} daily")

        def job():
            console.print(f"\n[dim]{datetime.now().isoformat()}[/dim] Running scheduled task...")
            run_task(task)

        schedule.every().day.at(run_time).do(job)
        console.print(f"[green]✅ Task scheduled. Running at {run_time} every day.[/green]")
        console.print("[dim]Press Ctrl+C to stop.[/dim]")

        while True:
            schedule.run_pending()
            time.sleep(30)

    except ImportError:
        console.print("[red]Error: schedule package not installed. Run: pip install schedule[/red]")


def main():
    parser = argparse.ArgumentParser(
        description="AI Business Operator — Autonomous multi-agent business intelligence",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py "Analyze Tesla EV competitors"
  python run.py "Research healthcare AI startups" --verbose
  python run.py --interactive
  python run.py --schedule "Morning market report" --time "09:00"
        """,
    )
    parser.add_argument("task", nargs="?", help="Business task to run")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show full report in terminal")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive REPL mode")
    parser.add_argument("--schedule", "-s", metavar="TASK", help="Schedule a recurring task")
    parser.add_argument("--time", "-t", metavar="HH:MM", default="09:00", help="Time for scheduled task (default: 09:00)")
    parser.add_argument("--output", "-o", metavar="FILE", help="Save result JSON to file")

    args = parser.parse_args()

    print_banner()

    if args.interactive:
        run_interactive()
    elif args.schedule:
        schedule_task(args.schedule, args.time)
    elif args.task:
        result = run_task(args.task, verbose=args.verbose)
        if args.output:
            with open(args.output, "w") as f:
                # Remove non-serializable content
                out = {k: v for k, v in result.items() if k != "agent_log"}
                json.dump(out, f, indent=2, default=str)
            console.print(f"\n[green]Result saved to {args.output}[/green]")
    else:
        parser.print_help()
        console.print("\n[dim]Tip: Use --interactive for REPL mode[/dim]")


if __name__ == "__main__":
    main()
