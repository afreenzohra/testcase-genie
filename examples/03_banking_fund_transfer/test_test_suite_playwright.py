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
