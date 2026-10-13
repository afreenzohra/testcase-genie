# 🧞 Test Suite: Banking Fund Transfer & Idempotency Test Suite

**Application Domain:** Banking & FinTech
**Framework:** playwright

## Executive Summary
- **Total Scenarios:** 5
- **Breakdown by Type:** Positive: 1 | Negative: 2 | Edge: 2
- **Breakdown by Priority:** Critical: 2 | High: 2 | Medium: 1 | Low: 0

### Requirement / Feature Description
> Validation of account balance rules, daily velocity limits, idempotency guards, and ledger reflection

## Test Cases Summary Matrix

| ID | Title | Type | Priority | Expected Result |
| :--- | :--- | :---: | :---: | :--- |
| `TC-001` | Successful domestic fund transfer within available balance and daily limit | POSITIVE | CRITICAL | Transfer confirmation modal displays Transaction Reference #; Checking balance updates to $1,999.50 ($500 + $0.50 fee); status 'Completed' |
| `TC-002` | Transfer rejected when amount exceeds available account balance | NEGATIVE | HIGH | Validation error 'Insufficient funds for this transfer including $0.50 transaction fee'; Transfer blocked before debit |
| `TC-003` | Transfer rejected when cumulative 24-hour limit exceeds $5,000 | NEGATIVE | HIGH | Error alert 'Daily transfer limit exceeded. Remaining allowance for today: $500.00'; Transfer rejected |
| `TC-004` | Idempotency key prevents duplicate debit on rapid double-click | EDGE | CRITICAL | Exactly ONE debit of $200.50 occurs in ledger; second request returns identical cached confirmation payload without duplicate debit |
| `TC-005` | Boundary value zero and negative amount rejection in UI input | EDGE | MEDIUM | Input field enforces minimum value > $0.01; 'Confirm Transfer' button remains disabled or alerts 'Amount must be greater than 0' |

## Detailed Test Specifications

### TC-001: Successful domestic fund transfer within available balance and daily limit
- **Type:** `positive`
- **Priority:** `critical`

**Preconditions:**
- Customer has Checking Account #1001 with available balance $2,500.00
- Daily transferred amount today is $0.00
- Beneficiary Account #9988 is registered and active

**Execution Steps:**
1. Navigate to /transfers/new
2. Select Source Account 'Checking #1001'
3. Select Beneficiary 'Bob Smith (#9988)'
4. Enter Amount '500.00'
5. Click 'Confirm Transfer'

**Expected Outcome:**
Transfer confirmation modal displays Transaction Reference #; Checking balance updates to $1,999.50 ($500 + $0.50 fee); status 'Completed'

---

### TC-002: Transfer rejected when amount exceeds available account balance
- **Type:** `negative`
- **Priority:** `high`

**Preconditions:**
- Checking balance is $100.00

**Execution Steps:**
1. Select Checking #1001
2. Enter Amount '150.00'
3. Click 'Confirm Transfer'

**Expected Outcome:**
Validation error 'Insufficient funds for this transfer including $0.50 transaction fee'; Transfer blocked before debit

---

### TC-003: Transfer rejected when cumulative 24-hour limit exceeds $5,000
- **Type:** `negative`
- **Priority:** `high`

**Preconditions:**
- Checking balance is $10,000.00
- Customer has already transferred $4,500.00 within past 24 hours

**Execution Steps:**
1. Enter Amount '600.00'
2. Click 'Confirm Transfer'

**Expected Outcome:**
Error alert 'Daily transfer limit exceeded. Remaining allowance for today: $500.00'; Transfer rejected

---

### TC-004: Idempotency key prevents duplicate debit on rapid double-click
- **Type:** `edge`
- **Priority:** `critical`

**Preconditions:**
- Checking balance is $1,000.00
- User fills valid transfer form for $200.00

**Execution Steps:**
1. Simulate double-click or simultaneous duplicate HTTP POST request with identical Idempotency-Key
2. Inspect backend transaction ledger for Checking #1001

