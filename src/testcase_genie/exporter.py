"""Export utilities for test suites: Markdown, JSON, CSV, and Python automation code."""

from __future__ import annotations

import csv
import io
import json
from pathlib import Path
from typing import Dict, Union

from testcase_genie.models import TestCaseSuite


def suite_to_json(suite: TestCaseSuite, indent: int = 2) -> str:
    """Serialize TestCaseSuite to a formatted JSON string."""
    return suite.model_dump_json(indent=indent)


def suite_to_csv(suite: TestCaseSuite) -> str:
    """Serialize test cases in the suite to RFC 4180 compliant CSV format."""
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_ALL)

    # Header
    writer.writerow([
        "ID",
        "Title",
        "Type",
        "Priority",
        "Preconditions",
        "Steps",
        "Expected Result",
    ])

    for tc in suite.test_cases:
        preconditions_str = "; ".join(tc.preconditions) if tc.preconditions else "None"
        steps_str = "\n".join(f"{i+1}. {step}" for i, step in enumerate(tc.steps))
        writer.writerow([
            tc.id,
            tc.title,
            tc.type.value if hasattr(tc.type, "value") else str(tc.type),
            tc.priority.value if hasattr(tc.priority, "value") else str(tc.priority),
            preconditions_str,
            steps_str,
            tc.expected_result,
        ])

    return output.getvalue()


def suite_to_markdown(suite: TestCaseSuite) -> str:
    """Format TestCaseSuite as a structured, human-readable Markdown report."""
    total = len(suite.test_cases)
    pos_count = sum(1 for tc in suite.test_cases if (tc.type.value if hasattr(tc.type, "value") else str(tc.type)) == "positive")
    neg_count = sum(1 for tc in suite.test_cases if (tc.type.value if hasattr(tc.type, "value") else str(tc.type)) == "negative")
    edge_count = sum(1 for tc in suite.test_cases if (tc.type.value if hasattr(tc.type, "value") else str(tc.type)) == "edge")

    crit_count = sum(1 for tc in suite.test_cases if (tc.priority.value if hasattr(tc.priority, "value") else str(tc.priority)) == "critical")
    high_count = sum(1 for tc in suite.test_cases if (tc.priority.value if hasattr(tc.priority, "value") else str(tc.priority)) == "high")
    med_count = sum(1 for tc in suite.test_cases if (tc.priority.value if hasattr(tc.priority, "value") else str(tc.priority)) == "medium")
    low_count = sum(1 for tc in suite.test_cases if (tc.priority.value if hasattr(tc.priority, "value") else str(tc.priority)) == "low")

    lines = [
        f"# 🧞 Test Suite: {suite.title}",
        "",
        f"**Application Domain:** {suite.app_type or 'General'}",
        f"**Framework:** {suite.framework.value if suite.framework else 'Not specified'}",
        "",
        "## Executive Summary",
        f"- **Total Scenarios:** {total}",
        f"- **Breakdown by Type:** Positive: {pos_count} | Negative: {neg_count} | Edge: {edge_count}",
        f"- **Breakdown by Priority:** Critical: {crit_count} | High: {high_count} | Medium: {med_count} | Low: {low_count}",
        "",
        "### Requirement / Feature Description",
        "> " + suite.description.replace("\n", "\n> "),
        "",
        "## Test Cases Summary Matrix",
        "",
        "| ID | Title | Type | Priority | Expected Result |",
        "| :--- | :--- | :---: | :---: | :--- |",
    ]

    for tc in suite.test_cases:
        t_val = tc.type.value if hasattr(tc.type, "value") else str(tc.type)
        p_val = tc.priority.value if hasattr(tc.priority, "value") else str(tc.priority)
        clean_exp = tc.expected_result.replace("|", "\\|").replace("\n", " ")
        lines.append(f"| `{tc.id}` | {tc.title} | {t_val.upper()} | {p_val.upper()} | {clean_exp} |")

    lines.append("")
    lines.append("## Detailed Test Specifications")
    lines.append("")

    for tc in suite.test_cases:
        t_val = tc.type.value if hasattr(tc.type, "value") else str(tc.type)
        p_val = tc.priority.value if hasattr(tc.priority, "value") else str(tc.priority)
        lines.append(f"### {tc.id}: {tc.title}")
        lines.append(f"- **Type:** `{t_val}`")
        lines.append(f"- **Priority:** `{p_val}`")
        lines.append("")
        lines.append("**Preconditions:**")
        if tc.preconditions:
            for pre in tc.preconditions:
                lines.append(f"- {pre}")
        else:
            lines.append("- None")
        lines.append("")
        lines.append("**Execution Steps:**")
        for i, step in enumerate(tc.steps, 1):
            lines.append(f"{i}. {step}")
        lines.append("")
        lines.append(f"**Expected Outcome:**\n{tc.expected_result}")
        lines.append("")
        lines.append("---")
        lines.append("")

    if suite.generated_code:
        framework_name = suite.framework.value if suite.framework else "python"
        lines.append("## Starter Automation Code")
        lines.append("")
        lines.append(f"```python\n{suite.generated_code.strip()}\n```")
        lines.append("")

    return "\n".join(lines)


def export_suite_to_files(
    suite: TestCaseSuite,
    output_dir: Union[Path, str],
    base_name: str = "test_suite",
) -> Dict[str, Path]:
    """Export the test suite to JSON, Markdown, CSV, and Python files.
    
    Args:
        suite: The TestCaseSuite to export.
        output_dir: Directory where files should be written.
        base_name: Base filename prefix for exported files.
        
    Returns:
        Dictionary mapping format name ('json', 'md', 'csv', 'py') to written Path.
    """
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    results: Dict[str, Path] = {}

    # JSON export
    json_path = out_path / f"{base_name}.json"
    json_path.write_text(suite_to_json(suite), encoding="utf-8")
    results["json"] = json_path

    # Markdown export
    md_path = out_path / f"{base_name}.md"
    md_path.write_text(suite_to_markdown(suite), encoding="utf-8")
    results["md"] = md_path

    # CSV export
    csv_path = out_path / f"{base_name}.csv"
    csv_path.write_text(suite_to_csv(suite), encoding="utf-8")
    results["csv"] = csv_path

    # Python starter code export (if present)
    if suite.generated_code:
        framework_tag = suite.framework.value if suite.framework else "automation"
        py_path = out_path / f"test_{base_name}_{framework_tag}.py"
        py_path.write_text(suite.generated_code, encoding="utf-8")
        results["py"] = py_path

    return results
