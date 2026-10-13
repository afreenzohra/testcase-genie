# User Story: E-Commerce Single-Page Checkout

**Domain:** E-Commerce & Retail  
**Feature:** Single-Page Checkout with Multi-Payment & Promo Code  

### User Story:
> As a registered shopper on an online shopping portal,  
> I want to proceed from my cart to a single-page checkout, select a saved shipping address or enter a new one, choose between Credit Card and PayPal payment methods, apply an optional promo code, and review order totals (subtotal, tax, shipping, discount),  
> So that I can place my order securely, receive immediate on-screen confirmation with an order number, and trigger an automated confirmation email.

### Acceptance Criteria:
1. Shopper must have at least one in-stock item in cart to access checkout.
2. Address form must validate postal code format according to selected country.
3. Promo code discounts must calculate dynamically; expired or invalid codes must display an inline error without wiping cart contents.
4. Credit card fields must enforce Luhn check and CVV length (3-4 digits).
5. If payment fails or times out, user must remain on checkout page with an actionable error message and item reservation retained for 10 minutes.
6. Upon successful placement, user sees an order confirmation screen with order reference number and estimated delivery date.
