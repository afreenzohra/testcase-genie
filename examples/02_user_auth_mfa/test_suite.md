# 🧞 Test Suite: Enterprise Authentication with MFA & Lockout Protection Test Suite

**Application Domain:** Authentication & Security
**Framework:** selenium

## Executive Summary
- **Total Scenarios:** 5
- **Breakdown by Type:** Positive: 2 | Negative: 2 | Edge: 1
- **Breakdown by Priority:** Critical: 2 | High: 2 | Medium: 1 | Low: 0

### Requirement / Feature Description
> Comprehensive test suite covering primary authentication, TOTP validation, anti-replay/expiration checks, password masking controls, and brute-force lockout rules across a 15-minute sliding window.

## Test Cases Summary Matrix

| ID | Title | Type | Priority | Expected Result |
| :--- | :--- | :---: | :---: | :--- |
| `TC-001` | Successful End-to-End Authentication with Valid Credentials and Active TOTP MFA | POSITIVE | CRITICAL | Authentication completes successfully; user session cookie/token is issued, and browser redirects to '/dashboard'. |
| `TC-002` | Verify Password Masking and Unhide/Mask Toggle Control Functionality | POSITIVE | MEDIUM | Password field defaults to masked input, toggles to plain text on user command, and toggles back to obscured characters without modifying or clearing the typed string. |
| `TC-003` | Reject Authentication Attempt with Expired or Previously Consumed TOTP Code | NEGATIVE | HIGH | Authentication fails; session is not granted, and error message is displayed: 'Code expired or invalid; generate a new code'. |
| `TC-004` | Trigger 15-Minute Account Lockout After 5 Consecutive Primary Password Failures | NEGATIVE | CRITICAL | On the 5th failure, the account status transitions to locked. The 6th attempt with valid credentials is rejected with an account lockout notification indicating the account is locked for 15 minutes. |
| `TC-005` | Account Lockout Enforcement Across Mixed Password and MFA Failures in 15-Minute Sliding Window | EDGE | HIGH | System aggregates primary credential and MFA failures within the 15-minute sliding window; the 5th cumulative failure triggers the 15-minute account lockout, denying access even with valid primary and MFA credentials. |

## Detailed Test Specifications

### TC-001: Successful End-to-End Authentication with Valid Credentials and Active TOTP MFA
- **Type:** `positive`
- **Priority:** `critical`

**Preconditions:**
- Corporate user account exists with email 'emp.test@corp.internal' and has MFA enabled.
- Authenticator TOTP shared secret is synchronized with the auth server.
- Account is active, unlocked, and has 0 failed attempts recorded.

**Execution Steps:**
1. 1. Navigate to enterprise login portal at '/login'.
2. 2. Input 'emp.test@corp.internal' into the corporate email field.
3. 3. Input the valid user password into the password field.
4. 4. Click the 'Sign In' button.
5. 5. Verify that the UI transitions to the MFA verification screen with an input field for a 6-digit code.
6. 6. Obtain the current valid 6-digit TOTP code from the authenticator app within its 30-second validity window.
7. 7. Enter the 6-digit TOTP code and submit the verification form.

**Expected Outcome:**
Authentication completes successfully; user session cookie/token is issued, and browser redirects to '/dashboard'.

---

### TC-002: Verify Password Masking and Unhide/Mask Toggle Control Functionality
- **Type:** `positive`
- **Priority:** `medium`

**Preconditions:**
- User is on the enterprise login screen at '/login'.

**Execution Steps:**
1. 1. Focus on the password input field.
2. 2. Type the string 'ComplexSecur3P@ss!'.
3. 3. Inspect the DOM to verify the input type attribute is 'password' and characters are obscured by mask glyphs.
4. 4. Click the eye/toggle unmask icon located inside or adjacent to the password input field.
5. 5. Inspect the DOM to verify the input type attribute changes to 'text' and the text 'ComplexSecur3P@ss!' is visible in plain text.
6. 6. Click the toggle unmask icon a second time.
7. 7. Verify the input type attribute switches back to 'password' with characters masked and input content intact.

