# ⚡ Quick Stripe Setup (5 Minutes)

## What's Done ✅
- Stripe integration code is complete
- Django views and webhooks are ready
- Database models are set up
- Settings are configured

## What You Need to Do 🔧

### 1️⃣ Get Stripe Keys (2 minutes)
```
1. Go to https://dashboard.stripe.com
2. Sign up (free) or sign in
3. Click Developers → API Keys
4. Copy your Publishable Key (pk_test_...)
5. Copy your Secret Key (sk_test_...)
```

### 2️⃣ Update `.env` File (1 minute)
```env
STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_KEY
STRIPE_SECRET_KEY=sk_test_YOUR_KEY
STRIPE_WEBHOOK_SECRET=whsec_YOUR_SECRET
SITE_URL=http://127.0.0.1:8000
```

### 3️⃣ Set Up Webhook (2 minutes)
```
1. Stripe Dashboard → Developers → Webhooks
2. Click "Add endpoint"
3. URL: http://127.0.0.1:8000/webhook/stripe/
4. Select events:
   - checkout.session.completed
   - payment_intent.payment_failed
5. Copy Signing Secret → paste in .env as STRIPE_WEBHOOK_SECRET
```

### 4️⃣ Test It! 🎉
```
1. Go to http://127.0.0.1:8000/subscribe/
2. Click "Subscribe Monthly"
3. Use test card: 4242 4242 4242 4242
4. Any future expiry date (12/25)
5. Any 3-digit CVC (123)
6. Click Pay
7. ✅ Subscription activated!
```

---

## That's It! 🚀

Your Stripe checkout is now **fully functional**!

Users can:
- ✅ Click subscribe
- ✅ Pay with Stripe
- ✅ Get unlimited access automatically

**See `STRIPE_SETUP_GUIDE.md` for detailed instructions**

