"""TeX/LaTeX parser — converts .tex files to plain text using pandoc.

Handles mathematical formulas by rendering them as Unicode symbols.
Requires pandoc (system package) and pypandoc (Python wrapper).
"""

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def parse_tex(file_path: str | Path) -> str:
    """Parse a .tex/.latex file and return plain text with Unicode math.

    Uses pandoc for conversion. Math formulas are rendered as Unicode
    symbols (e.g. $E = mc^2$ → E = mc², $$\\int_0^\\infty e^{-x}dx$$ → ∫₀^∞e^(-x)dx).

    Falls back to reading as plain text if pandoc is unavailable.

    Args:
        file_path: Path to the .tex file.

    Returns:
        Extracted plain text content.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")

    try:
        import pypandoc

        text = pypandoc.convert_file(
            str(path),
            "plain",
            format="latex",
            extra_args=["--wrap=none"],
        )
        return text.strip()
    except ImportError:
        logger.warning("pypandoc not available, reading .tex as plain text")
        return path.read_text(encoding="utf-8", errors="ignore")
    except Exception as e:
        logger.warning("pandoc conversion failed for %s: %s. Reading as plain text.", path.name, e)
        return path.read_text(encoding="utf-8", errors="ignore")


def generate_tex(content: str, title: str = "", author: str = "") -> str:
    """Generate a .tex document from plain text or markdown content.

    Converts the input content to LaTeX format using pandoc, wrapping
    in a complete document structure with optional title/author.

    Args:
        content: Plain text or markdown content.
        title: Optional document title.
        author: Optional document author.

    Returns:
        Complete .tex document string.
    """
    try:
        import pypandoc

        # Convert body content to LaTeX
        body = pypandoc.convert_text(
            content,
            "latex",
            format="markdown",
            extra_args=["--wrap=none"],
        ).strip()

        # Build complete document with metadata in preamble
        parts = [
            r"\documentclass{article}",
            r"\usepackage{amsmath}",
            r"\usepackage{amssymb}",
        ]
        if title:
            parts.append(rf"\title{{{title}}}")
        if author:
            parts.append(rf"\author{{{author}}}")
        parts.append(r"\begin{document}")
        if title or author:
            parts.append(r"\maketitle")
        parts.append(body)
        parts.append(r"\end{document}")
        return "\n\n".join(parts)
    except ImportError:
        logger.warning("pypandoc not available, generating minimal .tex")
        parts = [
            r"\documentclass{article}",
            r"\usepackage{amsmath}",
            r"\usepackage{amssymb}",
            r"\begin{document}",
        ]
        if title:
            parts.append(rf"\title{{{title}}}")
        if author:
            parts.append(rf"\author{{{author}}}")
        if title or author:
            parts.append(r"\maketitle")
        parts.append(content)
        parts.append(r"\end{document}")
        return "\n\n".join(parts)
