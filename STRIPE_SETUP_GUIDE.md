# 🎵 Stripe Integration Setup Guide

## ✅ What's Already Done

Your Django app is **fully configured** for Stripe integration:

- ✅ `StripeAPI` class in `utils.py` - Handles checkout sessions and webhooks
- ✅ Checkout views and API endpoints - Ready to process payments
- ✅ Webhook handler - Automatically activates subscriptions on payment
- ✅ Database models - Purchase and Subscription tracking
- ✅ Settings configured - `SITE_URL`, `STRIPE_PUBLISHABLE_KEY`, `STRIPE_SECRET_KEY`, `STRIPE_WEBHOOK_SECRET`
- ✅ Stripe package installed - `pip install stripe`

---

## 🔑 Step 1: Get Your Stripe API Keys

### Create a Stripe Account (Free)
1. Go to https://dashboard.stripe.com
2. Click **Sign up** (or sign in if you have an account)
3. Complete the registration

### Get Your API Keys
1. In the Stripe Dashboard, click **Developers** (left sidebar)
2. Click **API Keys**
3. You'll see two keys:
   - **Publishable Key** (starts with `pk_test_`)
   - **Secret Key** (starts with `sk_test_`)

**Copy both keys** - you'll need them in the next step.

---

## 🔐 Step 2: Update Your `.env` File

Open `.env` and update it with your Stripe keys:

```env
DJANGO_SECRET_KEY=6@xrwi_8+1q&u_nnb5^#vk!(w+7chgbjf)ow(*be_r9oj3l7p%
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3
SITE_URL=http://127.0.0.1:8000

STRIPE_PUBLISHABLE_KEY=pk_test_YOUR_ACTUAL_KEY_HERE
STRIPE_SECRET_KEY=sk_test_YOUR_ACTUAL_KEY_HERE
STRIPE_WEBHOOK_SECRET=whsec_YOUR_WEBHOOK_SECRET_HERE

FREE_USAGE_LIMIT=10
MONTHLY_PLAN_PRICE=20
YEARLY_PLAN_PRICE=100
```

**Replace:**
- `pk_test_YOUR_ACTUAL_KEY_HERE` with your Publishable Key
- `sk_test_YOUR_ACTUAL_KEY_HERE` with your Secret Key
- `whsec_YOUR_WEBHOOK_SECRET_HERE` with your Webhook Secret (see Step 3)

---

## 🪝 Step 3: Set Up Stripe Webhook

### Create Webhook Endpoint
1. In Stripe Dashboard, go to **Developers** → **Webhooks**
2. Click **Add endpoint**
3. Enter the endpoint URL:
   ```
   http://127.0.0.1:8000/webhook/stripe/
   ```
4. Click **Select events to listen to**
5. Search for and select these events:
   - `checkout.session.completed`
   - `payment_intent.payment_failed`
6. Click **Add endpoint**

### Get Webhook Secret
1. Click on your newly created endpoint
2. Scroll down to **Signing secret**
3. Click **Reveal** to show the secret
4. Copy it (starts with `whsec_`)
5. Paste it in your `.env` file as `STRIPE_WEBHOOK_SECRET`

---

## 🧪 Step 4: Test the Integration

### Test Stripe Keys
1. Restart your Django server (if it's running)
2. Go to http://127.0.0.1:8000/subscribe/
3. Click **Subscribe Monthly** or **Subscribe Yearly**
4. You should see a checkout page with order summary

### Use Stripe Test Card
When redirected to Stripe checkout, use this test card:
- **Card Number:** `4242 4242 4242 4242`
- **Expiry:** Any future date (e.g., `12/25`)
- **CVC:** Any 3 digits (e.g., `123`)
- **Name:** Any name

### Complete Payment
1. Fill in the test card details
2. Click **Pay**
3. You should be redirected back to your app
4. Check your database - subscription should be **active**!

---

## 🔍 Troubleshooting

### "Invalid API Key" Error
- ❌ Your `STRIPE_SECRET_KEY` is wrong or missing
- ✅ Copy it again from Stripe Dashboard
- ✅ Make sure it's in `.env` file
- ✅ Restart Django server

### Webhook Not Working
- ❌ Webhook secret is wrong
- ✅ Go to Stripe Dashboard → Webhooks
- ✅ Copy the correct signing secret
- ✅ Update `.env` with `STRIPE_WEBHOOK_SECRET`

### Checkout URL is None
- ❌ `SITE_URL` is not set in `.env`
- ✅ Add `SITE_URL=http://127.0.0.1:8000` to `.env`
- ✅ Restart Django server

### Payment Succeeds but Subscription Not Activated
- ❌ Webhook endpoint not configured correctly
- ✅ Check Stripe Dashboard → Webhooks
- ✅ Make sure endpoint URL is correct
- ✅ Make sure events are selected

---

## 📊 How It Works

### Payment Flow
```
1. User clicks "Subscribe Monthly/Yearly"
   ↓
2. Django creates Purchase & Subscription records (inactive)
   ↓
3. StripeAPI.create_checkout_session() creates Stripe session
   ↓
4. User redirected to Stripe checkout page
   ↓
5. User enters card details and pays
   ↓
6. Stripe sends webhook to /webhook/stripe/
   ↓
7. Django verifies webhook signature
   ↓
8. Subscription activated automatically
   ↓
9. User has unlimited access!
```

### Key Files
- **`recommender/utils.py`** - `StripeAPI` class handles all Stripe operations
- **`recommender/views.py`** - `checkout()` and `stripe_webhook()` views
- **`recommender/models.py`** - `Purchase` and `Subscription` models
- **`song_recommender/settings.py`** - Stripe configuration

---

## 🎯 What Happens After Payment

### Automatic Subscription Activation
When payment is successful:
1. Webhook is received at `/webhook/stripe/`
2. Signature is verified for security
3. `Subscription.activate()` is called
4. Subscription dates are set:
   - **Monthly:** 30 days from now
   - **Yearly:** 365 days from now
5. User gets unlimited access immediately

### User Benefits
- ✅ Unlimited song searches
- ✅ Unlimited recommendations
- ✅ No daily limit (10 free searches removed)
- ✅ Full access to all features

---

## 💳 Production Checklist

When going live, remember to:

- [ ] Switch to **Live API Keys** (not test keys)
- [ ] Update webhook to production URL
- [ ] Set `DEBUG=False` in `.env`
- [ ] Use a production database (not SQLite)
- [ ] Set up HTTPS (required by Stripe)
- [ ] Use environment variables for all secrets
- [ ] Test with real payments (small amount)

---

## ✅ You're All Set!

Your Stripe integration is **complete and ready to use**!

1. ✅ Add your Stripe keys to `.env`
2. ✅ Set up webhook in Stripe Dashboard
3. ✅ Test with test card `4242 4242 4242 4242`
4. ✅ Users can now subscribe and pay!

**Questions?** Check the troubleshooting section above.

**Need help?** Visit https://stripe.com/docs

