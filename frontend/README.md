# Frontend - Streamlit UI

This repository includes a Streamlit-based frontend demo that provides the full user workflow: upload documents, generate draft knowledge articles, edit/save drafts, publish to the global knowledge library, and use the Insight Chat.

Quick notes
- The frontend is a demo UI intended for evaluators and business users.
- The frontend talks to the backend API. Configure the backend URL via the `API_BASE_URL` environment variable (e.g. `http://127.0.0.1:8000/api/v1` or the deployed backend URL).
- Generative features (automated draft generation and Insight Chat) are implemented in the backend and rely on an external LLM. Set `OPENROUTER_API_KEY` in the backend environment to enable these features.

Run locally
1. Start the backend (see `backend/README.md` for setup and env vars).
2. From the repository root run:

```bash
pip install -r frontend/requirements.txt
streamlit run frontend/streamlit_app.py
```

Configuration
- `API_BASE_URL` — the backend API base (required for the frontend to call the API).

Security & production notes
- The frontend itself does not call the LLM directly; the backend makes LLM calls and requires `OPENROUTER_API_KEY`. Do not store LLM provider keys in client-side code.
- For production, run the frontend behind HTTPS and configure CORS and auth on the backend.

Contact
For questions about the demo or deployment, see `DEPLOY_RENDER.md` or the top-level `README.md`.
