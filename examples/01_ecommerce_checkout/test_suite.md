# 🧞 Test Suite: Single-Page Checkout with Multi-Payment and Promo Code Test Suite

**Application Domain:** E-Commerce & Retail
**Framework:** playwright

## Executive Summary
- **Total Scenarios:** 5
- **Breakdown by Type:** Positive: 2 | Negative: 2 | Edge: 1
- **Breakdown by Priority:** Critical: 2 | High: 2 | Medium: 1 | Low: 0

### Requirement / Feature Description
> Validation suite covering single-page checkout flows including payment processing, promo code calculation, address validation, and inventory hold edge cases.

## Test Cases Summary Matrix

| ID | Title | Type | Priority | Expected Result |
| :--- | :--- | :---: | :---: | :--- |
| `TC-001` | Successful order placement with saved address, valid promo code, and Credit Card payment | POSITIVE | CRITICAL | Order is placed successfully. User is redirected to the Order Confirmation screen displaying a unique order reference number, estimated delivery date, order summary, and a background trigger dispatching the confirmation email. |
| `TC-002` | Successful checkout with new international address and PayPal payment method | POSITIVE | HIGH | PayPal payment processes successfully, the user sees the confirmation page with order reference and estimated delivery date, and order confirmation email is queued. |
| `TC-003` | Invalid postal code format and expired promo code inline error handling without cart loss | NEGATIVE | HIGH | Inline validation error 'Invalid ZIP code format for United States (expected 12345 or 12345-6789)' appears under the postal field. An inline error 'Promo code EXPIRED2020 has expired' appears under the promo field. Cart contents, items, quantities, and subtotal remain intact and unaffected. |
| `TC-004` | Payment gateway failure retains user on checkout and holds item reservation for 10 minutes | NEGATIVE | CRITICAL | User remains on the single-page checkout with an actionable error banner ('Payment authorization failed. Please check your card details or select an alternative payment method.'). Cart and checkout fields remain pre-populated. The item's stock reservation is held for the original user and is unavailable to other shoppers during the 10-minute hold window. |
| `TC-005` | Boundary validation for Credit Card Luhn algorithm and CVV character lengths | EDGE | MEDIUM | Luhn-failing card triggers immediate inline error 'Invalid card number'. The CVV field strictly enforces 3 digits for Visa/Mastercard and 4 digits for American Express, disallowing submission if CVV is under the minimum or truncating/blocking input exceeding the maximum length. |

## Detailed Test Specifications

### TC-001: Successful order placement with saved address, valid promo code, and Credit Card payment
- **Type:** `positive`
- **Priority:** `critical`

**Preconditions:**
- Shopper is authenticated with at least one saved shipping address in profile.
- Shopping cart contains at least one in-stock item.
- Promo code 'SAVE15' is active with a 15% discount on cart subtotal.

**Execution Steps:**
1. Step 1: Navigate to the cart and click 'Proceed to Checkout'.
2. Step 2: Select the default saved shipping address.
3. Step 3: Enter promo code 'SAVE15' in the promo field and click 'Apply'.
4. Step 4: Verify the order summary updates immediately with the 15% discount line item, recalculated taxes, and new total.
5. Step 5: Select 'Credit Card' payment method and enter valid card details (Luhn-compliant card number, valid expiration date, 3-digit CVV).
6. Step 6: Click 'Place Order'.

**Expected Outcome:**
Order is placed successfully. User is redirected to the Order Confirmation screen displaying a unique order reference number, estimated delivery date, order summary, and a background trigger dispatching the confirmation email.

---

### TC-002: Successful checkout with new international address and PayPal payment method
- **Type:** `positive`
- **Priority:** `high`

**Preconditions:**
- Shopper is authenticated.
- Shopping cart contains at least one in-stock physical item.
- PayPal sandbox account has sufficient balance and is accessible.

**Execution Steps:**
1. Step 1: Navigate to checkout and select 'Enter New Address'.
2. Step 2: Select 'United Kingdom' from the country dropdown and enter valid UK address details including postal code 'SW1A 1AA'.
3. Step 3: Verify postal code is accepted without validation errors.
4. Step 4: Select 'PayPal' as the payment method.
5. Step 5: Click 'Continue with PayPal', authenticate within the PayPal modal/redirect, and confirm payment authorization.
6. Step 6: Confirm final order total and complete purchase on the checkout return flow.

**Expected Outcome:**
PayPal payment processes successfully, the user sees the confirmation page with order reference and estimated delivery date, and order confirmation email is queued.

---

