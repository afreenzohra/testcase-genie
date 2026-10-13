"""Orchestration pipeline for test case generation and POM automation code generation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from pydantic import ValidationError

from testcase_genie.agent import (
    EmptyInputError,
    GeminiAgent,
    JSONParsingError,
    clean_python_code,
    extract_json_payload,
)
from testcase_genie.models import FrameworkType, GenerationConfig, TestCaseSuite


def get_prompts_dir() -> Path:
    """Resolve the prompts directory location reliably."""
    # Try 1: Relative to package source root (src/testcase_genie -> repo root / prompts)
    pkg_root = Path(__file__).resolve().parent.parent.parent / "prompts"
    if pkg_root.exists() and pkg_root.is_dir():
        return pkg_root

    # Try 2: Current working directory / prompts
    cwd_prompts = Path.cwd() / "prompts"
    if cwd_prompts.exists() and cwd_prompts.is_dir():
        return cwd_prompts

    # Fallback: parent of current working directory
    parent_prompts = Path.cwd().parent / "prompts"
    if parent_prompts.exists() and parent_prompts.is_dir():
        return parent_prompts

    raise FileNotFoundError(f"Could not locate prompts directory. Checked: {pkg_root}, {cwd_prompts}")


def load_prompt_file(filename: str) -> str:
    """Read a prompt file by name from the prompts directory."""
    prompts_dir = get_prompts_dir()
    filepath = prompts_dir / filename
    if not filepath.exists():
        raise FileNotFoundError(f"Prompt file not found at: {filepath}")
    return filepath.read_text(encoding="utf-8")


class TestCaseGenerator:
    """Generates structured test cases and Page Object Model automation code."""
    __test__ = False

    def __init__(self, agent: Optional[GeminiAgent] = None) -> None:
        """Initialize with an optional GeminiAgent instance."""
        self.agent = agent or GeminiAgent()
        self.system_prompt = load_prompt_file("system_prompt.txt")
        self.test_gen_template = load_prompt_file("test_case_generation.txt")
        self.code_gen_template = load_prompt_file("code_generation.txt")

    def generate_test_cases(
        self,
        user_story: str,
        config: Optional[GenerationConfig] = None,
    ) -> TestCaseSuite:
        """Generate structured test cases from a user story.
        
        Args:
            user_story: The user story or feature specification text.
            config: Generation options (test count, app type, framework).
            
        Returns:
            Validated TestCaseSuite instance.
        """
        if not user_story or not user_story.strip():
            raise EmptyInputError("User story or feature description cannot be empty.")

        clean_story = user_story.strip()
        cfg = config or GenerationConfig()
        app_type_str = cfg.app_type.strip() if cfg.app_type else "General Web/API Application"

        prompt = (
            self.test_gen_template.replace("{app_type}", app_type_str)
            .replace("{test_count}", str(cfg.test_count))
            .replace("{user_story}", clean_story)
        )

        # First attempt
        raw_output = self.agent.generate_content(
            prompt=prompt,
            system_instruction=self.system_prompt,
            temperature=0.2,
        )

        try:
            payload = extract_json_payload(raw_output)
            suite = TestCaseSuite.model_validate(payload)
            if not suite.description:
                suite.description = clean_story
            if not suite.app_type:
                suite.app_type = cfg.app_type
            return suite
        except (JSONParsingError, ValidationError) as first_err:
            # Auto-retry once with repair prompt
            repair_prompt = (
                f"{prompt}\n\n"
                f"CRITICAL FIX REQUIRED: The previous attempt failed validation with error:\n"
                f"{str(first_err)}\n\n"
                f"You MUST return strictly valid JSON matching the exact schema without any markdown formatting or comments."
            )

            retry_output = self.agent.generate_content(
                prompt=repair_prompt,
                system_instruction=self.system_prompt,
                temperature=0.1,
            )

            try:
                payload = extract_json_payload(retry_output)
                suite = TestCaseSuite.model_validate(payload)
                if not suite.description:
                    suite.description = clean_story
                if not suite.app_type:
                    suite.app_type = cfg.app_type
                return suite
            except (JSONParsingError, ValidationError) as second_err:
                raise JSONParsingError(
                    f"Model failed to generate valid JSON test suite after retry. Error: {second_err}"
                ) from second_err

    def generate_automation_code(
        self,
        suite: TestCaseSuite,
        user_story: str,
        framework: FrameworkType = FrameworkType.PLAYWRIGHT,
    ) -> str:
        """Generate Page Object Model test automation code in Python.
        
        Args:
            suite: The generated TestCaseSuite.
            user_story: Original user story for context.
            framework: Target framework (selenium or playwright).
            
        Returns:
            Python starter automation code with POM and locator placeholders.
        """
        if not suite.test_cases:
            raise EmptyInputError("Cannot generate automation code for an empty test suite.")

        test_cases_dict = [tc.model_dump() for tc in suite.test_cases]
        test_cases_json = json.dumps(test_cases_dict, indent=2)

        prompt = (
            self.code_gen_template.replace("{framework}", framework.value)
            .replace("{user_story}", user_story.strip())
            .replace("{test_cases_json}", test_cases_json)
        )

        raw_code = self.agent.generate_content(
            prompt=prompt,
            system_instruction=self.system_prompt,
            temperature=0.2,
        )

        return clean_python_code(raw_code)

    def generate(
        self,
        user_story: str,
        config: Optional[GenerationConfig] = None,
    ) -> TestCaseSuite:
        """End-to-end generation of test cases and automation code.
        
        Args:
            user_story: Feature requirement or user story.
            config: Generation configuration options.
            
        Returns:
            TestCaseSuite with both test_cases and generated_code populated.
        """
        cfg = config or GenerationConfig()
        suite = self.generate_test_cases(user_story=user_story, config=cfg)
        code = self.generate_automation_code(
            suite=suite,
            user_story=user_story,
            framework=cfg.framework,
        )
        suite.generated_code = code
        suite.framework = cfg.framework
        return suite
