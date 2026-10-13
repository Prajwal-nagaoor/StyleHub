# StyleHub — full-stack project

This folder contains your original FastAPI backend and a new React + Vite frontend. **The existing Python backend source files were copied without editing.** The frontend is adapted to the routes currently declared in that backend, including route names that are missing a slash.

## 1. Start the backend

Open a terminal in the `StyleHub` project root (the folder containing `fast_api/`) and activate your existing virtual environment:

```bat
myenv\Scripts\activate
```

Install backend requirements if needed, then start FastAPI:

```bat
python -m uvicorn fast_api.main:app --reload
```

Open `http://127.0.0.1:8000/docs` to check the API.

### Environment variables

The original `.env` file is intentionally not included in this shareable ZIP because it contains Stripe secret credentials. Create a local `.env` in the project root with your own values:

```dotenv
STRIPE_SECRET_KEY=sk_test_your_own_test_secret_key
STRIPE_WEBHOOK_SECRET=whsec_your_own_webhook_secret
```

Use your own Stripe test credentials and keep `.env` private. The existing backend also has a hard-coded JWT signing key in `fast_api/auth.py`; that source was preserved as requested. For anything beyond local learning, replace secrets securely yourself before deployment.

## 2. Start the frontend

Open a second terminal and run:

```bat
cd frontend
copy .env.example .env
npm install
npm run dev
```

Open the Vite URL printed in the terminal, usually `http://localhost:5173`.

Set `VITE_API_BASE_URL` in `frontend/.env` if your API uses a different local address. To use the Stripe payment form, set `VITE_STRIPE_PUBLISHABLE_KEY` to your Stripe **publishable** test key (`pk_test_...`). Never put `sk_test_...` in the frontend.

## Included frontend pages

- Responsive fashion-store home page and product collection
- Product details and add-to-cart
- Registration and login with bearer-token storage
- Profile and seller product studio
- Cart quantity changes and item removal
- Order history, cancellation and Stripe Payment Element UI
- Responsive mobile navigation and status/error feedback

## Backend integration notes

The frontend intentionally uses the route paths present in the supplied backend. Some backend route decorators currently concatenate paths without a slash (for example, the product-list route). The frontend maps to those existing paths rather than modifying backend code. If a backend route is later corrected, update `src/api.js` accordingly.

The backend currently calculates order totals using the last cart item rather than the sum of all cart items. That issue was left untouched to respect the request not to change backend files. Test with care and correct the backend separately when you are ready.

The checkout UI can create a PaymentIntent and collect Stripe test payment details when the publishable key is configured. Successful payment-status updates still depend on the backend webhook and Stripe CLI listener being configured correctly.

## Included files and safety

- Existing `fast_api/` source files and `checkout.html` are preserved byte-for-byte.
- The existing SQLite database file is included as supplied.
- `.env`, `.git/`, Python virtual environments and caches are not included. This avoids distributing private keys and unnecessary repository/runtime files.
