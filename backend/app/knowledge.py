from __future__ import annotations

import json
import os
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import requests
from dotenv import load_dotenv
from langchain.chains.summarize import load_summarize_chain
from langchain_core.documents import Document
from langchain_core.language_models.llms import LLM
from langchain_core.prompts import PromptTemplate

from .chunking import chunk_and_save, chunk_text
from .config import CHUNKS_DIR, EXTRACTED_DIR
from .storage import save_knowledge_json


DEFAULT_MODEL = "openai/gpt-oss-120b:free"


TOKEN_LIMIT_HINTS = (
    "maximum context",
    "context length",
    "context window",
    "too many tokens",
    "token limit",
    "input too long",
    "prompt is too long",
    "exceeds context",
    "context_length",
)


class TokenLimitError(RuntimeError):
    pass


@dataclass
class KnowledgeResult:
    title: str
    content: str


class OpenRouterLLM(LLM):
    model_name: str = DEFAULT_MODEL
    temperature: float = 0.1

    @property
    def _llm_type(self) -> str:
        return "openrouter"

    def _call(self, prompt: str, stop: List[str] | None = None) -> str:
        load_dotenv()

        api_key = os.getenv("OPENROUTER_API_KEY")

        if not api_key:
            raise RuntimeError(
                "OPENROUTER_API_KEY is missing in environment or .env file"
            )

        payload = {
            "model": self.model_name,
            "messages": [{"role": "user", "content": prompt}],
            "reasoning": {"enabled": True},
            "temperature": self.temperature,
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
            message = response.text

            if _is_token_limit_error(message):
                raise TokenLimitError(message)

            raise RuntimeError(
                f"OpenRouter error {response.status_code}: {message}"
            )

        data = response.json()

        return data["choices"][0]["message"]["content"]


INITIAL_PROMPT = PromptTemplate(
    input_variables=["text"],
    template="""
You are a knowledge-base generation system.

Generate a structured explanation using ONLY the information
present in the provided transcript.

Rules:
- Do NOT add external knowledge.
- Do NOT hallucinate missing details.
- Do NOT invent code, APIs, workflows, or architecture.
- Do NOT add examples unless explicitly mentioned.
- Organize the content into clear sections.
- Remove conversational filler and repetition.
- Preserve important technical and operational details.
- Keep the explanation concise, accurate, and well-structured.

Return ONLY valid JSON in this format:

{{
  "title": "...",
  "content": "..."
}}

Transcript:
{text}
""",
)


REFINE_PROMPT = PromptTemplate(
    input_variables=["existing_answer", "text"],
    template="""
Refine the existing structured explanation using ONLY the new transcript content.

Rules:
- Do NOT add external knowledge.
- Do NOT hallucinate missing details.
- Preserve existing valid information.
- Add only information explicitly present in the new chunk.
- Remove redundancy if needed.
- Keep the document structured and concise.
- Maintain consistent formatting.

Return ONLY valid JSON in this format:

{{
  "title": "...",
  "content": "..."
}}

Existing explanation:
{existing_answer}

New transcript chunk:
{text}
""",
)

def build_refine_chain(llm: LLM):
    return load_summarize_chain(
        llm=llm,
        chain_type="refine",
        question_prompt=INITIAL_PROMPT,
        refine_prompt=REFINE_PROMPT,
    )


def _is_token_limit_error(message: str) -> bool:
    lowered = message.lower()

    return any(hint in lowered for hint in TOKEN_LIMIT_HINTS)


def parse_json_response(text: str) -> KnowledgeResult:
    try:
        data = json.loads(text)

        return KnowledgeResult(
            title=str(data.get("title", "")).strip(),
            content=str(data.get("content", "")).strip(),
        )

    except json.JSONDecodeError:
        cleaned = text.strip()

        return KnowledgeResult(
            title="Generated Knowledge Base",
            content=cleaned,
        )


def _build_knowledge_payload(
    source: str,
    result: KnowledgeResult,
    raw_response: str,
    steps: List[str],
    chunks: List[Dict[str, str]],
) -> Dict:
    return {
        "source": Path(source).name,
        "title": result.title,
        "content": result.content,
        "raw_response": raw_response,
        "step_outputs": steps,
        "chunk_count": len(chunks),
    }


def generate_explanation_stepwise(
    chunks: List[Dict[str, str]],
    model_name: str = DEFAULT_MODEL,
) -> Tuple[KnowledgeResult, str, List[str]]:

    if not chunks:
        empty = KnowledgeResult(title="", content="")

        return empty, "", []

    llm = OpenRouterLLM(model_name=model_name)

    chain = build_refine_chain(llm)

    step_outputs: List[str] = []

    if hasattr(chain, "initial_llm_chain") and hasattr(
        chain,
        "refine_llm_chain",
    ):

        current = chain.initial_llm_chain.predict(
            text=chunks[0]["content"]
        )

        step_outputs.append(current)

        for chunk in chunks[1:]:

            current = chain.refine_llm_chain.predict(
                existing_answer=current,
                text=chunk["content"],
            )

            step_outputs.append(current)

        result = parse_json_response(current)

        return result, current, step_outputs

    documents = [
        Document(page_content=chunk["content"])
        for chunk in chunks
    ]

    response = chain.invoke(
        {"input_documents": documents}
    )["output_text"]

    result = parse_json_response(response)

    return result, response, [response]


def generate_explanation(
    chunks: List[Dict[str, str]],
    model_name: str = DEFAULT_MODEL,
) -> Tuple[KnowledgeResult, str]:

    result, response, _steps = generate_explanation_stepwise(
        chunks,
        model_name=model_name,
    )

    return result, response


def generate_explanation_auto(
    text: str,
    source: str,
    model_name: str = DEFAULT_MODEL,
    chunk_size: int = 1200,
    chunk_overlap: int = 150,
    max_parts: int = 10,
    save_output: bool = True,
) -> Tuple[
    KnowledgeResult,
    str,
    List[str],
    List[Dict[str, str]],
]:

    full_chunk = [
        {
            "chunk_id": 1,
            "source": source,
            "content": text,
        }
    ]

    try:
        result, response, steps = generate_explanation_stepwise(
            full_chunk,
            model_name=model_name,
        )
        if save_output:
            payload = _build_knowledge_payload(
                source=source,
                result=result,
                raw_response=response,
                steps=steps,
                chunks=full_chunk,
            )
            save_knowledge_json(source, payload)
        return result, response, steps, full_chunk

    except TokenLimitError:
        pass

    text_length = max(1, len(text))

    for parts in range(2, max_parts + 1):

        target_size = max(
            chunk_size,
            math.ceil(text_length / parts),
        )

        overlap = min(
            chunk_overlap,
            max(0, target_size // 5),
        )

        chunks = chunk_text(
            text,
            source=source,
            chunk_size=target_size,
            chunk_overlap=overlap,
        )

        try:
            result, response, steps = generate_explanation_stepwise(
                chunks,
                model_name=model_name,
            )
            if save_output:
                payload = _build_knowledge_payload(
                    source=source,
                    result=result,
                    raw_response=response,
                    steps=steps,
                    chunks=chunks,
                )
                save_knowledge_json(source, payload)
            return result, response, steps, chunks

        except TokenLimitError:
            continue

    raise RuntimeError(
        "Token limit errors persisted after splitting the transcript."
    )


def load_chunk_files() -> List[Path]:

    files = sorted(CHUNKS_DIR.glob("*_chunks.json"))

    if files:
        return files

    extracted_files = sorted(EXTRACTED_DIR.glob("*.json"))

    for extracted_file in extracted_files:
        chunk_and_save(extracted_file)

    return sorted(CHUNKS_DIR.glob("*_chunks.json"))


def generate_and_save_knowledge(
    chunk_file: Path,
    model_name: str = DEFAULT_MODEL,
) -> Path:

    payload = json.loads(
        chunk_file.read_text(encoding="utf-8")
    )

    chunks = payload.get("chunks", [])

    source = payload.get(
        "source",
        chunk_file.stem,
    )

    result, raw_response = generate_explanation(
        chunks,
        model_name=model_name,
    )

    output = {
        "source": source,
        "title": result.title,
        "content": result.content,
        "raw_response": raw_response,
    }

    return save_knowledge_json(
        chunk_file.name,
        output,
    )