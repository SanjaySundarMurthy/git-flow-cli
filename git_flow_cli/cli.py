"""CLI entry point for git-flow-cli."""
import sys

import click
import yaml
from rich.console import Console
from rich.table import Table

from . import __version__
from .analyzers.flow_analyzer import analyze_flow
from .demo import get_demo_repo_config
from .models import GIT_RULES
from .parser import parse_repo_config
from .reporters.export_reporter import (
    to_csv,
    to_html,
    to_json,
    to_sarif,
)
from .reporters.terminal_reporter import print_report

console = Console()

FORMAT_CHOICES = ["terminal", "json", "html", "csv", "sarif"]
SEVERITY_ORDER = ["critical", "high", "medium", "low"]


@click.group()
@click.version_option(
    version=__version__,
    prog_name="git-flow-cli",
)
def cli():
    """🌿 git-flow-cli - Branch strategy enforcer and PR health checker."""
    pass


@cli.command()
@click.argument("config_file", type=click.Path(exists=True))
@click.option(
    "--format", "fmt",
    type=click.Choice(FORMAT_CHOICES),
    default="terminal",
    help="Output format",
)
@click.option(
    "--fail-on",
    type=click.Choice(SEVERITY_ORDER),
    default=None,
    help="Exit code 1 if findings at severity or above",
)
@click.option(
    "--output", "-o",
    type=click.Path(),
    default=None,
    help="Save report to file",
)
def audit(config_file, fmt, fail_on, output):
    """Audit repository config against branching best practices."""
    with open(config_file, "r") as f:
        content = f.read()
    config = parse_repo_config(content)
    report = analyze_flow(config)
    _output_report(report, fmt, output)
    _check_fail_on(report, fail_on)


@cli.command()
@click.option(
    "--format", "fmt",
    type=click.Choice(FORMAT_CHOICES),
    default="terminal",
)
def demo(fmt):
    """Run demo with sample repository configuration."""
    content = get_demo_repo_config()
    config = parse_repo_config(content)
    report = analyze_flow(config)
    _output_report(report, fmt, None)


@cli.command()
def rules():
    """List all 15 git flow validation rules."""
    table = Table(
        title="Git Flow Validation Rules (15 Rules)",
        show_lines=True,
    )
    table.add_column("Rule ID", style="bold", width=10)
    table.add_column("Severity", width=10)
    table.add_column("Title", width=35)
    table.add_column("Description", width=50)
    for rule_id, rule in GIT_RULES.items():
        sev = rule["severity"].value
        color = {
            "critical": "red bold", "high": "red",
            "medium": "yellow", "low": "cyan",
        }.get(sev, "white")
        table.add_row(
            rule_id,
            f"[{color}]{sev.upper()}[/]",
            rule["title"],
            rule["description"],
        )
    console.print(table)


@cli.command()
@click.argument(
    "path", type=click.Path(exists=True), default="."
)
@click.option(
    "--format", "fmt",
    type=click.Choice(FORMAT_CHOICES),
    default="terminal",
)
@click.option(
    "--fail-on",
    type=click.Choice(SEVERITY_ORDER),
    default=None,
)
@click.option("--output", "-o", type=click.Path(), default=None)
def scan(path, fmt, fail_on, output):
    """Scan a local git repository for best practices."""
    from .scanners.git_scanner import scan_local_repo

    try:
        config = scan_local_repo(path)
    except ValueError as e:
        console.print(f"[red]Error: {e}[/]")
        sys.exit(1)

    report = analyze_flow(config)
    _output_report(report, fmt, output)
    _check_fail_on(report, fail_on)


@cli.command()
@click.argument("owner_repo")
@click.option(
    "--token", "-t",
    envvar="GITHUB_TOKEN",
    default=None,
    help="GitHub personal access token",
)
@click.option(
    "--format", "fmt",
    type=click.Choice(FORMAT_CHOICES),
    default="terminal",
)
@click.option(
    "--fail-on",
    type=click.Choice(SEVERITY_ORDER),
    default=None,
)
@click.option("--output", "-o", type=click.Path(), default=None)
def github(owner_repo, token, fmt, fail_on, output):
    """Audit a GitHub repository via API (owner/repo)."""
    from .scanners.github_scanner import scan_github_repo

    try:
        config = scan_github_repo(owner_repo, token)
    except (ValueError, RuntimeError) as e:
        console.print(f"[red]Error: {e}[/]")
        sys.exit(1)

    report = analyze_flow(config)
    _output_report(report, fmt, output)
    _check_fail_on(report, fail_on)


@cli.command()
@click.argument("config_file", type=click.Path(exists=True))
def validate(config_file):
    """Validate a config file against the schema."""
    from .validators.schema_validator import validate_file

    valid, errors = validate_file(config_file)
    if valid:
        console.print(
            f"[green]✅ {config_file} is valid![/]"
        )
    else:
        console.print(
            f"[red]❌ {config_file} has errors:[/]"
        )
        for err in errors:
            console.print(f"  [red]• {err}[/]")
        sys.exit(1)


@cli.command()
@click.option(
    "--output", "-o",
    type=click.Path(),
    default="repo-config.yaml",
    help="Output file path",
)
@click.option(
    "--strategy",
    type=click.Choice([
        "gitflow", "github_flow",
        "trunk_based", "release_flow",
    ]),
    default="gitflow",
)
def init(output, strategy):
    """Generate a starter configuration file."""
    config = {
        "name": "my-repository",
        "default_branch": "main",
        "strategy": strategy,
        "required_approvals": 2,
        "enforce_linear_history": False,
        "require_conventional_commits": False,
        "max_pr_size": 500,
        "max_pr_age_days": 14,
        "branch_naming_pattern": (
            "^(feature|bugfix|hotfix|release)/[a-z0-9-]+$"
        ),
        "required_labels": [],
        "branches": [
            {
                "name": "main",
                "is_protected": True,
                "last_commit_age_days": 0,
            },
            {
                "name": "develop",
                "is_protected": True,
                "last_commit_age_days": 1,
            },
        ],
        "pull_requests": [],
    }
    content = yaml.dump(
        config, default_flow_style=False, sort_keys=False
    )
    with open(output, "w") as f:
        f.write(content)
    console.print(
        f"[green]✅ Config generated: {output}[/]"
    )


def _output_report(report, fmt, output):
    """Route report to the correct formatter."""
    formatters = {
        "json": to_json,
        "html": to_html,
        "csv": to_csv,
        "sarif": to_sarif,
    }
    if fmt in formatters:
        result = formatters[fmt](report)
        if output:
            with open(output, "w") as f:
                f.write(result)
            console.print(
                f"[green]Report saved to {output}[/]"
            )
        else:
            console.print(result)
    else:
        print_report(report, console)


def _check_fail_on(report, fail_on):
    """Exit with code 1 if findings meet threshold."""
    if not fail_on:
        return
    threshold = SEVERITY_ORDER.index(fail_on)
    for finding in report.findings:
        idx = SEVERITY_ORDER.index(finding.severity.value)
        if idx <= threshold:
            sys.exit(1)


if __name__ == "__main__":
    cli()
