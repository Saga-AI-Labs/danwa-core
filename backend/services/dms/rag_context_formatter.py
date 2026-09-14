"""RAG context formatter — formats retrieved chunks for LLM prompts.

Migrated from src/dms/rag_context_formatter.py. Default max_chars increased to 50,000.
"""

import logging
from typing import Any

logger = logging.getLogger(__name__)

# ~25,000 tokens — fits in most context windows while leaving room for
# system prompt, user prompt, and agent output. Callers can override
# with max_chars for explicit document selections.
DEFAULT_MAX_CHARS = 100_000


class RAGContextFormatter:
    """Formats RAG chunks into a readable string for LLM context injection."""

    def format(self, chunks: list[dict[str, Any]], max_chars: int | None = None) -> str:
        """Format chunks into a single context string.

        Args:
            chunks: List of chunk dicts with 'text' and 'metadata' keys.
            max_chars: Maximum character count. Defaults to 50,000 (~12,500 tokens).

        Returns:
            Formatted context string, truncated at chunk boundaries if necessary.
        """
        if not chunks:
            return ""

        effective_max = max_chars or DEFAULT_MAX_CHARS

        formatted_parts = []
        total_len = 0
        included = 0
        for idx, chunk in enumerate(chunks, start=1):
            text = chunk.get("text", "")
            metadata = chunk.get("metadata", {})
            file_name = metadata.get("file_name", "Unknown")
            formatted = f"[Document {idx} from {file_name}]: {text}\n\n"
            # Truncate at chunk boundaries — never mid-text
            if total_len + len(formatted) > effective_max:
                break
            formatted_parts.append(formatted)
            total_len += len(formatted)
            included = idx

        full_context = "".join(formatted_parts)

        if included < len(chunks):
            remaining = len(chunks) - included
            full_context += f"\n[... {remaining} more document section(s) truncated to fit context window]\n"

        return full_context
