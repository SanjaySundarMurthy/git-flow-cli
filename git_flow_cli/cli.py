"""CLI entry point for git-flow-cli."""
import sys
import click
from rich.console import Console
from rich.table import Table
from .models import GIT_RULES
from .parser import parse_repo_config
from .analyzers.flow_analyzer import analyze_flow
from .reporters.terminal_reporter import print_report
from .reporters.export_reporter import to_json, to_html
from .demo import get_demo_repo_config

console = Console()


@click.group()
def cli():
    """🌿 git-flow-cli — Branch strategy enforcer and PR health checker."""
    pass


@cli.command()
@click.argument("config_file", type=click.Path(exists=True))
@click.option("--format", "fmt", type=click.Choice(["terminal", "json", "html"]), default="terminal")
@click.option("--fail-on", type=click.Choice(["critical", "high", "medium", "low"]), default=None)
@click.option("--output", "-o", type=click.Path(), default=None)
def audit(config_file, fmt, fail_on, output):
    """Audit repository against branching best practices."""
    with open(config_file, "r") as f:
        content = f.read()
    config = parse_repo_config(content)
    report = analyze_flow(config)
    _output_report(report, fmt, output)
    if fail_on:
        severity_order = ["critical", "high", "medium", "low"]
        threshold = severity_order.index(fail_on)
        for finding in report.findings:
            if severity_order.index(finding.severity.value) <= threshold:
                sys.exit(1)


@cli.command()
@click.option("--format", "fmt", type=click.Choice(["terminal", "json", "html"]), default="terminal")
def demo(fmt):
    """Run demo with sample repository configuration."""
    content = get_demo_repo_config()
    config = parse_repo_config(content)
    report = analyze_flow(config)
    _output_report(report, fmt, None)


@cli.command()
def rules():
    """List all git flow validation rules."""
    table = Table(title="Git Flow Validation Rules", show_lines=True)
    table.add_column("Rule ID", style="bold", width=10)
    table.add_column("Severity", width=10)
    table.add_column("Title", width=35)
    table.add_column("Description", width=50)
    for rule_id, rule in GIT_RULES.items():
        color = {"critical": "red bold", "high": "red", "medium": "yellow", "low": "cyan"}.get(rule["severity"].value, "white")
        table.add_row(rule_id, f"[{color}]{rule['severity'].value.upper()}[/]", rule["title"], rule["description"])
    console.print(table)


def _output_report(report, fmt, output):
    if fmt == "json":
        result = to_json(report)
        if output:
            with open(output, "w") as f:
                f.write(result)
            console.print(f"[green]Report saved to {output}[/]")
        else:
            console.print(result)
    elif fmt == "html":
        result = to_html(report)
        if output:
            with open(output, "w") as f:
                f.write(result)
            console.print(f"[green]Report saved to {output}[/]")
        else:
            console.print(result)
    else:
        print_report(report, console)


if __name__ == "__main__":
    cli()
