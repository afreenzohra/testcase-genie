"""Pytest shared fixtures and mock data for TestCase-Genie tests."""

from __future__ import annotations

import json
from typing import Any, Dict
import pytest

from testcase_genie.models import (
    FrameworkType,
    PriorityLevel,
    TestCase,
    TestCaseSuite,
    TestCaseType,
)


@pytest.fixture
def sample_user_story() -> str:
    return (
        "As a registered shopper, I want to add items to my cart and complete checkout "
        "using a credit card so that I receive an order confirmation number."
    )


@pytest.fixture
def sample_test_case_dict() -> Dict[str, Any]:
    return {
        "id": "TC-001",
        "title": "Successful checkout with valid credit card",
        "type": "positive",
        "preconditions": ["User is logged in", "Item is in cart"],
        "steps": [
            "Navigate to cart",
            "Click Checkout",
            "Enter valid credit card details",
            "Click Place Order",
        ],
        "expected_result": "Order confirmation number displayed with success message",
        "priority": "high",
    }


@pytest.fixture
def sample_suite_dict(sample_test_case_dict) -> Dict[str, Any]:
    return {
        "title": "E-Commerce Checkout Suite",
        "description": "Validation of payment and checkout workflows",
        "app_type": "E-Commerce",
        "test_cases": [
            sample_test_case_dict,
            {
                "id": "TC-002",
                "title": "Checkout rejected when credit card is expired",
                "type": "negative",
                "preconditions": ["Item is in cart"],
                "steps": [
                    "Proceed to checkout",
                    "Enter expired card date",
                    "Click Place Order",
                ],
                "expected_result": "Error alert 'Card expired' displayed; order not submitted",
                "priority": "high",
            },
            {
                "id": "TC-003",
                "title": "Simultaneous checkout when last inventory item is bought",
                "type": "edge",
                "preconditions": ["Stock count is 1"],
                "steps": [
                    "User A submits order",
                    "User B submits order concurrently",
                ],
                "expected_result": "One order succeeds, second user receives out-of-stock notification",
                "priority": "medium",
            },
        ],
    }


@pytest.fixture
def sample_test_case(sample_test_case_dict) -> TestCase:
    return TestCase.model_validate(sample_test_case_dict)


@pytest.fixture
def sample_test_suite(sample_suite_dict) -> TestCaseSuite:
    suite = TestCaseSuite.model_validate(sample_suite_dict)
    suite.framework = FrameworkType.PLAYWRIGHT
    suite.generated_code = (
        "# Sample Playwright Automation\n"
        "import pytest\n"
        "from playwright.sync_api import Page, expect\n\n"
        "class CheckoutPage:\n"
        "    def __init__(self, page: Page):\n"
        "        self.page = page\n"
        "        self.pay_btn = page.locator('#pay')  # TODO: Define locator for pay button\n\n"
        "def test_tc_001_checkout(page: Page):\n"
        "    checkout = CheckoutPage(page)\n"
        "    assert checkout is not None\n"
    )
    return suite


@pytest.fixture
def mock_gemini_json_response(sample_suite_dict) -> str:
    return json.dumps(sample_suite_dict)


@pytest.fixture
def mock_gemini_code_response() -> str:
    return (
        "```python\n"
        "import pytest\n"
        "from playwright.sync_api import Page\n\n"
        "class LoginPage:\n"
        "    def __init__(self, page: Page):\n"
        "        self.page = page\n"
        "        self.username = page.locator('#username')  # TODO: Define locator for username\n\n"
        "def test_tc_001_login(page: Page):\n"
        "    login = LoginPage(page)\n"
        "    assert login is not None\n"
        "```"
    )
