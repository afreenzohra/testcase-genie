# User Story: Enterprise Authentication with MFA & Lockout Protection

**Domain:** Authentication & Security  
**Feature:** Enterprise Login, Two-Factor TOTP & Rate-Limited Account Lockout  

### User Story:
> As an enterprise employee accessing the internal management console,  
> I want to authenticate using my corporate email address and password, and if Two-Factor Authentication (MFA) is enabled on my profile, enter a 6-digit Time-based One-Time Password (TOTP) from an authenticator app,  
> So that I can securely access the internal dashboard while protecting corporate data from credential stuffing and brute-force attacks.

### Acceptance Criteria:
1. Valid corporate email and password prompts for 6-digit MFA code when MFA is enabled.
2. Entering a valid 6-digit TOTP within its 30-second window grants session access and redirects to `/dashboard`.
3. Account must automatically lock for 15 minutes after 5 consecutive incorrect password or MFA attempts within a 15-minute sliding window.
4. An expired or previously used TOTP code must be rejected with "Code expired or invalid; generate a new code".
5. Password input field must obscure characters and provide a toggle button to unhide/mask.
