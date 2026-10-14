# StyleHub fixes applied

This update focuses only on product-image display and Stripe payment status.

## Changes
- FastAPI now serves the existing `uploads` directory at `/uploads`; product upload logic was not rewritten.
- React now reads `product_image` (with compatibility fallbacks) and builds a URL pointing to the FastAPI server for product cards, details, seller inventory, and cart thumbnails.
- Added an authenticated `/order/confirm-payment` endpoint. After Stripe.js reports a successful PaymentIntent, the backend retrieves the PaymentIntent from Stripe and checks its status, order/user metadata, amount, and currency before marking the order `Paid`.
- The Stripe webhook remains available as an asynchronous backup.
- Fixed order total calculation so a multi-product order adds each line total rather than replacing the total with the last item.
- Product response schema now supports ORM objects and nullable image fields.

## Run locally
1. Copy `.env.example` to `.env` and fill in your own Stripe test secret and webhook secret.
2. In the project root, activate your virtual environment and install backend dependencies from `requirements.txt` if needed.
3. Start the API from the project root:
   `python -m uvicorn fast_api.main:app --reload`
4. In another terminal:
   `cd frontend`
   `npm install`
   Copy `frontend/.env.example` to `frontend/.env` and set `VITE_STRIPE_PUBLISHABLE_KEY` to the matching Stripe test publishable key.
   Then run `npm run dev`.

## Notes
- The archive intentionally excludes the local `.env`, SQLite database, `.git`, `node_modules`, and virtual environment. Your secrets and local database are not included.
- Payment confirmation requires the backend `STRIPE_SECRET_KEY` and frontend publishable key to belong to the same Stripe account and test/live mode.
- For webhook delivery, configure Stripe CLI or your Stripe webhook endpoint to forward `payment_intent.succeeded` and `payment_intent.payment_failed` to `http://127.0.0.1:8000/order/stripe-webhook`, with the matching `STRIPE_WEBHOOK_SECRET`.
