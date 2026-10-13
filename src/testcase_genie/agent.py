"""Gemini client wrapper with error handling, rate limiting, and retry mechanisms."""

from __future__ import annotations

import json
import os
import re
import time
from typing import Any, Dict, Optional

from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError, ClientError


class TestCaseGenieError(Exception):
    """Base exception for TestCase-Genie."""
    pass


class MissingAPIKeyError(TestCaseGenieError):
    """Raised when GEMINI_API_KEY is not configured."""
    pass


class EmptyInputError(TestCaseGenieError):
    """Raised when user story or input text is empty or invalid."""
    pass


class GeminiRateLimitError(TestCaseGenieError):
    """Raised when Gemini API encounters a rate limit (HTTP 429)."""
    pass


class GeminiServiceError(TestCaseGenieError):
    """Raised when Gemini API encounters a server or network failure."""
    pass


class JSONParsingError(TestCaseGenieError):
    """Raised when the model output cannot be parsed into the expected JSON schema."""
    pass


def extract_json_payload(raw_text: str) -> Dict[str, Any]:
    """Extract and parse a JSON dictionary from raw model output.
    
    Handles markdown code fences, leading commentary, and trailing text.
    """
    if not raw_text or not raw_text.strip():
        raise JSONParsingError("Received empty response from the model.")

    cleaned = raw_text.strip()

    # Try 1: Direct JSON parsing
    try:
        data = json.loads(cleaned)
        if isinstance(data, dict):
            return data
    except json.JSONDecodeError:
        pass

    # Try 2: Extract from markdown code fence (```json ... ``` or ``` ...)
    fence_pattern = r"```(?:json)?\s*([\s\S]*?)\s*```"
    matches = re.findall(fence_pattern, cleaned)
    for match in matches:
        try:
            data = json.loads(match.strip())
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            continue

    # Try 3: Find outermost curly braces { ... }
    first_brace = cleaned.find("{")
    last_brace = cleaned.rfind("}")
    if first_brace != -1 and last_brace != -1 and last_brace > first_brace:
        candidate = cleaned[first_brace : last_brace + 1]
        try:
            data = json.loads(candidate)
            if isinstance(data, dict):
                return data
        except json.JSONDecodeError:
            pass

    raise JSONParsingError(f"Failed to extract valid JSON object from model output:\n{raw_text[:300]}...")


def clean_python_code(raw_code: str) -> str:
    """Extract Python code from markdown fences if present."""
    if not raw_code:
        return ""
    cleaned = raw_code.strip()
    fence_pattern = r"```(?:python)?\s*([\s\S]*?)\s*```"
    matches = re.findall(fence_pattern, cleaned)
    if matches:
        return matches[0].strip()
    return cleaned


class GeminiAgent:
    """Wrapper around the Google GenAI SDK for TestCase-Genie."""

    DEFAULT_MODEL = "gemini-3.8-flash"

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: Optional[str] = None,
        max_retries: int = 3,
    ) -> None:
        """Initialize the Gemini client.
        
        Args:
            api_key: Optional API key. If omitted, loaded from GEMINI_API_KEY in .env/env.
            model: Optional model name. If omitted, loaded from GEMINI_MODEL or defaults.
            max_retries: Number of automatic retries on transient errors.
        """
        load_dotenv()
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key or not self.api_key.strip():
            raise MissingAPIKeyError(
                "GEMINI_API_KEY is not configured. "
                "Please add GEMINI_API_KEY to your .env file or environment variables."
            )

        self.model = model or os.getenv("GEMINI_MODEL") or self.DEFAULT_MODEL
        self.max_retries = max_retries
        self.client = genai.Client(api_key=self.api_key)

    def generate_content(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: float = 0.2,
    ) -> str:
        """Send a prompt to Gemini with exponential backoff on transient errors.
        
        Args:
            prompt: User/task prompt.
            system_instruction: Persona/role system instruction.
            temperature: Sampling temperature (0.0 to 1.0).
            
        Returns:
            Raw text response from the model.
        """
        if not prompt or not prompt.strip():
            raise EmptyInputError("Prompt cannot be empty.")

        config = types.GenerateContentConfig(
            temperature=temperature,
            system_instruction=system_instruction if system_instruction else None,
        )

        attempts = 0
        backoff = 3.0

        while attempts <= self.max_retries:
            try:
                response = self.client.models.generate_content(
                    model=self.model,
                    contents=prompt,
                    config=config,
                )
                if not response.text:
                    raise GeminiServiceError("Model returned an empty response.")
                return response.text

            except ClientError as ce:
                # HTTP 429 or ResourceExhausted
                error_msg = str(ce).lower()
                if "429" in error_msg or "resource_exhausted" in error_msg or "quota" in error_msg:
                    if attempts < self.max_retries:
                        attempts += 1
                        time.sleep(backoff)
                        backoff *= 2
                        continue
                    raise GeminiRateLimitError(
                        f"Gemini API rate limit exceeded: {ce}"
                    ) from ce
                raise GeminiServiceError(f"Gemini ClientError: {ce}") from ce

            except APIError as ae:
                if attempts < self.max_retries:
                    attempts += 1
                    time.sleep(backoff)
                    backoff *= 2
                    continue
                raise GeminiServiceError(f"Gemini API error: {ae}") from ae

            except Exception as e:
                raise GeminiServiceError(f"Unexpected error communicating with Gemini: {e}") from e

        raise GeminiServiceError("Max retries exceeded while calling Gemini.")
