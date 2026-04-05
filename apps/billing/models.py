"""
Billing models — placeholder for future implementation.

Planned:
  - SubscriptionPlan  (free / pro / enterprise tiers)
  - Invoice           (monthly usage report per organization)
  - PaymentMethod     (Stripe payment source)
  - UsageRecord       (energy consumed per session, used for invoice line items)

Integration:
  - Stripe via djstripe or direct stripe-python SDK
  - Webhook endpoint to reconcile payment events
"""
