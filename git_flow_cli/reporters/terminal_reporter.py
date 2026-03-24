"""Rich terminal reporter for git flow analysis."""
from typing import Optional

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ..models import FlowReport, Severity

SEVERITY_COLORS = {
    Severity.CRITICAL: "red bold",
    Severity.HIGH: "red",
    Severity.MEDIUM: "yellow",
    Severity.LOW: "cyan",
    Severity.INFO: "dim",
}

SEVERITY_ICONS = {
    Severity.CRITICAL: "🔴",
    Severity.HIGH: "🟠",
    Severity.MEDIUM: "🟡",
    Severity.LOW: "🔵",
    Severity.INFO: "⚪",
}


def print_report(
    report: FlowReport, console: Optional[Console] = None
):
    console = console or Console()
    grade_color = {
        "A": "green", "B": "blue", "C": "yellow",
        "D": "red", "F": "red bold",
    }.get(report.grade, "white")

    findings_summary = (
        f"🔴 {report.critical_count}"
        f" 🟠 {report.high_count}"
        f" 🟡 {report.medium_count}"
        f" 🔵 {report.low_count}"
        f" ⚪ {report.info_count}"
    )

    console.print(Panel(
        f"[bold]Repository:[/] {report.repo_name}\n"
        f"[bold]Strategy:[/] {report.strategy.value}\n"
        f"[bold]Branches:[/] {report.total_branches}"
        f" | [bold]PRs:[/] {report.total_prs}\n"
        f"[bold]Health Score:[/]"
        f" [{grade_color}]"
        f"{report.health_score:.1f}/100"
        f" (Grade {report.grade})[/]\n"
        f"[bold]Findings:[/] {len(report.findings)}"
        f" ({findings_summary})",
        title="🌿 Git Flow Analysis Report",
        border_style=grade_color,
    ))

    if not report.findings:
        console.print(
            "[green]✅ Repository follows best practices![/]"
        )
        return

    table = Table(title="Findings", show_lines=True)
    table.add_column("Rule", style="bold", width=10)
    table.add_column("Severity", width=10)
    table.add_column("Resource", width=25)
    table.add_column("Issue", width=45)
    table.add_column("Recommendation", width=40)

    for f in report.findings:
        sev_style = SEVERITY_COLORS.get(f.severity, "white")
        icon = SEVERITY_ICONS.get(f.severity, "")
        table.add_row(
            f.rule_id,
            f"[{sev_style}]{icon}"
            f" {f.severity.value.upper()}[/]",
            f"{f.resource_type}/{f.resource_name}",
            f.description,
            f.recommendation,
        )
    console.print(table)
