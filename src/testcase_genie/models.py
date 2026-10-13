"""Pydantic data models and schemas for TestCase-Genie."""

from __future__ import annotations

from enum import Enum
from typing import List, Optional, Union
from pydantic import BaseModel, Field, field_validator


class TestCaseType(str, Enum):
    """Categorization of test case behavior."""
    POSITIVE = "positive"
    NEGATIVE = "negative"
    EDGE = "edge"


class PriorityLevel(str, Enum):
    """Execution priority of a test case."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    CRITICAL = "critical"


class FrameworkType(str, Enum):
    """Supported test automation frameworks."""
    SELENIUM = "selenium"
    PLAYWRIGHT = "playwright"


class TestCase(BaseModel):
    """Schema representing an individual structured QA test case."""

    id: str = Field(
        ...,
        description="Unique identifier for the test case, e.g. TC-001",
        examples=["TC-001"],
    )
    title: str = Field(
        ...,
        description="Concise descriptive title of the test scenario",
        examples=["Successful login with valid credentials"],
    )
    type: TestCaseType = Field(
        ...,
        description="Type of test: positive, negative, or edge",
    )
    preconditions: List[str] = Field(
        default_factory=list,
        description="Prerequisites or state required before running steps",
    )
    steps: List[str] = Field(
        ...,
        description="Numbered or sequential steps to execute the test",
    )
    expected_result: str = Field(
        ...,
        description="Expected behavior or observable outcome of the test",
    )
    priority: PriorityLevel = Field(
        default=PriorityLevel.MEDIUM,
        description="Priority of execution: critical, high, medium, low",
    )

    @field_validator("type", mode="before")
    @classmethod
    def normalize_type(cls, v: Union[str, TestCaseType]) -> TestCaseType:
        if isinstance(v, TestCaseType):
            return v
        if isinstance(v, str):
            val = v.strip().lower()
            if "edge" in val:
                return TestCaseType.EDGE
            if "neg" in val:
                return TestCaseType.NEGATIVE
            if "pos" in val:
                return TestCaseType.POSITIVE
        return TestCaseType(v)

    @field_validator("priority", mode="before")
    @classmethod
    def normalize_priority(cls, v: Union[str, PriorityLevel]) -> PriorityLevel:
        if isinstance(v, PriorityLevel):
            return v
        if isinstance(v, str):
            val = v.strip().lower()
            for p in PriorityLevel:
                if p.value in val:
                    return p
            return PriorityLevel.MEDIUM
        return PriorityLevel(v)

    @field_validator("preconditions", mode="before")
    @classmethod
    def normalize_preconditions(cls, v: Union[str, List[str], None]) -> List[str]:
        if v is None:
            return []
        if isinstance(v, str):
            lines = [line.strip().lstrip("-*1234567890. ") for line in v.splitlines() if line.strip()]
            return lines if lines else [v.strip()]
        if isinstance(v, list):
            return [str(item).strip() for item in v if str(item).strip()]
        return []

    @field_validator("steps", mode="before")
    @classmethod
    def normalize_steps(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str):
            lines = [line.strip() for line in v.splitlines() if line.strip()]
            return lines if lines else [v.strip()]
        if isinstance(v, list):
            return [str(item).strip() for item in v if str(item).strip()]
        return []


class TestCaseSuite(BaseModel):
    """Collection of generated test cases and metadata for a user story."""

    title: str = Field(
        default="Generated Test Suite",
        description="Title of the feature or user story tested",
    )
    description: str = Field(
        default="",
        description="Summary or raw description of the requirement",
    )
    app_type: Optional[str] = Field(
        default=None,
        description="Application domain (e.g. e-commerce, login, banking)",
    )
    test_cases: List[TestCase] = Field(
        default_factory=list,
        description="List of structured test cases",
    )
    generated_code: Optional[str] = Field(
        default=None,
        description="Starter automation code in Selenium or Playwright",
    )
    framework: Optional[FrameworkType] = Field(
        default=None,
        description="Target automation framework used for code generation",
    )


class GenerationConfig(BaseModel):
    """Configuration options supplied by the user for generation."""

    framework: FrameworkType = Field(
        default=FrameworkType.PLAYWRIGHT,
        description="Target framework: selenium or playwright",
    )
    test_count: int = Field(
        default=5,
        ge=1,
        le=30,
        description="Target number of test cases to generate",
    )
    app_type: Optional[str] = Field(
        default=None,
        description="Application domain hint (e.g. e-commerce, auth, banking)",
    )
