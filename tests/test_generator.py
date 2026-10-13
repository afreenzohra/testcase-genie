"""Unit tests for prompt loading and generator orchestration in generator.py."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from testcase_genie.agent import EmptyInputError, GeminiAgent, JSONParsingError
from testcase_genie.generator import (
    TestCaseGenerator,
    get_prompts_dir,
    load_prompt_file,
)
from testcase_genie.models import FrameworkType, GenerationConfig, TestCaseSuite


def test_prompt_file_loading():
    """Verify prompt files are found and loaded without errors."""
    prompts_dir = get_prompts_dir()
    assert prompts_dir.exists()
    assert (prompts_dir / "system_prompt.txt").exists()
    assert (prompts_dir / "test_case_generation.txt").exists()
    assert (prompts_dir / "code_generation.txt").exists()

    sys_prompt = load_prompt_file("system_prompt.txt")
    assert "Staff QA Architect" in sys_prompt


def test_generator_empty_input_raises_error():
    """Verify EmptyInputError when empty user story is provided."""
    mock_agent = MagicMock(spec=GeminiAgent)
    generator = TestCaseGenerator(agent=mock_agent)

    with pytest.raises(EmptyInputError):
        generator.generate_test_cases(user_story="   ")


def test_generator_successful_test_cases(sample_user_story, mock_gemini_json_response):
    """Verify test cases generated and validated from mock model response."""
    mock_agent = MagicMock(spec=GeminiAgent)
    mock_agent.generate_content.return_value = mock_gemini_json_response

    generator = TestCaseGenerator(agent=mock_agent)
    cfg = GenerationConfig(test_count=3, app_type="E-Commerce")

    suite = generator.generate_test_cases(sample_user_story, config=cfg)
    assert isinstance(suite, TestCaseSuite)
    assert len(suite.test_cases) == 3
    assert suite.test_cases[0].id == "TC-001"
    assert suite.test_cases[0].type.value == "positive"
    assert mock_agent.generate_content.call_count == 1


def test_generator_auto_retry_on_invalid_json(sample_user_story, mock_gemini_json_response):
    """Verify automatic 1-retry repair flow when initial response is invalid JSON."""
    mock_agent = MagicMock(spec=GeminiAgent)
    # First response is malformed, second response is valid JSON
    mock_agent.generate_content.side_effect = [
        "Oops, this is broken invalid json { not valid }",
        mock_gemini_json_response,
    ]

    generator = TestCaseGenerator(agent=mock_agent)
    suite = generator.generate_test_cases(sample_user_story)

    assert isinstance(suite, TestCaseSuite)
    assert len(suite.test_cases) == 3
    # Exactly 2 calls: initial attempt + 1 repair retry
    assert mock_agent.generate_content.call_count == 2


def test_generator_fails_after_retry(sample_user_story):
    """Verify JSONParsingError is raised if retry attempt also fails."""
    mock_agent = MagicMock(spec=GeminiAgent)
    mock_agent.generate_content.side_effect = [
        "Broken attempt 1",
        "Still broken attempt 2",
    ]

    generator = TestCaseGenerator(agent=mock_agent)
    with pytest.raises(JSONParsingError):
        generator.generate_test_cases(sample_user_story)

    assert mock_agent.generate_content.call_count == 2


def test_generator_automation_code_generation(sample_user_story, sample_test_suite, mock_gemini_code_response):
    """Verify automation code generation and cleaning."""
    mock_agent = MagicMock(spec=GeminiAgent)
    mock_agent.generate_content.return_value = mock_gemini_code_response

    generator = TestCaseGenerator(agent=mock_agent)
    code = generator.generate_automation_code(
        suite=sample_test_suite,
        user_story=sample_user_story,
        framework=FrameworkType.PLAYWRIGHT,
    )

    assert "import pytest" in code
    assert "class LoginPage" in code
    assert "```" not in code  # Verified markdown fence stripped


def test_generator_end_to_end_generate(
    sample_user_story,
    mock_gemini_json_response,
    mock_gemini_code_response,
):
    """Verify end-to-end generate() creates both test cases and automation code."""
    mock_agent = MagicMock(spec=GeminiAgent)
    mock_agent.generate_content.side_effect = [
        mock_gemini_json_response,
        mock_gemini_code_response,
    ]

    generator = TestCaseGenerator(agent=mock_agent)
    cfg = GenerationConfig(framework=FrameworkType.SELENIUM)
    suite = generator.generate(sample_user_story, config=cfg)

    assert isinstance(suite, TestCaseSuite)
    assert len(suite.test_cases) == 3
    assert suite.framework == FrameworkType.SELENIUM
    assert suite.generated_code is not None
    assert "class LoginPage" in suite.generated_code
