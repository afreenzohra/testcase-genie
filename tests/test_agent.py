"""Unit tests for GeminiAgent and parsing utilities in agent.py."""

from __future__ import annotations

import os
from unittest.mock import MagicMock, patch

import pytest
from google.genai.errors import APIError, ClientError

from testcase_genie.agent import (
    EmptyInputError,
    GeminiAgent,
    GeminiRateLimitError,
    GeminiServiceError,
    JSONParsingError,
    MissingAPIKeyError,
    clean_python_code,
    extract_json_payload,
)


def test_missing_api_key_raises_exception(monkeypatch):
    """Verify MissingAPIKeyError is raised when no API key is provided or found."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    with patch("testcase_genie.agent.load_dotenv"):
        with pytest.raises(MissingAPIKeyError, match="GEMINI_API_KEY is not configured"):
            GeminiAgent(api_key="")


def test_empty_prompt_raises_exception():
    """Verify EmptyInputError is raised when empty prompt is passed."""
    agent = GeminiAgent(api_key="fake-key-for-unit-test")
    with pytest.raises(EmptyInputError):
        agent.generate_content(prompt="   ")


def test_extract_json_payload_direct_json():
    """Verify direct JSON string is parsed correctly."""
    raw = '{"title": "Sample", "count": 5}'
    result = extract_json_payload(raw)
    assert result == {"title": "Sample", "count": 5}


def test_extract_json_payload_markdown_fence():
    """Verify markdown code-fenced JSON is parsed correctly."""
    raw = "```json\n{\n  \"status\": \"success\"\n}\n```"
    result = extract_json_payload(raw)
    assert result == {"status": "success"}


def test_extract_json_payload_with_surrounding_text():
    """Verify JSON embedded within conversational text is extracted."""
    raw = (
        "Sure, here is the generated suite:\n\n"
        "{\n  \"valid\": true,\n  \"name\": \"Test\"\n}\n\n"
        "Hope this helps!"
    )
    result = extract_json_payload(raw)
    assert result == {"valid": True, "name": "Test"}


def test_extract_json_payload_invalid_raises_error():
    """Verify JSONParsingError is raised for non-JSON text."""
    with pytest.raises(JSONParsingError):
        extract_json_payload("This is completely unparseable text with no json.")


def test_clean_python_code_markdown_fence():
    """Verify clean_python_code strips markdown code fences."""
    fenced = "```python\nprint('hello world')\n```"
    assert clean_python_code(fenced) == "print('hello world')"


def test_clean_python_code_raw():
    """Verify clean_python_code preserves raw code without fences."""
    raw = "def test_func():\n    assert True"
    assert clean_python_code(raw) == raw


def test_agent_generate_content_success():
    """Verify generate_content returns text on client success."""
    with patch("google.genai.Client") as mock_client_cls:
        mock_instance = MagicMock()
        mock_client_cls.return_value = mock_instance
        mock_instance.models.generate_content.return_value = MagicMock(text="Generated text response")

        agent = GeminiAgent(api_key="test-api-key")
        result = agent.generate_content("Generate tests")
        assert result == "Generated text response"


def test_agent_rate_limit_error_handling():
    """Verify 429 ClientError triggers GeminiRateLimitError."""
    with patch("google.genai.Client") as mock_client_cls:
        mock_instance = MagicMock()
        mock_client_cls.return_value = mock_instance
        # Mock ClientError with 429 in message
        mock_instance.models.generate_content.side_effect = ClientError(
            429, {"error": {"message": "Resource has been exhausted (e.g. check quota)."}}
        )

        agent = GeminiAgent(api_key="test-api-key", max_retries=0)
        with pytest.raises(GeminiRateLimitError):
            agent.generate_content("Generate tests")
