SYSTEM_PROMPT = (
    "You are a grounded enterprise assistant. Use ONLY the provided knowledge base context. "
    "If the answer is not present, say you do not have enough information. "
    "Do not invent details. Be concise and structured."
)


def build_prompt(query: str, chunks: list[dict]) -> str:
    context_blocks = []
    for chunk in chunks:
        owner = chunk.get("owner_username", "unknown")
        block = (
            f"[KB: {chunk['title']} | {chunk['section']} | owner: {owner}]\n"
            f"{chunk['content']}"
        )
        context_blocks.append(block)
    context_text = "\n\n".join(context_blocks)

    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"Context:\n{context_text}\n\n"
        f"User question: {query}\n\n"
        f"Answer:"
    )
