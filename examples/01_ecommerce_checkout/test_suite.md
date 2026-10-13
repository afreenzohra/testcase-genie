# 🧞 Test Suite: E-Commerce Single-Page Checkout Test Suite

**Application Domain:** E-Commerce & Retail
**Framework:** playwright

## Executive Summary
- **Total Scenarios:** 5
- **Breakdown by Type:** Positive: 2 | Negative: 2 | Edge: 1
- **Breakdown by Priority:** Critical: 1 | High: 3 | Medium: 1 | Low: 0

### Requirement / Feature Description
> Validation of address entry, promo discount calculation, payment gateways, and order placement

## Test Cases Summary Matrix

| ID | Title | Type | Priority | Expected Result |
| :--- | :--- | :---: | :---: | :--- |
| `TC-001` | Successful order placement with saved address and valid Credit Card | POSITIVE | CRITICAL | User redirected to /order-confirmation with unique Order ID and confirmation email sent notification |
| `TC-002` | Apply valid promotional discount code and verify recalculation | POSITIVE | HIGH | Success message 'Promo SAVE20 applied (-$20.00)' displayed; Subtotal unchanged, Discount -$20.00, Total adjusted correctly |
| `TC-003` | Checkout rejected when credit card CVV length is invalid | NEGATIVE | HIGH | Inline field validation error 'CVV must be 3 or 4 digits' displayed; Order is not submitted and payment gateway is not contacted |
| `TC-004` | Expired promo code displays inline error without resetting cart | NEGATIVE | MEDIUM | Alert message 'Promo code has expired' displayed; Total remains unchanged and all entered address details remain intact |
| `TC-005` | Inventory depletion during checkout payment processing | EDGE | HIGH | Order fails gracefully with alert 'Item is no longer in stock'; Payment is not charged; User returned to cart with item flagged |

## Detailed Test Specifications

### TC-001: Successful order placement with saved address and valid Credit Card
- **Type:** `positive`
- **Priority:** `critical`

**Preconditions:**
- User is logged in as registered customer
- Cart contains 2 in-stock items ($85 total)
- User has at least 1 saved valid shipping address

**Execution Steps:**
1. Navigate to cart page and click 'Proceed to Checkout'
2. Select default shipping address from address radio group
3. Select 'Credit Card' as payment method
4. Enter valid Visa card number, expiration date, and CVV
5. Click 'Place Order' button

**Expected Outcome:**
User redirected to /order-confirmation with unique Order ID and confirmation email sent notification

---

### TC-002: Apply valid promotional discount code and verify recalculation
- **Type:** `positive`
- **Priority:** `high`

**Preconditions:**
- User is on checkout page with items totaling $100
- Promo code 'SAVE20' is active in promotion system

**Execution Steps:**
1. Enter 'SAVE20' into Promo Code text input
2. Click 'Apply' button
3. Observe Order Summary totals breakdown

**Expected Outcome:**
Success message 'Promo SAVE20 applied (-$20.00)' displayed; Subtotal unchanged, Discount -$20.00, Total adjusted correctly

---

### TC-003: Checkout rejected when credit card CVV length is invalid
- **Type:** `negative`
- **Priority:** `high`

**Preconditions:**
- User is on checkout payment section

**Execution Steps:**
1. Select 'Credit Card'
2. Enter valid 16-digit card number and future expiration date
3. Enter '1' (single digit) into CVV field
4. Click 'Place Order'

**Expected Outcome:**
Inline field validation error 'CVV must be 3 or 4 digits' displayed; Order is not submitted and payment gateway is not contacted

---

### TC-004: Expired promo code displays inline error without resetting cart
- **Type:** `negative`
- **Priority:** `medium`

**Preconditions:**
- Promo code 'SUMMER2025' is marked expired in backend

**Execution Steps:**
1. Enter 'SUMMER2025' into Promo Code input
2. Click 'Apply'

**Expected Outcome:**
Alert message 'Promo code has expired' displayed; Total remains unchanged and all entered address details remain intact

---

### TC-005: Inventory depletion during checkout payment processing
- **Type:** `edge`
- **Priority:** `high`

**Preconditions:**
- Cart contains 1 item with remaining inventory count = 1

