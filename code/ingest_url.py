#!/usr/bin/env python3
"""Optional support-site ingester for future product use.

This file is intentionally separate from the hackathon prediction path. The
challenge runner uses `main.py --data data`, which reads only the provided local
corpus. Product users can run this utility to build a local corpus from a public
support page, then point `main.py --data` at the generated directory.
"""
from __future__ import annotations

import argparse
import html.parser
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import deque
from dataclasses import dataclass
from pathlib import Path

USER_AGENT = "SupportTriageCorpusBuilder/0.1 (+local CLI)"
SKIP_EXTENSIONS = (
    ".css", ".js", ".png", ".jpg", ".jpeg", ".gif", ".svg", ".webp", ".ico",
    ".pdf", ".zip", ".gz", ".mp4", ".mp3", ".woff", ".woff2", ".ttf",
)


@dataclass(frozen=True)
class Page:
    url: str
    title: str
    text: str
    links: list[str]


class ReadableHTMLParser(html.parser.HTMLParser):
    """Small stdlib HTML-to-text/link extractor.

    It is not a browser. It is intentionally deterministic, dependency-free, and
    good enough to turn help-center pages into retrieval documents.
    """

    def __init__(self, base_url: str):
        super().__init__(convert_charrefs=True)
        self.base_url = base_url
        self.title_parts: list[str] = []
        self.text_parts: list[str] = []
        self.links: list[str] = []
        self._tag_stack: list[str] = []
        self._skip_depth = 0
        self._in_title = False

    def handle_starttag(self, tag: str, attrs):
        attrs_dict = dict(attrs)
        tag = tag.lower()
        self._tag_stack.append(tag)
        if tag in {"script", "style", "noscript", "svg"}:
            self._skip_depth += 1
        if tag == "title":
            self._in_title = True
        if tag == "a" and attrs_dict.get("href"):
            self.links.append(urllib.parse.urljoin(self.base_url, attrs_dict["href"]))
        if tag in {"p", "div", "section", "article", "br", "li", "h1", "h2", "h3"}:
            self.text_parts.append("\n")

    def handle_endtag(self, tag: str):
        tag = tag.lower()
        if tag in {"script", "style", "noscript", "svg"} and self._skip_depth:
            self._skip_depth -= 1
        if tag == "title":
            self._in_title = False
        if tag in {"p", "div", "section", "article", "li", "h1", "h2", "h3"}:
            self.text_parts.append("\n")
        if self._tag_stack:
            self._tag_stack.pop()

    def handle_data(self, data: str):
        if self._skip_depth:
            return
        cleaned = re.sub(r"\s+", " ", data).strip()
        if not cleaned:
            return
        if self._in_title:
            self.title_parts.append(cleaned)
        self.text_parts.append(cleaned)
        self.text_parts.append(" ")

    def page(self) -> Page:
        title = re.sub(r"\s+", " ", " ".join(self.title_parts)).strip() or "Untitled support page"
        text = re.sub(r"[ \t]+", " ", "".join(self.text_parts))
        text = re.sub(r"\n{3,}", "\n\n", text).strip()
        return Page(self.base_url, title, text, self.links)


def is_crawlable(url: str, root_host: str) -> bool:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme not in {"http", "https"}:
        return False
    if parsed.netloc != root_host:
        return False
    lowered_path = parsed.path.lower()
    if lowered_path.endswith(SKIP_EXTENSIONS):
        return False
    return True


def canonicalize(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    parsed = parsed._replace(fragment="")
    path = parsed.path or "/"
    if path != "/":
        path = path.rstrip("/")
    return urllib.parse.urlunparse(parsed._replace(path=path))


def fetch_page(url: str, timeout: int = 20) -> Page | None:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            content_type = response.headers.get("content-type", "")
            if "text/html" not in content_type and "application/xhtml" not in content_type:
                return None
            raw = response.read(2_000_000)
    except (urllib.error.URLError, TimeoutError, OSError):
        return None
    html = raw.decode("utf-8", errors="ignore")
    parser = ReadableHTMLParser(url)
    parser.feed(html)
    return parser.page()


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", value.lower()).strip("-")
    return slug[:90] or "page"


def write_page(page: Page, output_dir: Path, index: int) -> Path:
    filename = f"{index:04d}-{slugify(page.title)}.md"
    path = output_dir / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(f"# {page.title}\n\nSource: {page.url}\n\n{page.text}\n", encoding="utf-8")
    return path


def crawl(start_url: str, output_dir: Path, max_pages: int = 50, delay: float = 0.2) -> list[Path]:
    start_url = canonicalize(start_url)
    root_host = urllib.parse.urlparse(start_url).netloc
    queue: deque[str] = deque([start_url])
    seen: set[str] = set()
    written: list[Path] = []

    while queue and len(written) < max_pages:
        url = canonicalize(queue.popleft())
        if url in seen or not is_crawlable(url, root_host):
            continue
        seen.add(url)
        page = fetch_page(url)
        if page and len(page.text.split()) >= 30:
            written.append(write_page(page, output_dir, len(written) + 1))
            for link in page.links:
                link = canonicalize(link)
                if link not in seen and is_crawlable(link, root_host):
                    queue.append(link)
        if delay:
            time.sleep(delay)
    return written


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build a local markdown corpus from a public support URL")
    parser.add_argument("--url", required=True, help="Starting support/help-center URL")
    parser.add_argument("--output", required=True, help="Directory to write markdown corpus into")
    parser.add_argument("--max-pages", type=int, default=50, help="Maximum same-domain pages to fetch")
    parser.add_argument("--delay", type=float, default=0.2, help="Delay between requests in seconds")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    written = crawl(args.url, Path(args.output), max_pages=args.max_pages, delay=args.delay)
    print(f"Wrote {len(written)} markdown pages to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
