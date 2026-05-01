"""Corpus loading and chunking."""
from __future__ import annotations

import re
from pathlib import Path

from models import Chunk
from text_utils import tokenize

DOMAIN_ALIASES = {"hackerrank": "HackerRank", "claude": "Claude", "visa": "Visa"}

AREA_MAPPING = {
    "general_help": "general_help",
    "hackerrank_community": "community",
    "privacy_and_legal": "privacy",
    "team_and_enterprise_plans": "team_and_enterprise_plans",
    "pro_and_max_plans": "billing",
    "claude_api_and_console": "claude_api_and_console",
    "amazon_bedrock": "amazon_bedrock",
    "claude_for_education": "claude_for_education",
    "identity_management_sso_jit_scim": "account_management",
    "support": "general_support",
}


def domain_from_path(path: Path) -> str:
    parts = [part.lower() for part in path.parts]
    for key, value in DOMAIN_ALIASES.items():
        if key in parts:
            return value
    return "None"


def product_area_from_path(path: Path) -> str:
    parts = [part.lower().replace("-", "_") for part in path.parts]
    rel = parts[parts.index("data") + 1 :] if "data" in parts else parts
    area = rel[1] if len(rel) >= 2 else "general_support"
    return AREA_MAPPING.get(area, area)


def title_from_markdown(text: str, path: Path) -> str:
    for line in text.splitlines()[:40]:
        if line.startswith("#"):
            return line.lstrip("# ").strip()[:120]
    return path.stem.replace("-", " ").replace("_", " ")


def split_markdown(text: str, max_words: int = 380, overlap: int = 60) -> list[str]:
    text = re.sub(r"\n{3,}", "\n\n", text)
    blocks = re.split(r"(?=\n#{1,3} )", text)
    chunks: list[str] = []
    step = max(1, max_words - overlap)
    for block in blocks:
        words = block.split()
        if not words:
            continue
        if len(words) <= max_words:
            chunks.append(block.strip())
            continue
        for start in range(0, len(words), step):
            chunks.append(" ".join(words[start : start + max_words]).strip())
    return chunks


def load_corpus(data_dir: Path) -> list[Chunk]:
    chunks: list[Chunk] = []
    for path in sorted(data_dir.rglob("*.md")):
        try:
            text = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if not text.strip():
            continue
        title = title_from_markdown(text, path)
        domain = domain_from_path(path)
        product_area = product_area_from_path(path)
        for part in split_markdown(text):
            chunks.append(Chunk(domain, product_area, str(path), title, part, tokenize(f"{title}\n{part}")))
    return chunks
