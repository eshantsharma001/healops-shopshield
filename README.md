## Local setup

1. Install Python and create a virtual environment with `python -m venv .venv`.
2. Activate it with `.venv\Scripts\Activate.ps1`.
3. Install dependencies with `python -m pip install -r requirements.txt`.
4. Start the complete system with `python run_all.py`.

The services remain on their existing ports: ShopShield on 5000, Product Service
on 5001, and the HealOps Control Room on 5050. Admin access is at the direct
URL `http://127.0.0.1:5000/admin`.

Set `SHOPSHIELD_SECRET_KEY` to a persistent, randomly generated secret before
deploying so customer sessions survive application restarts. To enable UPI QR
payments, set `SHOPSHIELD_UPI_ID` to the store's actual merchant VPA. The QR is
generated locally. The checkout records a 12-digit UTR for manual reconciliation;
it does not verify payment settlement. Card and NetBanking orders are unavailable
until a payment provider integration is configured. Cash on Delivery remains
available without payment-provider credentials.