from __future__ import annotations

import json
import logging
import os
from typing import Dict, List

import requests
from dotenv import load_dotenv

from .prompts import build_prompt
from .retrieval import retrieve
from .embedding import LocalEmbedder

logger = logging.getLogger("rag.chatbot")


def _call_openrouter(prompt: str, model: str) -> str:
    load_dotenv()
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise RuntimeError("OPENROUTER_API_KEY is missing in environment or .env file")

    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "reasoning": {"enabled": True},
        "temperature": 0.2,
    }
    response = requests.post(
        url="https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        data=json.dumps(payload),
        timeout=120,
    )
    if response.status_code != 200:
        raise RuntimeError(f"OpenRouter error {response.status_code}: {response.text}")

    data = response.json()
    return data["choices"][0]["message"]["content"]


def answer_query(
    query: str,
    index,
    metadata: List[Dict],
    embedder: LocalEmbedder,
    model: str = "openai/gpt-oss-120b:free",
    top_k: int = 5,
) -> Dict:
    retrieved = retrieve(query, index, metadata, embedder, top_k=top_k)
    prompt = build_prompt(query, retrieved)

    logger.info("Prompt context length: %s", len(prompt))
    response_text = _call_openrouter(prompt, model=model)

    return {
        "query": query,
        "retrieved": retrieved,
        "prompt": prompt,
        "response": response_text,
    }
