"""Unit tests for exporter utilities in exporter.py."""

from __future__ import annotations

import csv
import json

from testcase_genie.exporter import (
    export_suite_to_files,
    suite_to_csv,
    suite_to_json,
    suite_to_markdown,
)
from testcase_genie.models import TestCaseSuite


def test_suite_to_json(sample_test_suite: TestCaseSuite):
    """Verify JSON export produces valid JSON string loadable by standard parser."""
    json_output = suite_to_json(sample_test_suite)
    parsed = json.loads(json_output)
    assert parsed["title"] == "E-Commerce Checkout Suite"
    assert len(parsed["test_cases"]) == 3
    assert parsed["test_cases"][0]["id"] == "TC-001"


def test_suite_to_csv(sample_test_suite: TestCaseSuite):
    """Verify CSV export produces RFC 4180 compliant CSV table."""
    csv_output = suite_to_csv(sample_test_suite)
    reader = csv.reader(csv_output.splitlines())
    rows = list(reader)

    # Header check
    assert rows[0] == ["ID", "Title", "Type", "Priority", "Preconditions", "Steps", "Expected Result"]
    # Data rows check
    assert len(rows) == 4  # Header + 3 test cases
    assert rows[1][0] == "TC-001"
    assert rows[1][2] == "positive"
    assert "1. Navigate to cart" in rows[1][5]


def test_suite_to_markdown(sample_test_suite: TestCaseSuite):
    """Verify Markdown export contains executive summary, tables, and details."""
    md_output = suite_to_markdown(sample_test_suite)

    assert "# 🧞 Test Suite: E-Commerce Checkout Suite" in md_output
    assert "## Executive Summary" in md_output
    assert "## Test Cases Summary Matrix" in md_output
    assert "| `TC-001` | Successful checkout with valid credit card" in md_output
    assert "## Detailed Test Specifications" in md_output
    assert "### TC-001: Successful checkout with valid credit card" in md_output
    assert "## Starter Automation Code" in md_output
    assert "class CheckoutPage" in md_output


def test_export_suite_to_files(sample_test_suite: TestCaseSuite, tmp_path):
    """Verify all expected asset files are written to destination folder."""
    dest_dir = tmp_path / "exports"
    results = export_suite_to_files(sample_test_suite, output_dir=dest_dir, base_name="checkout_test")

    assert "json" in results
    assert "md" in results
    assert "csv" in results
    assert "py" in results

    assert results["json"].exists()
    assert results["md"].exists()
    assert results["csv"].exists()
    assert results["py"].exists()

    # Verify content in created files
    assert "E-Commerce Checkout Suite" in results["json"].read_text(encoding="utf-8")
    assert "TC-001" in results["csv"].read_text(encoding="utf-8")
    assert "class CheckoutPage" in results["py"].read_text(encoding="utf-8")
