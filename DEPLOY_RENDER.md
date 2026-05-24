Render deployment guide
======================

This project can be deployed to Render as two services:

- `knowledge-backend` — FastAPI REST API (backend)
- `knowledge-frontend` — Streamlit UI (frontend)

Files added to this repo to support Render:

- `backend/Dockerfile` — container for the FastAPI backend
- `frontend/Dockerfile` — container for the Streamlit frontend
- `frontend/requirements.txt` — minimal deps for the frontend container
- `render.yaml` — Render service manifest (optional, for Render's Infrastructure as Code)

Quick steps (Render dashboard)
-------------------------------

1. Create a new GitHub repo (or use this one) and push the code.
2. In Render dashboard, create a new service and choose "Web Service".
   - Connect your GitHub repository and pick the branch.
   - Select "Docker" as the environment and point the Dockerfile to `backend/Dockerfile` for the backend service.
   - Expose port: Render sets `$PORT` automatically — the provided Dockerfile honors `$PORT`.
3. Add environment variables for the backend service (in Render service settings):
   - `DATABASE_URL` — optional; default uses a local SQLite file (not persistent across deploys). For production provide a managed Postgres URL.
   - `OPENROUTER_API_KEY` — optional; required if you want the Insight Chat to call OpenRouter/LLM.
4. Create a second Web Service for the frontend:
   - Use `frontend/Dockerfile` as the Dockerfile path.
   - Add environment variable `API_BASE_URL` pointing to the backend URL, e.g. `https://knowledge-backend.onrender.com/api/v1`.

Notes & recommendations
-----------------------

- Persistent storage: the default SQLite file is stored in the container filesystem and is ephemeral on Render. For real deployments use a managed database and set `DATABASE_URL` to a Postgres instance.
- Asset storage: uploaded files and generated assets are stored under `backend/uploads` and `backend/knowledge_base/assets` in the container. For persistent assets, configure an object store (S3) and update `storage.py` accordingly.
- LLM provider: the Insight Chat calls an external provider via `OPENROUTER_API_KEY` — set this secret in Render to enable chat generation.
 - LLM provider: the Insight Chat and the automated knowledge-drafting feature call an external LLM (the code uses OpenRouter by default). Set `OPENROUTER_API_KEY` in Render to enable generative responses for both chat and KB generation.
- Healthcheck: backend exposes `/health` for status checks.

Automated deploy via `render.yaml`
---------------------------------

Push `render.yaml` to your repo and use Render's "Create from YAML" feature to create both services in one step. After creation, set the environment variables described above.

If you want, I can:

- Create a simple `docker-compose.yml` for local testing of both services before pushing.
- Add CI steps to build and push images automatically.
