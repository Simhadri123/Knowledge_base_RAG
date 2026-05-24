FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install a small set of frontend deps (Streamlit + requests)
COPY frontend/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# Copy frontend files
COPY frontend /app
COPY backend /app/backend

ENV PYTHONUNBUFFERED=1

# Streamlit listens on $PORT provided by Render
CMD ["sh", "-c", "streamlit run streamlit_app.py --server.port ${PORT:-8501} --server.address 0.0.0.0"]