### TC-003: Invalid postal code format and expired promo code inline error handling without cart loss
- **Type:** `negative`
- **Priority:** `high`

**Preconditions:**
- Shopper is authenticated with two in-stock items in the cart.
- Promo code 'EXPIRED2020' is configured as expired in the promotion engine.

**Execution Steps:**
1. Step 1: Proceed to the single-page checkout.
2. Step 2: Select country 'United States' and enter an invalid postal code 'ABCDE-12'.
3. Step 3: Attempt to move focus or submit the shipping section.
4. Step 4: Enter promo code 'EXPIRED2020' into the promo code field and click 'Apply'.
5. Step 5: Observe the promo code section and the cart item list.

**Expected Outcome:**
Inline validation error 'Invalid ZIP code format for United States (expected 12345 or 12345-6789)' appears under the postal field. An inline error 'Promo code EXPIRED2020 has expired' appears under the promo field. Cart contents, items, quantities, and subtotal remain intact and unaffected.

---

### TC-004: Payment gateway failure retains user on checkout and holds item reservation for 10 minutes
- **Type:** `negative`
- **Priority:** `critical`

**Preconditions:**
- Shopper is on the checkout page with 1 item remaining in store inventory (low stock).
- Shipping details are valid.
- Payment gateway stub is configured to simulate an HTTP 504 Gateway Timeout or generic decline.

**Execution Steps:**
1. Step 1: Enter credit card details configured to trigger payment decline/timeout.
2. Step 2: Click 'Place Order'.
3. Step 3: Observe the checkout page after the payment failure response.
4. Step 4: In a separate session, attempt to purchase the same low-stock item as another user within 5 minutes.
5. Step 5: Verify item availability in the second session.

**Expected Outcome:**
User remains on the single-page checkout with an actionable error banner ('Payment authorization failed. Please check your card details or select an alternative payment method.'). Cart and checkout fields remain pre-populated. The item's stock reservation is held for the original user and is unavailable to other shoppers during the 10-minute hold window.

---

### TC-005: Boundary validation for Credit Card Luhn algorithm and CVV character lengths
- **Type:** `edge`
- **Priority:** `medium`

**Preconditions:**
- Shopper has an active cart and has filled all valid shipping address details.
- Checkout page is loaded with Credit Card selected as payment method.

**Execution Steps:**
1. Step 1: Enter a 16-digit card number failing the MOD-10 Luhn check (e.g., standard Visa pattern with incremented checksum digit) and observe validation.
2. Step 2: Enter a valid 16-digit Visa card and enter a 2-digit CVV ('12'); attempt to submit.
3. Step 3: Update CVV to a 5-digit number ('12345'); observe input field limit and validation.
4. Step 4: Enter a valid 15-digit American Express number and verify CVV accepts exactly 4 digits but rejects 3 or 5 digits.
5. Step 5: Enter exactly 3 digits for Visa and verify CVV field accepts it as valid.

**Expected Outcome:**
Luhn-failing card triggers immediate inline error 'Invalid card number'. The CVV field strictly enforces 3 digits for Visa/Mastercard and 4 digits for American Express, disallowing submission if CVV is under the minimum or truncating/blocking input exceeding the maximum length.

---

## Starter Automation Code

