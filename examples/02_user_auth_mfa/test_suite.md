# 🧞 Test Suite: Enterprise Authentication and MFA Security Test Suite

**Application Domain:** Authentication & Security
**Framework:** selenium

## Executive Summary
- **Total Scenarios:** 5
- **Breakdown by Type:** Positive: 2 | Negative: 2 | Edge: 1
- **Breakdown by Priority:** Critical: 2 | High: 2 | Medium: 0 | Low: 1

### Requirement / Feature Description
> Validation of credentials, TOTP verification, brute-force defense, and account lockout

## Test Cases Summary Matrix

| ID | Title | Type | Priority | Expected Result |
| :--- | :--- | :---: | :---: | :--- |
| `TC-001` | Successful login with valid corporate credentials and valid TOTP MFA code | POSITIVE | CRITICAL | Session established; user redirected to /dashboard with greeting 'Welcome, Alice' |
| `TC-002` | Authentication denied when password is incorrect | NEGATIVE | HIGH | Error alert 'Invalid credentials' displayed; MFA prompt is not displayed; failed attempt count increments |
| `TC-003` | Rejection of expired or previously consumed TOTP token | NEGATIVE | HIGH | Inline validation error 'Invalid or expired code. Please enter the current code from your authenticator' displayed |
| `TC-004` | Account lockout triggered upon 5 consecutive failed login attempts | EDGE | CRITICAL | Account locked banner displayed: 'Your account has been temporarily locked for 15 minutes due to multiple failed attempts'; subsequent valid login attempts are rejected during lockout |
| `TC-005` | Mask and unmask password toggle interaction | POSITIVE | LOW | Input field toggles dynamically between type='text' and type='password' |

## Detailed Test Specifications

### TC-001: Successful login with valid corporate credentials and valid TOTP MFA code
- **Type:** `positive`
- **Priority:** `critical`

**Preconditions:**
- User account exists with email 'alice@enterprise.corp' and status 'Active'
- Two-factor authentication is configured and enabled for user

**Execution Steps:**
1. Navigate to https://portal.enterprise.corp/login
2. Enter 'alice@enterprise.corp' into email field
3. Enter valid password into password field and click 'Sign In'
4. Observe redirect to MFA challenge page
5. Generate fresh TOTP from authenticator and enter into 6-digit input
6. Click 'Verify & Continue'

**Expected Outcome:**
Session established; user redirected to /dashboard with greeting 'Welcome, Alice'

---

### TC-002: Authentication denied when password is incorrect
- **Type:** `negative`
- **Priority:** `high`

**Preconditions:**
- User account exists and is not locked

**Execution Steps:**
1. Navigate to login page
2. Enter 'alice@enterprise.corp' and invalid password 'WrongPass!123'
3. Click 'Sign In'

**Expected Outcome:**
Error alert 'Invalid credentials' displayed; MFA prompt is not displayed; failed attempt count increments

---

### TC-003: Rejection of expired or previously consumed TOTP token
- **Type:** `negative`
- **Priority:** `high`

**Preconditions:**
- User has submitted valid primary credentials and is on MFA prompt screen
- TOTP token '123456' has already been consumed or its 30s window has expired

**Execution Steps:**
1. Enter expired TOTP '123456' into code input
2. Click 'Verify & Continue'

**Expected Outcome:**
Inline validation error 'Invalid or expired code. Please enter the current code from your authenticator' displayed

---

### TC-004: Account lockout triggered upon 5 consecutive failed login attempts
- **Type:** `edge`
- **Priority:** `critical`

**Preconditions:**
- User account has 4 recorded failed attempts within the past 10 minutes

**Execution Steps:**
1. Enter 'alice@enterprise.corp' with 5th incorrect password
2. Click 'Sign In'

**Expected Outcome:**
Account locked banner displayed: 'Your account has been temporarily locked for 15 minutes due to multiple failed attempts'; subsequent valid login attempts are rejected during lockout

---

### TC-005: Mask and unmask password toggle interaction
- **Type:** `positive`
- **Priority:** `low`

**Preconditions:**
- User is on the login page

**Execution Steps:**
1. Enter 'SuperSecretP@ss1' in password input
2. Verify input type is 'password'
3. Click eye / toggle icon
4. Verify input type changes to 'text' and password characters are visible
5. Click toggle icon again

**Expected Outcome:**
Input field toggles dynamically between type='text' and type='password'

---

## Starter Automation Code

