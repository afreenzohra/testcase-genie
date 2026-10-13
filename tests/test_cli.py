"""Unit tests for the Typer CLI in cli.py."""

from __future__ import annotations

from unittest.mock import MagicMock, patch
from typer.testing import CliRunner

from testcase_genie.agent import MissingAPIKeyError
from testcase_genie.cli import app
from testcase_genie.models import TestCaseSuite

runner = CliRunner()


def test_cli_help():
    """Verify CLI --help runs cleanly and outputs commands and options."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Generate structured QA test cases" in result.output
    assert "--framework" in result.output
    assert "--count" in result.output


def test_cli_version():
    """Verify CLI --version prints current package version."""
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "TestCase-Genie version" in result.output


def test_cli_missing_api_key(monkeypatch):
    """Verify friendly error panel is rendered when GEMINI_API_KEY is missing."""
    with patch("testcase_genie.cli.GeminiAgent") as mock_agent_cls:
        mock_agent_cls.side_effect = MissingAPIKeyError("GEMINI_API_KEY is not configured.")
        result = runner.invoke(app, ["As a user I want to log in"])
        assert result.exit_code == 1
        assert "API Key Error" in result.output or "Authentication Missing" in result.output


def test_cli_successful_generation(sample_test_suite: TestCaseSuite):
    """Verify CLI prints summary table on successful generation."""
    with patch("testcase_genie.cli.GeminiAgent"):
        with patch("testcase_genie.cli.TestCaseGenerator") as mock_gen_cls:
            mock_gen_instance = MagicMock()
            mock_gen_cls.return_value = mock_gen_instance
            mock_gen_instance.generate.return_value = sample_test_suite

            result = runner.invoke(
                app,
                [
                    "As a user I want to checkout",
                    "--framework", "playwright",
                    "--count", "3",
                ],
            )
            assert result.exit_code == 0
            assert "Successfully generated 3 test cases" in result.output
            assert "TC-001" in result.output


def test_cli_file_input(sample_test_suite: TestCaseSuite, tmp_path):
    """Verify CLI correctly reads user story from a file."""
    story_file = tmp_path / "user_story.md"
    story_file.write_text("As an admin, I want to manage roles.", encoding="utf-8")

    with patch("testcase_genie.cli.GeminiAgent"):
        with patch("testcase_genie.cli.TestCaseGenerator") as mock_gen_cls:
            mock_gen_instance = MagicMock()
            mock_gen_cls.return_value = mock_gen_instance
            mock_gen_instance.generate.return_value = sample_test_suite

            result = runner.invoke(app, ["--file", str(story_file)])
            assert result.exit_code == 0
            assert "Successfully generated 3 test cases" in result.output


def test_cli_export_directory(sample_test_suite: TestCaseSuite, tmp_path):
    """Verify CLI creates output files when --output-dir is passed."""
    out_dir = tmp_path / "cli_exports"

    with patch("testcase_genie.cli.GeminiAgent"):
        with patch("testcase_genie.cli.TestCaseGenerator") as mock_gen_cls:
            mock_gen_instance = MagicMock()
            mock_gen_cls.return_value = mock_gen_instance
            mock_gen_instance.generate.return_value = sample_test_suite

            result = runner.invoke(
                app,
                [
                    "As a user I want to checkout",
                    "--output-dir", str(out_dir),
                ],
            )
            assert result.exit_code == 0
            assert "Exported assets to directory" in result.output
            assert out_dir.exists()