**Expected Outcome:**
Exactly ONE debit of $200.50 occurs in ledger; second request returns identical cached confirmation payload without duplicate debit

---

### TC-005: Boundary value zero and negative amount rejection in UI input
- **Type:** `edge`
- **Priority:** `medium`

**Preconditions:**
- User is on transfer screen

**Execution Steps:**
1. Attempt to input '0.00' and click Confirm
2. Attempt to input '-50.00' and click Confirm

**Expected Outcome:**
Input field enforces minimum value > $0.01; 'Confirm Transfer' button remains disabled or alerts 'Amount must be greater than 0'

---

## Starter Automation Code

```python
import pytest
from playwright.sync_api import Page, expect


class TransferPage:
    """Page Object Model for Banking Fund Transfer interface."""

    def __init__(self, page: Page):
        self.page = page
        self.source_account_select = page.locator("select#source-account")  # TODO: Define locator for source account dropdown
        self.beneficiary_select = page.locator("select#beneficiary-account")  # TODO: Define locator for beneficiary selector
        self.amount_input = page.locator("input#transfer-amount")  # TODO: Define locator for transfer amount input
        self.confirm_btn = page.locator("button#btn-confirm-transfer")  # TODO: Define locator for confirm transfer button
        self.tx_modal_success = page.locator(".modal-tx-success")  # TODO: Define locator for success confirmation modal
        self.insufficient_funds_alert = page.locator(".alert-insufficient-funds")  # TODO: Define locator for insufficient funds alert
        self.daily_limit_alert = page.locator(".alert-daily-limit")  # TODO: Define locator for daily limit alert
        self.account_balance_display = page.locator("#balance-display")  # TODO: Define locator for account balance display

    def execute_transfer(self, source_acc: str, beneficiary: str, amount: str):
        self.source_account_select.select_option(label=source_acc)
        self.beneficiary_select.select_option(label=beneficiary)
        self.amount_input.fill(amount)
        self.confirm_btn.click()


@pytest.fixture
def transfer_page(page: Page) -> TransferPage:
    page.goto("https://banking.example.com/transfers/new")
    return TransferPage(page)


def test_tc_001_successful_fund_transfer(transfer_page: TransferPage):
    """TC-001: Successful domestic fund transfer within available balance and daily limit."""
    transfer_page.execute_transfer("Checking #1001", "Bob Smith (#9988)", "500.00")
    expect(transfer_page.tx_modal_success).to_be_visible()
    expect(transfer_page.account_balance_display).to_contain_text("1,999.50")


def test_tc_002_insufficient_funds_rejected(transfer_page: TransferPage):
    """TC-002: Transfer rejected when amount exceeds available account balance."""
    transfer_page.execute_transfer("Checking #1001", "Bob Smith (#9988)", "150.00")
    expect(transfer_page.insufficient_funds_alert).to_be_visible()


def test_tc_003_daily_limit_exceeded(transfer_page: TransferPage):
    """TC-003: Transfer rejected when cumulative 24-hour limit exceeds $5,000."""
    transfer_page.execute_transfer("Checking #1001", "Bob Smith (#9988)", "600.00")
    expect(transfer_page.daily_limit_alert).to_be_visible()


def test_tc_004_idempotency_prevents_duplicate_debit(transfer_page: TransferPage):
    """TC-004: Idempotency key prevents duplicate debit on rapid double-click."""
    transfer_page.source_account_select.select_option(label="Checking #1001")
    transfer_page.beneficiary_select.select_option(label="Bob Smith (#9988)")
    transfer_page.amount_input.fill("200.00")
    # Simulate double-click
    transfer_page.confirm_btn.dblclick()
    expect(transfer_page.tx_modal_success).to_be_visible()


def test_tc_005_zero_and_negative_amount_blocked(transfer_page: TransferPage):
    """TC-005: Boundary value zero and negative amount rejection in UI input."""
    transfer_page.amount_input.fill("0.00")
    expect(transfer_page.confirm_btn).to_be_disabled()
```