```python
import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class LoginPage:
    """Page Object for Enterprise Login and MFA Challenge."""

    EMAIL_INPUT = (By.ID, "corporate-email")  # TODO: Define locator for email input
    PASSWORD_INPUT = (By.ID, "account-password")  # TODO: Define locator for password input
    SIGN_IN_BTN = (By.CSS_SELECTOR, "button[type='submit']")  # TODO: Define locator for sign in button
    MFA_CODE_INPUT = (By.ID, "totp-code-input")  # TODO: Define locator for 6-digit TOTP input
    VERIFY_MFA_BTN = (By.ID, "btn-verify-mfa")  # TODO: Define locator for verify MFA button
    ERROR_ALERT = (By.CLASS_NAME, "alert-danger")  # TODO: Define locator for error alert
    LOCKOUT_ALERT = (By.CLASS_NAME, "alert-lockout")  # TODO: Define locator for lockout message
    PASSWORD_TOGGLE = (By.ID, "toggle-password-visibility")  # TODO: Define locator for show/hide password toggle
    DASHBOARD_HEADING = (By.TAG_NAME, "h1")  # TODO: Define locator for dashboard greeting

    def __init__(self, driver: webdriver.Remote):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    def enter_credentials(self, email: str, password: str):
        self.wait.until(EC.visibility_of_element_located(self.EMAIL_INPUT)).send_keys(email)
        self.driver.find_element(*self.PASSWORD_INPUT).send_keys(password)
        self.driver.find_element(*self.SIGN_IN_BTN).click()

    def enter_mfa_code(self, code: str):
        self.wait.until(EC.visibility_of_element_located(self.MFA_CODE_INPUT)).send_keys(code)
        self.driver.find_element(*self.VERIFY_MFA_BTN).click()

    def toggle_password_visibility(self):
        self.driver.find_element(*self.PASSWORD_TOGGLE).click()

    def get_password_field_type(self) -> str:
        return self.driver.find_element(*self.PASSWORD_INPUT).get_attribute("type")


@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)
    driver.implicitly_wait(5)
    yield driver
    driver.quit()


def test_tc_001_successful_login_with_mfa(driver):
    """TC-001: Successful login with valid corporate credentials and valid TOTP MFA code."""
    driver.get("https://portal.enterprise.corp/login")
    login = LoginPage(driver)
    login.enter_credentials("alice@enterprise.corp", "ValidP@ssw0rd!")
    login.enter_mfa_code("582910")
    heading = login.wait.until(EC.visibility_of_element_located(LoginPage.DASHBOARD_HEADING))
    assert "Welcome, Alice" in heading.text


def test_tc_002_invalid_password(driver):
    """TC-002: Authentication denied when password is incorrect."""
    driver.get("https://portal.enterprise.corp/login")
    login = LoginPage(driver)
    login.enter_credentials("alice@enterprise.corp", "WrongPass!123")
    alert = login.wait.until(EC.visibility_of_element_located(LoginPage.ERROR_ALERT))
    assert "Invalid credentials" in alert.text


def test_tc_003_expired_mfa_code(driver):
    """TC-003: Rejection of expired or previously consumed TOTP token."""
    driver.get("https://portal.enterprise.corp/login")
    login = LoginPage(driver)
    login.enter_credentials("alice@enterprise.corp", "ValidP@ssw0rd!")
    login.enter_mfa_code("000000")
    alert = login.wait.until(EC.visibility_of_element_located(LoginPage.ERROR_ALERT))
    assert "Invalid or expired code" in alert.text


def test_tc_004_account_lockout_after_failures(driver):
    """TC-004: Account lockout triggered upon 5 consecutive failed login attempts."""
    driver.get("https://portal.enterprise.corp/login")
    login = LoginPage(driver)
    login.enter_credentials("alice@enterprise.corp", "WrongPass5")
    lockout = login.wait.until(EC.visibility_of_element_located(LoginPage.LOCKOUT_ALERT))
    assert "locked for 15 minutes" in lockout.text


def test_tc_005_password_mask_toggle(driver):
    """TC-005: Mask and unmask password toggle interaction."""
    driver.get("https://portal.enterprise.corp/login")
    login = LoginPage(driver)
    login.enter_credentials("alice@enterprise.corp", "SuperSecretP@ss1")
    assert login.get_password_field_type() == "password"
    login.toggle_password_visibility()
    assert login.get_password_field_type() == "text"
```
