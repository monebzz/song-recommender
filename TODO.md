# TODO: Fix Subscription Activation and Header Dropdown

## Issues Identified
1. **Subscription activation bug**: Webhook lookup fails because `stripe_payment_intent_id` is updated before webhook fires
2. **Header dropdown not working**: JavaScript event listener doesn't match HTML classes/IDs

## Tasks
- [x] Add `order_id` field to Purchase and Subscription models
- [x] Create and run migration for `order_id` field
- [x] Update webhook to find records by `order_id` instead of `stripe_payment_intent_id`
- [x] Fix JavaScript event listeners for user dropdown
- [ ] Test subscription activation and dropdown functionality
