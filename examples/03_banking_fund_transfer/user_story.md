# User Story: Retail Banking Instant Fund Transfer

**Domain:** Banking & FinTech  
**Feature:** Peer-to-Peer & External Account Fund Transfer with Idempotency  

### User Story:
> As a retail banking mobile/web customer,  
> I want to transfer funds from my checking account to an external beneficiary using an account number and routing code (or IBAN), with real-time balance checks, daily limit enforcement ($5,000 maximum per 24 hours), and protection against duplicate submissions,  
> So that I can reliably pay bills or individuals without accidental duplicate debits or overdraft penalties.

### Acceptance Criteria:
1. Available balance must exceed transfer amount + applicable transaction fee ($0.50).
2. Daily transfer cumulative limit cannot exceed $5,000; transfers exceeding the limit must fail with "Daily transfer limit exceeded".
3. Idempotency key generated per transfer request must prevent duplicate debit even if user double-clicks the submit button or suffers a network retry.
4. Negative numbers or zero amounts must be blocked at UI validation before network request.
5. On successful transfer, source account balance is immediately debited, transaction appears in ledger, and SMS/Email confirmation is triggered.
