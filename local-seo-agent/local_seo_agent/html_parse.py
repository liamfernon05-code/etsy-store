"""Stdlib HTML -> PageData. No third-party parser (every direct dependency must have >5k GitHub stars)."""

from __future__ import annotations

import json
import re
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit

from .models import PageData, clean

_SKIP = {"script", "style", "noscript", "template", "svg"}
_VOID_NO_END = {"br", "img", "meta", "link", "input", "hr"}


class _Extractor(HTMLParser):
    def __init__(self, base_url: str):
        super().__init__(convert_charrefs=True)
        self.base = base_url
        self.title = ""
        self.meta: dict[str, str] = {}
        self.canonical = ""
        self.lang = ""
        self.h1: list[str] = []
        self.h2: list[str] = []
        self.links: list[str] = []
        self.tel: list[str] = []
        self.images = 0
        self.images_missing_alt = 0
        self.scripts = 0
        self.jsonld_raw: list[str] = []
        self.text_parts: list[str] = []
        self._stack: list[str] = []
        self._buf: list[str] | None = None
        self._buf_tag = ""
        self._ld = False
        self._in_title = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        a = {k.lower(): (v or "") for k, v in attrs}
        if tag == "html":
            self.lang = a.get("lang", "")
        elif tag == "title":
            self._in_title = True
        elif tag == "meta":
            key = (a.get("name") or a.get("property") or a.get("http-equiv") or "").lower()
            if key and key not in self.meta:
                self.meta[key] = a.get("content", "")
        elif tag == "link" and "canonical" in a.get("rel", "").lower().split():
            self.canonical = a.get("href", "")
        elif tag == "a" and a.get("href"):
            href = a["href"].strip()
            if href.lower().startswith("tel:"):
                self.tel.append(href[4:])
            elif not href.lower().startswith(("mailto:", "javascript:", "#", "sms:")):
                self.links.append(urljoin(self.base, href).split("#")[0])
        elif tag == "img":
            self.images += 1
            if not a.get("alt", "").strip():
                self.images_missing_alt += 1
        elif tag == "script":
            self.scripts += 1
            if a.get("type", "").lower() == "application/ld+json":
                self._ld = True
                self.jsonld_raw.append("")
        elif tag in ("h1", "h2"):
            self._buf, self._buf_tag = [], tag
        if tag not in _VOID_NO_END:
            self._stack.append(tag)

    def handle_endtag(self, tag: str) -> None:
        if tag == "title":
            self._in_title = False
        elif tag == "script":
            self._ld = False
        elif tag in ("h1", "h2") and self._buf is not None and self._buf_tag == tag:
            text = clean(" ".join(self._buf), 200)
            if text:
                (self.h1 if tag == "h1" else self.h2).append(text)
            self._buf = None
        for i in range(len(self._stack) - 1, -1, -1):
            if self._stack[i] == tag:
                del self._stack[i:]
                break

    def handle_data(self, data: str) -> None:
        if self._ld and self.jsonld_raw:
            self.jsonld_raw[-1] += data
            return
        if self._in_title:
            self.title += data
        if any(t in _SKIP for t in self._stack):
            return
        if self._buf is not None:
            self._buf.append(data)
        self.text_parts.append(data)


def parse_html(url: str, html: str, status: int = 200, headers: dict[str, str] | None = None) -> PageData:
    ex = _Extractor(url)
    ex.feed(html)
    ex.close()
    jsonld: list[dict] = []
    errors = 0
    for raw in ex.jsonld_raw:
        try:
            obj = json.loads(raw)
        except ValueError:
            errors += 1
            continue
        items = obj if isinstance(obj, list) else [obj]
        jsonld.extend(i for i in items if isinstance(i, dict))
    text = clean(" ".join(ex.text_parts), 20_000)
    host = (urlsplit(url).hostname or "").removeprefix("www.")
    internal = []
    seen: set[str] = set()
    for link in ex.links:
        h = (urlsplit(link).hostname or "").removeprefix("www.")
        if h == host and link not in seen and urlsplit(link).scheme in ("http", "https"):
            seen.add(link)
            internal.append(link)
    return PageData(
        url=url,
        final_url=url,
        status=status,
        bytes=len(html.encode("utf-8", errors="replace")),
        headers={k: v for k, v in (headers or {}).items() if k in ("x-robots-tag", "content-type", "link")},
        title=clean(ex.title, 300),
        meta_description=clean(ex.meta.get("description", ""), 500),
        h1=ex.h1,
        h2=ex.h2[:30],
        canonical=ex.canonical.strip(),
        robots_meta=ex.meta.get("robots", "").lower(),
        viewport="viewport" in ex.meta,
        lang=ex.lang,
        jsonld=jsonld,
        jsonld_errors=errors,
        internal_links=internal[:300],
        tel_links=ex.tel[:20],
        images=ex.images,
        images_missing_alt=ex.images_missing_alt,
        scripts=ex.scripts,
        text=text,
        word_count=len(re.findall(r"\w+", text)),
    )
