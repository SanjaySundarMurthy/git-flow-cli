"""Export reporter - JSON, HTML, CSV, and SARIF output."""
import csv
import io
import json

from ..models import FlowReport


def to_dict(report: FlowReport) -> dict:
    return {
        "repo_name": report.repo_name,
        "strategy": report.strategy.value,
        "total_branches": report.total_branches,
        "total_prs": report.total_prs,
        "health_score": report.health_score,
        "grade": report.grade,
        "summary": {
            "critical": report.critical_count,
            "high": report.high_count,
            "medium": report.medium_count,
            "low": report.low_count,
            "info": report.info_count,
        },
        "findings": [
            {
                "rule_id": f.rule_id,
                "title": f.title,
                "severity": f.severity.value,
                "resource_name": f.resource_name,
                "resource_type": f.resource_type,
                "description": f.description,
                "recommendation": f.recommendation,
            }
            for f in report.findings
        ],
    }


def to_json(report: FlowReport) -> str:
    return json.dumps(to_dict(report), indent=2)


def to_csv(report: FlowReport) -> str:
    """Export findings as CSV."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Rule ID", "Severity", "Title",
        "Resource Type", "Resource Name",
        "Description", "Recommendation",
    ])
    for f in report.findings:
        writer.writerow([
            f.rule_id,
            f.severity.value.upper(),
            f.title,
            f.resource_type,
            f.resource_name,
            f.description,
            f.recommendation,
        ])
    return output.getvalue()


def to_sarif(report: FlowReport) -> str:
    """Export findings as SARIF 2.1.0 for GitHub Code Scanning."""
    rules = []
    results = []
    seen_rules: set[str] = set()

    for f in report.findings:
        if f.rule_id not in seen_rules:
            seen_rules.add(f.rule_id)
            level_map = {
                "critical": "error",
                "high": "error",
                "medium": "warning",
                "low": "note",
                "info": "note",
            }
            rules.append({
                "id": f.rule_id,
                "name": f.title,
                "shortDescription": {
                    "text": f.title,
                },
                "fullDescription": {
                    "text": f.description,
                },
                "defaultConfiguration": {
                    "level": level_map.get(
                        f.severity.value, "note"
                    ),
                },
                "helpUri": (
                    "https://github.com/SanjaySundarMurthy"
                    "/git-flow-cli#rules"
                ),
            })

        results.append({
            "ruleId": f.rule_id,
            "message": {
                "text": (
                    f"{f.description}."
                    f" Recommendation: {f.recommendation}"
                ),
            },
            "locations": [{
                "physicalLocation": {
                    "artifactLocation": {
                        "uri": f"{f.resource_type}"
                               f"/{f.resource_name}",
                    },
                },
            }],
        })

    sarif = {
        "version": "2.1.0",
        "$schema": (
            "https://raw.githubusercontent.com/oasis-tcs"
            "/sarif-spec/main/sarif-2.1"
            "/schema/sarif-schema-2.1.0.json"
        ),
        "runs": [{
            "tool": {
                "driver": {
                    "name": "git-flow-cli",
                    "version": "2.0.0",
                    "informationUri": (
                        "https://github.com"
                        "/SanjaySundarMurthy/git-flow-cli"
                    ),
                    "rules": rules,
                },
            },
            "results": results,
        }],
    }
    return json.dumps(sarif, indent=2)


def to_html(report: FlowReport) -> str:
    d = to_dict(report)
    rows = ""
    for f in d["findings"]:
        color = {
            "critical": "#dc3545",
            "high": "#fd7e14",
            "medium": "#ffc107",
            "low": "#17a2b8",
        }.get(f["severity"], "#6c757d")
        rows += (
            f"<tr><td>{f['rule_id']}</td>"
            f'<td style="color:{color};font-weight:bold">'
            f"{f['severity'].upper()}</td>"
            f"<td>{f['resource_type']}"
            f"/{f['resource_name']}</td>"
            f"<td>{f['description']}</td>"
            f"<td>{f['recommendation']}</td></tr>\n"
        )
    return (
        "<!DOCTYPE html>\n"
        "<html><head><title>Git Flow Report</title>\n"
        "<style>"
        "body{font-family:sans-serif;margin:2em}"
        "table{border-collapse:collapse;width:100%}"
        "th,td{border:1px solid #ddd;padding:8px;"
        "text-align:left}"
        "th{background:#f4f4f4}"
        ".score{font-size:2em;font-weight:bold}"
        "</style></head>\n"
        f"<body><h1>Git Flow Analysis Report</h1>\n"
        f"<p><b>Repo:</b> {d['repo_name']}"
        f" | <b>Strategy:</b> {d['strategy']}"
        f" | <b>Score:</b>"
        f" <span class='score'>"
        f"{d['health_score']}/100"
        f" (Grade {d['grade']})</span></p>\n"
        "<table><tr>"
        "<th>Rule</th><th>Severity</th>"
        "<th>Resource</th><th>Issue</th>"
        "<th>Recommendation</th>"
        f"</tr>\n{rows}</table>"
        "</body></html>"
    )
