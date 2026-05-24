from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List

from langchain_text_splitters import MarkdownHeaderTextSplitter

logger = logging.getLogger("rag.chunking")


@dataclass
class KBChunk:
    kb_id: str
    title: str
    section: str
    content: str


def _load_kb_json(path: Path) -> Dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        "kb_id": path.stem,
        "title": str(data.get("title", "")).strip(),
        "content": str(data.get("content", "")).strip(),
    }


def load_kb_files(kb_dir: Path) -> List[Dict]:
    kb_dir = Path(kb_dir)
    files = sorted(kb_dir.glob("*.json"))
    logger.info("KB files found: %s", len(files))
    entries: List[Dict] = []
    for file_path in files:
        entry = _load_kb_json(file_path)
        if not entry["content"]:
            logger.warning("Skipping empty KB content: %s", file_path.name)
            continue
        logger.info("Loaded KB file: %s", file_path.name)
        entries.append(entry)
    return entries


def split_markdown(kb_id: str, title: str, content: str) -> List[KBChunk]:
    splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=[("##", "section"), ("###", "subsection")]
    )
    documents = splitter.split_text(content)
    chunks: List[KBChunk] = []
    for doc in documents:
        section = doc.metadata.get("section") or doc.metadata.get("subsection") or "General"
        chunk_content = doc.page_content.strip()
        if not chunk_content:
            continue
        chunks.append(
            KBChunk(
                kb_id=kb_id,
                title=title or kb_id,
                section=section,
                content=chunk_content,
            )
        )
    logger.info("Split KB '%s' into %s sections", kb_id, len(chunks))
    return chunks


def split_markdown_content(title: str, content: str) -> List[Dict]:
    chunks = split_markdown("kb", title, content)
    return [
        {
            "title": chunk.title,
            "section": chunk.section,
            "content": chunk.content,
        }
        for chunk in chunks
    ]


def build_chunks(kb_dir: Path) -> List[Dict]:
    entries = load_kb_files(kb_dir)
    all_chunks: List[Dict] = []
    for entry in entries:
        chunks = split_markdown(entry["kb_id"], entry["title"], entry["content"])
        for chunk in chunks:
            all_chunks.append(
                {
                    "kb_id": chunk.kb_id,
                    "title": chunk.title,
                    "section": chunk.section,
                    "content": chunk.content,
                }
            )
    logger.info("Total chunks generated: %s", len(all_chunks))
    return all_chunks
