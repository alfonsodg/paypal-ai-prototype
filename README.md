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

## LLM provider

Default uses OpenDesign (`https://amr-link.open-design.ai/v1`, model `deepseek-v4.1-flash`).
Set `OPENAI_API_KEY`, `OPENAI_BASE_URL`, `LLM_MODEL` in `.env`.
Any OpenAI-compatible endpoint works.

## PayPal setup

1. Create a sandbox app at <https://developer.paypal.com/dashboard/applications/sandbox>
2. Copy Client ID and Secret to `.env` (`PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET`)
3. Set `PAYPAL_MODE=sandbox`
4. (Optional) Configure webhook and set `PAYPAL_WEBHOOK_ID`

## License

MIT — see LICENSE.