```python
"""
Enterprise Playwright Test Suite for E-Commerce Single-Page Checkout.

Architecture:
- Page Object Model (POM): CheckoutPage, OrderConfirmationPage, PayPalModalPage
- Framework: Playwright (Python synchronous API) + Pytest
- Concurrency / Multi-session support for inventory lock verification
"""

from typing import Generator
import pytest
from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    expect,
)


# ==============================================================================
# PAGE OBJECT MODEL
# ==============================================================================

class CheckoutPage:
    """Page Object encapsulating interactions on the Single-Page Checkout."""

    def __init__(self, page: Page) -> None:
        self.page = page

        # --- Navigation & Cart ---
        self.proceed_to_checkout_btn = page.locator("TODO_proceed_to_checkout_btn")  # TODO: Define locator for Proceed to Checkout button
        self.cart_items = page.locator("TODO_cart_items")  # TODO: Define locator for cart line items list
        self.subtotal_text = page.locator("TODO_subtotal_text")  # TODO: Define locator for cart subtotal display

        # --- Address Section ---
        self.saved_address_radio = page.locator("TODO_saved_address_radio")  # TODO: Define locator for default saved address radio
        self.enter_new_address_radio = page.locator("TODO_enter_new_address_radio")  # TODO: Define locator for enter new address option
        self.country_select = page.locator("TODO_country_select")  # TODO: Define locator for country dropdown
        self.street_input = page.locator("TODO_street_input")  # TODO: Define locator for street address input
        self.city_input = page.locator("TODO_city_input")  # TODO: Define locator for city input
        self.postal_code_input = page.locator("TODO_postal_code_input")  # TODO: Define locator for postal/ZIP code input
        self.postal_code_error = page.locator("TODO_postal_code_error")  # TODO: Define locator for postal code inline error

        # --- Promo Code Section ---
        self.promo_code_input = page.locator("TODO_promo_code_input")  # TODO: Define locator for promo code input
        self.apply_promo_btn = page.locator("TODO_apply_promo_btn")  # TODO: Define locator for apply promo code button
        self.promo_error_message = page.locator("TODO_promo_error_message")  # TODO: Define locator for promo code error message
        self.discount_line_item = page.locator("TODO_discount_line_item")  # TODO: Define locator for discount summary line
        self.tax_summary = page.locator("TODO_tax_summary")  # TODO: Define locator for recalculated tax display
        self.total_summary = page.locator("TODO_total_summary")  # TODO: Define locator for order total amount

        # --- Payment Methods ---
        self.credit_card_radio = page.locator("TODO_credit_card_radio")  # TODO: Define locator for Credit Card radio button
        self.paypal_radio = page.locator("TODO_paypal_radio")  # TODO: Define locator for PayPal radio button

        # --- Credit Card Form Fields ---
        self.card_number_input = page.locator("TODO_card_number_input")  # TODO: Define locator for Card Number input field
        self.card_expiry_input = page.locator("TODO_card_expiry_input")  # TODO: Define locator for Expiry Date input field
        self.card_cvv_input = page.locator("TODO_card_cvv_input")  # TODO: Define locator for CVV/CVC input field
        self.card_number_error = page.locator("TODO_card_number_error")  # TODO: Define locator for card number inline error
        self.card_cvv_error = page.locator("TODO_card_cvv_error")  # TODO: Define locator for CVV inline error

        # --- Action Buttons & Global Banners ---
        self.place_order_btn = page.locator("TODO_place_order_btn")  # TODO: Define locator for Place Order submission button
        self.continue_paypal_btn = page.locator("TODO_continue_paypal_btn")  # TODO: Define locator for Continue with PayPal button
        self.global_payment_error_banner = page.locator("TODO_global_payment_error_banner")  # TODO: Define locator for payment failure banner

    def navigate(self, url: str = "/checkout") -> None:
        """Navigate directly to the checkout page."""
        self.page.goto(url)

    def select_default_saved_address(self) -> None:
        """Select existing saved shipping address."""
        self.saved_address_radio.check()

    def enter_new_shipping_address(self, country: str, street: str, city: str, postal_code: str) -> None:
        """Fill new shipping address fields."""
        self.enter_new_address_radio.check()
        self.country_select.select_option(label=country)
        self.street_input.fill(street)
        self.city_input.fill(city)
        self.postal_code_input.fill(postal_code)

    def apply_promo_code(self, promo_code: str) -> None:
        """Input and apply a promotional discount code."""
        self.promo_code_input.fill(promo_code)
        self.apply_promo_btn.click()

    def select_credit_card(self) -> None:
        """Select Credit Card payment option."""
        self.credit_card_radio.check()

    def fill_credit_card_details(self, card_number: str, expiry: str, cvv: str) -> None:
        """Fill credit card fields."""
        self.card_number_input.fill(card_number)
        self.card_expiry_input.fill(expiry)
        self.card_cvv_input.fill(cvv)

    def place_order(self) -> None:
        """Submit the order placement form."""
        self.place_order_btn.click()


class PayPalModalPage:
    """Page Object encapsulating PayPal login & payment authorization popup/redirect."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.email_input = page.locator("TODO_paypal_email_input")  # TODO: Define locator for PayPal email input
        self.password_input = page.locator("TODO_paypal_password_input")  # TODO: Define locator for PayPal password input
        self.login_btn = page.locator("TODO_paypal_login_btn")  # TODO: Define locator for PayPal login button
        self.confirm_payment_btn = page.locator("TODO_paypal_confirm_payment_btn")  # TODO: Define locator for PayPal agree and pay button

    def authorize_payment(self, email: str, password: str) -> None:
        """Handle PayPal authentication and payment authorization."""
        self.email_input.fill(email)
        self.password_input.fill(password)
        self.login_btn.click()
        self.confirm_payment_btn.click()


class OrderConfirmationPage:
    """Page Object encapsulating verification on post-purchase confirmation."""

    def __init__(self, page: Page) -> None:
        self.page = page
        self.order_reference_number = page.locator("TODO_order_reference_number")  # TODO: Define locator for order ID element
        self.delivery_date = page.locator("TODO_delivery_date")  # TODO: Define locator for estimated delivery date text
        self.order_summary_container = page.locator("TODO_order_summary_container")  # TODO: Define locator for order summary box


# ==============================================================================
# PYTEST FIXTURES
# ==============================================================================

@pytest.fixture(scope="function")
def authenticated_context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """Provide an authenticated browser context with active cart state."""
    # Pre-configure storage state or injected session tokens as needed
    context = browser.new_context()
    yield context
    context.close()


@pytest.fixture(scope="function")
def checkout_page(authenticated_context: BrowserContext) -> CheckoutPage:
    """Provide an initialized CheckoutPage instance on an active session."""
    page = authenticated_context.new_page()
    checkout = CheckoutPage(page)
    checkout.navigate()
    return checkout


# ==============================================================================
# TEST CASES
# ==============================================================================

def test_tc_001_successful_order_saved_address_credit_card(checkout_page: CheckoutPage) -> None:
    """
    Test ID: TC-001
    Title: Successful order placement with saved address, valid promo code, and Credit Card payment.
    Expected Result: Order placed, redirected to confirmation with reference number, delivery date, and summary.
    """
    confirmation_page = OrderConfirmationPage(checkout_page.page)

    # Step 2: Select default saved shipping address
    checkout_page.select_default_saved_address()

    # Step 3: Enter and apply active promo code 'SAVE15'
    checkout_page.apply_promo_code("SAVE15")

    # Step 4: Verify order summary updates immediately with discount line item
    expect(checkout_page.discount_line_item).to_be_visible()
    expect(checkout_page.discount_line_item).to_contain_text("15%")

    # Step 5: Fill Credit Card payment method with Luhn-compliant credentials
    checkout_page.select_credit_card()
    checkout_page.fill_credit_card_details(
        card_number="4532015112830366",  # Standard Luhn-valid test Visa
        expiry="12/28",
        cvv="123",
    )

    # Step 6: Place Order
    checkout_page.place_order()

    # Assert: User is redirected to confirmation screen displaying order details
    expect(confirmation_page.order_reference_number).to_be_visible()
    expect(confirmation_page.delivery_date).to_be_visible()
    expect(confirmation_page.order_summary_container).to_be_visible()


def test_tc_002_checkout_new_international_address_paypal(
    authenticated_context: BrowserContext,
    checkout_page: CheckoutPage,
) -> None:
    """
    Test ID: TC-002
    Title: Successful checkout with new international address and PayPal payment method.
    Expected Result: PayPal payment authorizes successfully, confirmation page displays order reference and delivery date.
    """
    confirmation_page = OrderConfirmationPage(checkout_page.page)

    # Steps 1 & 2: Enter new UK address with valid postal code
    checkout_page.enter_new_shipping_address(
        country="United Kingdom",
        street="10 Downing Street",
        city="London",
        postal_code="SW1A 1AA",
    )

    # Step 3: Verify postal code is accepted without error
    expect(checkout_page.postal_code_error).not_to_be_visible()

    # Step 4: Select PayPal payment option
    checkout_page.paypal_radio.check()

    # Step 5: Handle PayPal redirect / popup window
    with authenticated_context.expect_page() as new_page_info:
        checkout_page.continue_paypal_btn.click()
    paypal_page = new_page_info.value
    paypal_modal = PayPalModalPage(paypal_page)

    paypal_modal.authorize_payment(email="shopper_sandbox@test.com", password="Password123!")

    # Step 6: Return to checkout flow and verify successful confirmation
    expect(confirmation_page.order_reference_number).to_be_visible()
    expect(confirmation_page.delivery_date).to_be_visible()


def test_tc_003_invalid_postal_code_and_expired_promo_without_cart_loss(
    checkout_page: CheckoutPage,
) -> None:
    """
    Test ID: TC-003
    Title: Invalid postal code format and expired promo code inline error handling without cart loss.
    Expected Result: Inline errors appear under postal and promo fields; cart contents remain intact.
    """
    initial_subtotal = checkout_page.subtotal_text.text_content()

    # Steps 2 & 3: Select US and enter malformed postal code
    checkout_page.enter_new_shipping_address(
        country="United States",
        street="123 Broadway",
        city="New York",
        postal_code="ABCDE-12",
    )
    checkout_page.postal_code_input.blur()

    # Verify postal code validation error
    expect(checkout_page.postal_code_error).to_be_visible()
    expect(checkout_page.postal_code_error).to_contain_text(
        "Invalid ZIP code format for United States (expected 12345 or 12345-6789)"
    )

    # Step 4: Apply expired promo code
    checkout_page.apply_promo_code("EXPIRED2020")

    # Step 5: Verify promo error displayed and cart preserved
    expect(checkout_page.promo_error_message).to_be_visible()
    expect(checkout_page.promo_error_message).to_contain_text("Promo code EXPIRED2020 has expired")

    # Verify cart contents, quantities, and subtotal are unaffected
    expect(checkout_page.cart_items).to_have_count(2)
    expect(checkout_page.subtotal_text).to_have_text(initial_subtotal or "")


def test_tc_004_payment_gateway_failure_retains_cart_and_holds_reservation(
    browser: Browser,
    checkout_page: CheckoutPage,
) -> None:
    """
    Test ID: TC-004
    Title: Payment gateway failure retains user on checkout and holds item reservation for 10 minutes.
    Expected Result: User remains on checkout with error banner; item is locked and unavailable to other sessions.
    """
    # Step 1: Input credit card configured to mock HTTP 504 gateway timeout / decline
    checkout_page.select_credit_card()
    checkout_page.fill_credit_card_details(
        card_number="4000000000000002",  # Gateway test stub for timeout / decline
        expiry="11/29",
        cvv="999",
    )

    # Step 2: Place order to trigger gateway failure
    checkout_page.place_order()

    # Step 3: Observe user remains on checkout page with actionable error banner
    expect(checkout_page.global_payment_error_banner).to_be_visible()
    expect(checkout_page.global_payment_error_banner).to_contain_text(
        "Payment authorization failed. Please check your card details or select an alternative payment method."
    )
    expect(checkout_page.card_number_input).to_be_visible()

    # Steps 4 & 5: Second session attempts to purchase low-stock reserved item within 10-minute hold window
    second_context = browser.new_context()
    second_user_page = second_context.new_page()
    second_user_page.goto("/product/low-stock-item-id")

    out_of_stock_banner = second_user_page.locator("TODO_out_of_stock_or_reserved_banner")  # TODO: Define locator for reservation lock label
    expect(out_of_stock_banner).to_be_visible()
    expect(out_of_stock_banner).to_contain_text("Reserved by another shopper")

    second_context.close()


def test_tc_005_boundary_validation_luhn_and_cvv_length(
    checkout_page: CheckoutPage,
) -> None:
    """
    Test ID: TC-005
    Title: Boundary validation for Credit Card Luhn algorithm and CVV character lengths.
    Expected Result: Luhn-failing card triggers inline error; CVV strictly enforces 3 digits for Visa and 4 for Amex.
    """
    checkout_page.select_credit_card()

    # Step 1: 16-digit card failing MOD-10 Luhn check (incremented checksum)
    checkout_page.card_number_input.fill("4532015112830367")
    checkout_page.card_number_input.blur()
    expect(checkout_page.card_number_error).to_be_visible()
    expect(checkout_page.card_number_error).to_contain_text("Invalid card number")

    # Step 2: Valid Visa with 2-digit CVV (under minimum)
    checkout_page.card_number_input.fill("4532015112830366")
    checkout_page.card_expiry_input.fill("12/28")
    checkout_page.card_cvv_input.fill("12")
    checkout_page.place_order()
    expect(checkout_page.card_cvv_error).to_be_visible()

    # Step 3: Input 5 digits into CVV for Visa (exceeds maximum boundary)
    checkout_page.card_cvv_input.fill("12345")
    # Verify input field enforces 3-digit max length via truncation or attribute constraint
    expect(checkout_page.card_cvv_input).to_have_value("123")

    # Step 4: American Express 15-digit card (expects exactly 4 digits)
    checkout_page.card_number_input.fill("378282246310005")  # Valid Amex prefix
    checkout_page.card_cvv_input.fill("123")
    checkout_page.place_order()
    expect(checkout_page.card_cvv_error).to_be_visible()  # 3 digits invalid for Amex

    checkout_page.card_cvv_input.fill("1234")
    checkout_page.card_cvv_input.blur()
    expect(checkout_page.card_cvv_error).not_to_be_visible()  # 4 digits accepted for Amex

    # Step 5: Visa with valid 3-digit CVV
    checkout_page.card_number_input.fill("4532015112830366")
    checkout_page.card_cvv_input.fill("123")
    checkout_page.card_cvv_input.blur()
    expect(checkout_page.card_cvv_error).not_to_be_visible()
```
