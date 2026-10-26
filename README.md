# PayPal AI Hackathon — Prototype (unnamed)

Provisional repository. Smart invoice & cashflow copilot: generate invoices from
natural conversation, send via PayPal, track payments, and project cash flow.

## Status

Work in progress. Run instructions will be finalized before submission.

## Quick start (dev)

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp ../.env.example ../.env   # fill real values
uvicorn app.main:app --reload --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

## License

MIT — see LICENSE.