**Expected Outcome:**
Password field defaults to masked input, toggles to plain text on user command, and toggles back to obscured characters without modifying or clearing the typed string.

---

### TC-003: Reject Authentication Attempt with Expired or Previously Consumed TOTP Code
- **Type:** `negative`
- **Priority:** `high`

**Preconditions:**
- User account 'mfa.user@corp.internal' has MFA enabled.
- Primary email and password credentials have been entered successfully, landing on the MFA entry step.

**Execution Steps:**
1. 1. Capture a valid 6-digit TOTP code from the authenticator app.
2. 2. Wait at least 31 seconds for the current 30-second TOTP validity window to lapse.
3. 3. Enter the elapsed 6-digit TOTP code into the MFA code input field.
4. 4. Click the 'Verify' button.
5. 5. Attempt to re-enter a previously consumed TOTP token from an earlier successful login.

**Expected Outcome:**
Authentication fails; session is not granted, and error message is displayed: 'Code expired or invalid; generate a new code'.

---

### TC-004: Trigger 15-Minute Account Lockout After 5 Consecutive Primary Password Failures
- **Type:** `negative`
- **Priority:** `critical`

**Preconditions:**
- User account 'lockout.victim@corp.internal' exists, is active, and has 0 failed attempts recorded.

**Execution Steps:**
1. 1. Navigate to '/login'.
2. 2. Submit 'lockout.victim@corp.internal' with an invalid password 4 consecutive times within a 2-minute interval.
3. 3. Confirm that attempts 1 through 4 display an 'Invalid credentials' error and allow subsequent login attempts.
4. 4. Submit the 5th consecutive invalid password attempt.
5. 5. Attempt a 6th login using the actual, valid password for 'lockout.victim@corp.internal'.

**Expected Outcome:**
On the 5th failure, the account status transitions to locked. The 6th attempt with valid credentials is rejected with an account lockout notification indicating the account is locked for 15 minutes.

---

### TC-005: Account Lockout Enforcement Across Mixed Password and MFA Failures in 15-Minute Sliding Window
- **Type:** `edge`
- **Priority:** `high`

**Preconditions:**
- User account 'mixed.fail@corp.internal' exists with MFA enabled.
- Sliding window counter is clean with 0 recorded failures.

**Execution Steps:**
1. 1. Enter 'mixed.fail@corp.internal' with an incorrect password 3 consecutive times.
2. 2. On attempt 4, enter the correct password to pass primary authentication and reach the MFA screen.
3. 3. Enter an invalid 6-digit code on the MFA screen (failure count: 4).
4. 4. Return to login, enter the correct password, reach the MFA screen, and enter an invalid 6-digit code for the 5th total failure within 10 minutes of attempt 1.
5. 5. Immediately attempt to authenticate using valid primary credentials and a valid TOTP.

**Expected Outcome:**
System aggregates primary credential and MFA failures within the 15-minute sliding window; the 5th cumulative failure triggers the 15-minute account lockout, denying access even with valid primary and MFA credentials.

---

## Starter Automation Code