**Execution Steps:**
1. User fills checkout details and clicks 'Place Order'
2. Concurrent shopper completes purchase of the last stock item 100ms earlier

**Expected Outcome:**
Order fails gracefully with alert 'Item is no longer in stock'; Payment is not charged; User returned to cart with item flagged

---

## Starter Automation Code

```python
import pytest
from playwright.sync_api import Page, expect

class CheckoutPage:
    """Page Object Model encapsulating the E-Commerce Checkout interface."""
    def __init__(self, page: Page):
        self.page = page
        self.saved_address_radio = page.locator("input[name='shipping_address']").first  # TODO: Define locator for address selector
        self.payment_cc_radio = page.locator("input[value='credit_card']")  # TODO: Define locator for Credit Card radio
        self.cc_number_input = page.locator("#cc-number")  # TODO: Define locator for CC number input
        self.cc_expiry_input = page.locator("#cc-exp")  # TODO: Define locator for CC expiry input
        self.cc_cvv_input = page.locator("#cc-cvv")  # TODO: Define locator for CC CVV input
        self.promo_code_input = page.locator("#promo-code")  # TODO: Define locator for Promo code input
        self.apply_promo_btn = page.locator("button#apply-promo")  # TODO: Define locator for Apply Promo button
        self.place_order_btn = page.locator("button#place-order")  # TODO: Define locator for Place Order button
        self.order_confirmation_header = page.locator("h1.order-confirmed")  # TODO: Define locator for confirmation header
        self.inline_cvv_error = page.locator(".error-cvv")  # TODO: Define locator for CVV inline error
        self.promo_error_alert = page.locator(".alert-promo-error")  # TODO: Define locator for Promo error alert
        self.out_of_stock_banner = page.locator(".alert-out-of-stock")  # TODO: Define locator for out-of-stock banner

    def select_saved_address(self):
        self.saved_address_radio.check()

    def fill_credit_card(self, number: str, exp: str, cvv: str):
        self.payment_cc_radio.check()
        self.cc_number_input.fill(number)
        self.cc_expiry_input.fill(exp)
        self.cc_cvv_input.fill(cvv)

    def apply_promo(self, code: str):
        self.promo_code_input.fill(code)
        self.apply_promo_btn.click()

    def submit_order(self):
        self.place_order_btn.click()


@pytest.fixture
def checkout_page(page: Page) -> CheckoutPage:
    page.goto("https://example.com/checkout")
    return CheckoutPage(page)


def test_tc_001_successful_order_placement(checkout_page: CheckoutPage):
    """TC-001: Successful order placement with saved address and valid Credit Card."""
    checkout_page.select_saved_address()
    checkout_page.fill_credit_card("4111111111111111", "12/28", "123")
    checkout_page.submit_order()
    expect(checkout_page.order_confirmation_header).to_be_visible()


def test_tc_002_apply_valid_promo_code(checkout_page: CheckoutPage):
    """TC-002: Apply valid promotional discount code and verify recalculation."""
    checkout_page.apply_promo("SAVE20")
    expect(checkout_page.page.locator(".discount-badge")).to_contain_text("-$20.00")


def test_tc_003_checkout_rejected_invalid_cvv(checkout_page: CheckoutPage):
    """TC-003: Checkout rejected when credit card CVV length is invalid."""
    checkout_page.fill_credit_card("4111111111111111", "12/28", "1")
    checkout_page.submit_order()
    expect(checkout_page.inline_cvv_error).to_be_visible()


def test_tc_004_expired_promo_displays_error(checkout_page: CheckoutPage):
    """TC-004: Expired promo code displays inline error without resetting cart."""
    checkout_page.apply_promo("SUMMER2025")
    expect(checkout_page.promo_error_alert).to_be_visible()


def test_tc_005_inventory_depletion_handling(checkout_page: CheckoutPage):
    """TC-005: Inventory depletion during checkout payment processing."""
    checkout_page.select_saved_address()
    checkout_page.fill_credit_card("4111111111111111", "12/28", "123")
    checkout_page.submit_order()
    expect(checkout_page.out_of_stock_banner).to_be_visible()
```
