"""Unit tests for Pydantic models in models.py."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from testcase_genie.models import (
    FrameworkType,
    GenerationConfig,
    PriorityLevel,
    TestCase,
    TestCaseSuite,
    TestCaseType,
)


def test_test_case_valid_instantiation(sample_test_case_dict):
    """Verify TestCase instantiates correctly with full valid data."""
    tc = TestCase.model_validate(sample_test_case_dict)
    assert tc.id == "TC-001"
    assert tc.type == TestCaseType.POSITIVE
    assert tc.priority == PriorityLevel.HIGH
    assert len(tc.steps) == 4
    assert len(tc.preconditions) == 2


def test_test_case_type_normalization():
    """Verify tolerant normalization of test case types."""
    tc_pos = TestCase(
        id="TC-1",
        title="Title",
        type="Positive scenario",
        steps=["Step 1"],
        expected_result="Success",
    )
    assert tc_pos.type == TestCaseType.POSITIVE

    tc_neg = TestCase(
        id="TC-2",
        title="Title",
        type="Negative check",
        steps=["Step 1"],
        expected_result="Fail",
    )
    assert tc_neg.type == TestCaseType.NEGATIVE

    tc_edge = TestCase(
        id="TC-3",
        title="Title",
        type="Boundary / Edge",
        steps=["Step 1"],
        expected_result="Boundary",
    )
    assert tc_edge.type == TestCaseType.EDGE


def test_test_case_priority_normalization():
    """Verify tolerant normalization of priorities."""
    tc = TestCase(
        id="TC-1",
        title="Title",
        type=TestCaseType.POSITIVE,
        steps=["Step 1"],
        expected_result="Success",
        priority="CRITICAL_BLOCKER",
    )
    assert tc.priority == PriorityLevel.CRITICAL

    tc_default = TestCase(
        id="TC-2",
        title="Title",
        type=TestCaseType.POSITIVE,
        steps=["Step 1"],
        expected_result="Success",
        priority="unknown_priority_value",
    )
    assert tc_default.priority == PriorityLevel.MEDIUM


def test_test_case_steps_multiline_string_normalization():
    """Verify multiline string steps are split into a clean list."""
    tc = TestCase(
        id="TC-1",
        title="Title",
        type=TestCaseType.POSITIVE,
        steps="Step 1: Go to url\nStep 2: Click login\nStep 3: Submit",
        expected_result="Success",
    )
    assert len(tc.steps) == 3
    assert tc.steps[0] == "Step 1: Go to url"


def test_test_case_preconditions_string_normalization():
    """Verify preconditions string is split into clean items."""
    tc = TestCase(
        id="TC-1",
        title="Title",
        type=TestCaseType.POSITIVE,
        steps=["Step 1"],
        expected_result="Success",
        preconditions="1. User is registered\n2. User is on homepage",
    )
    assert len(tc.preconditions) == 2
    assert tc.preconditions[0] == "User is registered"


def test_test_case_missing_required_fields():
    """Verify ValidationError when mandatory fields are absent."""
    with pytest.raises(ValidationError):
        TestCase.model_validate({"id": "TC-001"})


def test_test_case_suite_validation(sample_suite_dict):
    """Verify TestCaseSuite validation and serialization."""
    suite = TestCaseSuite.model_validate(sample_suite_dict)
    assert len(suite.test_cases) == 3
    assert suite.title == "E-Commerce Checkout Suite"
    json_data = suite.model_dump_json()
    assert "TC-001" in json_data


def test_generation_config_defaults_and_limits():
    """Verify GenerationConfig defaults and boundary validation."""
    cfg = GenerationConfig()
    assert cfg.framework == FrameworkType.PLAYWRIGHT
    assert cfg.test_count == 5
    assert cfg.app_type is None

    # Test count validation limits
    with pytest.raises(ValidationError):
        GenerationConfig(test_count=0)

    with pytest.raises(ValidationError):
        GenerationConfig(test_count=50)