```python
"""
Enterprise Authentication & MFA Test Suite
Implements Page Object Model (POM) using Selenium WebDriver and pytest.
Covers positive authentication, MFA validation, field masking, and rate-limiting/lockout logic.
"""

from typing import Tuple
import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait


# ==============================================================================
# Helper Utilities (TOTP Generator Simulation)
# ==============================================================================

class TotpHelper:
    """Helper to simulate TOTP code generation for automation."""

    @staticmethod
    def get_valid_totp(secret: str = "JBSWY3DPEHPK3PXP") -> str:
        """
        Generate or retrieve a currently valid 6-digit TOTP token.
        In production, integrate `pyotp.TOTP(secret).now()`.
        """
        try:
            import pyotp  # type: ignore
            return pyotp.TOTP(secret).now()
        except ImportError:
            # Fallback stub token for environments without pyotp installed
            return "123456"

    @staticmethod
    def get_expired_totp(secret: str = "JBSWY3DPEHPK3PXP") -> str:
        """
        Generate an expired 6-digit TOTP token (offset by -60 seconds).
        In production, integrate `pyotp.TOTP(secret).at(time.time() - 60)`.
        """
        try:
            import time
            import pyotp  # type: ignore
            return pyotp.TOTP(secret).at(time.time() - 60)
        except ImportError:
            # Fallback stub expired/consumed token
            return "987654"


# ==============================================================================
# Page Object Model: Base Page
# ==============================================================================

class BasePage:
    """Base Page Object containing shared browser interactions and wait mechanisms."""

    def __init__(self, driver: WebDriver, timeout: int = 10) -> None:
        self.driver: WebDriver = driver
        self.wait: WebDriverWait = WebDriverWait(driver, timeout)

    def navigate_to(self, url: str) -> None:
        """Navigate to a target URL."""
        self.driver.get(url)

    def find(self, locator: Tuple[By, str]) -> WebElement:
        """Find an element after waiting for its presence in the DOM."""
        return self.wait.until(EC.presence_of_element_located(locator))

    def find_visible(self, locator: Tuple[By, str]) -> WebElement:
        """Find an element after waiting for its visibility."""
        return self.wait.until(EC.visibility_of_element_located(locator))

    def click(self, locator: Tuple[By, str]) -> None:
        """Wait for element to be clickable and click."""
        self.wait.until(EC.element_to_be_clickable(locator)).click()

    def type_text(self, locator: Tuple[By, str], text: str, clear: bool = True) -> None:
        """Type text into an input field, optionally clearing it first."""
        element = self.wait.until(EC.visibility_of_element_located(locator))
        if clear:
            element.clear()
        element.send_keys(text)

    def get_text(self, locator: Tuple[By, str]) -> str:
        """Get visible text from an element."""
        return self.wait.until(EC.visibility_of_element_located(locator)).text

    def get_attribute(self, locator: Tuple[By, str], attribute: str) -> str:
        """Retrieve an element attribute value."""
        return self.find(locator).get_attribute(attribute) or ""

    def wait_for_url_contains(self, fragment: str) -> bool:
        """Wait until current URL contains expected text fragment."""
        return self.wait.until(EC.url_contains(fragment))


# ==============================================================================
# Page Object Model: Login Page
# ==============================================================================

class LoginPage(BasePage):
    """Page Object encapsulating UI interactions on '/login'."""

    # Locators
    EMAIL_INPUT = (By.ID, "TODO_replace_with_email_input_id")  # TODO: Define locator for corporate email input
    PASSWORD_INPUT = (By.ID, "TODO_replace_with_password_input_id")  # TODO: Define locator for password input
    PASSWORD_TOGGLE_BUTTON = (By.CSS_SELECTOR, "TODO_replace_with_toggle_btn_selector")  # TODO: Define locator for unmask toggle
    SIGN_IN_BUTTON = (By.XPATH, "//button[@type='submit']")  # TODO: Define locator for sign in submit button
    ERROR_ALERT_BANNER = (By.CSS_SELECTOR, "[role='alert']")  # TODO: Define locator for credential error alert
    LOCKOUT_ALERT_BANNER = (By.ID, "TODO_replace_with_lockout_alert_id")  # TODO: Define locator for account lockout alert

    def open(self, base_url: str = "https://corp.internal/login") -> "LoginPage":
        """Navigate to enterprise login portal."""
        self.navigate_to(base_url)
        return self

    def enter_email(self, email: str) -> "LoginPage":
        """Input corporate email."""
        self.type_text(self.EMAIL_INPUT, email)
        return self

    def enter_password(self, password: str) -> "LoginPage":
        """Input user password."""
        self.type_text(self.PASSWORD_INPUT, password)
        return self

    def click_password_visibility_toggle(self) -> "LoginPage":
        """Toggle mask/unmask control for password input."""
        self.click(self.PASSWORD_TOGGLE_BUTTON)
        return self

    def get_password_field_type(self) -> str:
        """Retrieve DOM 'type' attribute of password field (e.g. 'password' vs 'text')."""
        return self.get_attribute(self.PASSWORD_INPUT, "type")

    def get_password_field_value(self) -> str:
        """Retrieve DOM 'value' attribute of password field."""
        return self.get_attribute(self.PASSWORD_INPUT, "value")

    def submit_login(self) -> None:
        """Click the primary Sign In button."""
        self.click(self.SIGN_IN_BUTTON)

    def execute_login(self, email: str, password: str) -> None:
        """Convenience composite action for email + password + submit."""
        self.enter_email(email)
        self.enter_password(password)
        self.submit_login()

    def get_error_message(self) -> str:
        """Retrieve the text from the error alert banner."""
        return self.get_text(self.ERROR_ALERT_BANNER)

    def get_lockout_message(self) -> str:
        """Retrieve text from account lockout notification."""
        return self.get_text(self.LOCKOUT_ALERT_BANNER)


# ==============================================================================
# Page Object Model: MFA Verification Page
# ==============================================================================

class MfaPage(BasePage):
    """Page Object encapsulating UI interactions on the MFA TOTP step."""

    # Locators
    MFA_CONTAINER = (By.ID, "TODO_replace_with_mfa_container_id")  # TODO: Define locator for MFA view container
    TOTP_INPUT = (By.NAME, "TODO_replace_with_totp_code_name")  # TODO: Define locator for 6-digit TOTP input
    VERIFY_BUTTON = (By.XPATH, "//button[contains(text(),'Verify')]")  # TODO: Define locator for verify button
    MFA_ERROR_MESSAGE = (By.CSS_SELECTOR, ".mfa-error-message")  # TODO: Define locator for MFA error label

    def is_mfa_screen_displayed(self) -> bool:
        """Verify presence and visibility of the MFA input screen."""
        element = self.find_visible(self.MFA_CONTAINER)
        return element.is_displayed()

    def enter_totp_code(self, code: str) -> "MfaPage":
        """Enter 6-digit TOTP into verification input."""
        self.type_text(self.TOTP_INPUT, code)
        return self

    def click_verify(self) -> None:
        """Submit the TOTP verification form."""
        self.click(self.VERIFY_BUTTON)

    def submit_totp(self, code: str) -> None:
        """Composite action to enter code and click verify."""
        self.enter_totp_code(code)
        self.click_verify()

    def get_mfa_error_message(self) -> str:
        """Retrieve displayed error text when TOTP verification fails."""
        return self.get_text(self.MFA_ERROR_MESSAGE)


# ==============================================================================
# Page Object Model: Internal Dashboard Page
# ==============================================================================

class DashboardPage(BasePage):
    """Page Object encapsulating UI interactions on '/dashboard'."""

    # Locators
    DASHBOARD_HEADER = (By.TAG_NAME, "h1")  # TODO: Define locator for dashboard title header
    USER_PROFILE_MENU = (By.ID, "TODO_replace_with_profile_menu_id")  # TODO: Define locator for profile badge

    def is_dashboard_loaded(self) -> bool:
        """Verify redirect to dashboard and visibility of core dashboard components."""
        url_matches = self.wait_for_url_contains("/dashboard")
        header_visible = self.find_visible(self.DASHBOARD_HEADER).is_displayed()
        return url_matches and header_visible


# ==============================================================================
# Test Fixtures
# ==============================================================================

@pytest.fixture(scope="function")
def driver() -> WebDriver:
    """
    Standard pytest fixture for WebDriver lifecycle management.
    Initializes headless Chrome with security defaults and cleans up after test.
    """
    chrome_options = ChromeOptions()
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)
    yield driver
    driver.quit()


# ==============================================================================
# Test Suite: Enterprise Authentication & Lockout Protection
# ==============================================================================

class TestEnterpriseAuthentication:
    """Suite validating enterprise authentication, MFA TOTP checks, and lockout policies."""

    LOGIN_URL = "https://corp.internal/login"
    VALID_USER = "emp.test@corp.internal"
    VALID_PASSWORD = "CorrectSecurePassword123!"

    def test_tc_001_successful_auth_with_valid_credentials_and_active_totp(self, driver: WebDriver) -> None:
        """
        Test ID: TC-001
        Priority: Critical
        Expected Result: Authentication completes successfully; user session is issued,
                         and browser redirects to '/dashboard'.
        """
        login_page = LoginPage(driver).open(self.LOGIN_URL)
        mfa_page = MfaPage(driver)
        dashboard_page = DashboardPage(driver)

        # Step 1-4: Submit primary credentials
        login_page.execute_login(self.VALID_USER, self.VALID_PASSWORD)

        # Step 5: Verify transition to MFA challenge screen
        assert mfa_page.is_mfa_screen_displayed(), (
            "Expected MFA verification screen to display after valid primary credentials."
        )

        # Step 6-7: Enter active TOTP code and submit
        totp_code = TotpHelper.get_valid_totp()
        mfa_page.submit_totp(totp_code)

        # Assertion: Validate successful redirect to '/dashboard'
        assert dashboard_page.is_dashboard_loaded(), (
            "Expected user to be authenticated and redirected to '/dashboard'."
        )

    def test_tc_002_password_masking_and_unhide_toggle_functionality(self, driver: WebDriver) -> None:
        """
        Test ID: TC-002
        Priority: Medium
        Expected Result: Password field defaults to masked input ('password'), toggles to
                         plain text ('text'), and toggles back without clearing input.
        """
        login_page = LoginPage(driver).open(self.LOGIN_URL)
        test_payload = "ComplexSecur3P@ss!"

        # Step 1-2: Type password into input field
        login_page.enter_password(test_payload)

        # Step 3: Verify initial state is obscured ('password')
        initial_type = login_page.get_password_field_type()
        assert initial_type == "password", (
            f"Expected initial input type to be 'password', got '{initial_type}'."
        )

        # Step 4-5: Click toggle icon and verify conversion to plain text ('text')
        login_page.click_password_visibility_toggle()
        unmasked_type = login_page.get_password_field_type()
        unmasked_value = login_page.get_password_field_value()
        assert unmasked_type == "text", (
            f"Expected input type to switch to 'text', got '{unmasked_type}'."
        )
        assert unmasked_value == test_payload, (
            "Password input value changed or was cleared upon toggle."
        )

        # Step 6-7: Click toggle icon again and verify reversion to obscured ('password')
        login_page.click_password_visibility_toggle()
        remasked_type = login_page.get_password_field_type()
        remasked_value = login_page.get_password_field_value()
        assert remasked_type == "password", (
            f"Expected input type to revert to 'password', got '{remasked_type}'."
        )
        assert remasked_value == test_payload, (
            "Password input value was modified after unmask-mask cycle."
        )

    def test_tc_003_reject_expired_or_consumed_totp_code(self, driver: WebDriver) -> None:
        """
        Test ID: TC-003
        Priority: High
        Expected Result: Authentication fails; session is not granted, and error message
                         is displayed: 'Code expired or invalid; generate a new code'.
        """
        user_email = "mfa.user@corp.internal"
        login_page = LoginPage(driver).open(self.LOGIN_URL)
        mfa_page = MfaPage(driver)

        # Primary authentication
        login_page.execute_login(user_email, self.VALID_PASSWORD)
        assert mfa_page.is_mfa_screen_displayed(), "Failed to reach MFA challenge screen."

        # Provide expired TOTP code (offset window)
        expired_totp = TotpHelper.get_expired_totp()
        mfa_page.submit_totp(expired_totp)

        # Assertion: Check explicit rejection message and that URL remains on MFA
        error_text = mfa_page.get_mfa_error_message()
        expected_error = "Code expired or invalid; generate a new code"
        assert expected_error in error_text, (
            f"Expected error '{expected_error}', but received '{error_text}'."
        )
        assert "/dashboard" not in driver.current_url, (
            "User must not be redirected to '/dashboard' with an expired TOTP."
        )

    def test_tc_004_trigger_account_lockout_after_five_consecutive_password_failures(self, driver: WebDriver) -> None:
        """
        Test ID: TC-004
        Priority: Critical
        Expected Result: On 5th invalid attempt, account locks. 6th attempt with valid
                         credentials is rejected with a 15-minute lockout notice.
        """
        target_account = "lockout.victim@corp.internal"
        login_page = LoginPage(driver).open(self.LOGIN_URL)

        # Step 1-3: Perform 4 consecutive failed password attempts
        for attempt_index in range(1, 5):
            login_page.execute_login(target_account, f"InvalidPass_{attempt_index}")
            error_message = login_page.get_error_message()
            assert "Invalid credentials" in error_message, (
                f"Attempt {attempt_index}: Expected 'Invalid credentials' error banner."
            )

        # Step 4: Perform 5th consecutive failure to trip lockout threshold
        login_page.execute_login(target_account, "InvalidPass_5")

        # Step 5: Attempt 6th login using legitimate, valid credentials
        login_page.execute_login(target_account, self.VALID_PASSWORD)

        # Assertion: Validate lockout enforcement
        lockout_text = login_page.get_lockout_message()
        assert "locked for 15 minutes" in lockout_text.lower(), (
            f"Expected 15-minute account lockout warning on valid login attempt, got: '{lockout_text}'."
        )
        assert "/dashboard" not in driver.current_url, (
            "Locked account was unexpectedly granted access to '/dashboard'."
        )

    def test_tc_005_account_lockout_mixed_password_and_mfa_failures(self, driver: WebDriver) -> None:
        """
        Test ID: TC-005
        Priority: High
        Expected Result: System aggregates password and MFA failures within sliding window;
                         5th failure triggers lockout, denying access even with valid credentials.
        """
        target_account = "mixed.fail@corp.internal"
        login_page = LoginPage(driver).open(self.LOGIN_URL)
        mfa_page = MfaPage(driver)

        # Step 1: 3 failed password attempts
        for attempt_index in range(1, 4):
            login_page.execute_login(target_account, f"WrongPassword_{attempt_index}")
            assert "Invalid credentials" in login_page.get_error_message()

        # Step 2-3: 4th failure (Valid primary password, but invalid MFA)
        login_page.execute_login(target_account, self.VALID_PASSWORD)
        assert mfa_page.is_mfa_screen_displayed()
        mfa_page.submit_totp("000000")  # Invalid MFA Attempt #1 (Total Failures = 4)

        # Step 4: 5th cumulative failure (Return to login, correct password, invalid MFA)
        login_page.open(self.LOGIN_URL)
        login_page.execute_login(target_account, self.VALID_PASSWORD)
        assert mfa_page.is_mfa_screen_displayed()
        mfa_page.submit_totp("000001")  # Invalid MFA Attempt #2 (Total Failures = 5 -> Lockout)

        # Step 5: Attempt 6th login with valid primary credentials and valid TOTP
        login_page.open(self.LOGIN_URL)
        login_page.execute_login(target_account, self.VALID_PASSWORD)

        # Assertion: Account should be locked immediately at primary login or fail to transition
        lockout_notice = login_page.get_lockout_message()
        assert "locked" in lockout_notice.lower(), (
            "Expected account lockout enforcement after 5 cumulative failures across password and MFA."
        )
        assert "/dashboard" not in driver.current_url, (
            "Access was granted despite hitting 5 cumulative authentication failures."
        )
```
