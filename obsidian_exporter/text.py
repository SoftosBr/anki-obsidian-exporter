from __future__ import annotations

import re
from html import unescape
from html.parser import HTMLParser


MEDIA_TAGS = {"audio", "embed", "iframe", "img", "object", "source", "video"}
BLOCK_TAGS = {"blockquote", "div", "li", "ol", "p", "pre", "section", "table", "tr", "ul"}


class _TextOnlyParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=False)
        self.parts: list[str] = []
        self.skip_depth = 0
        self.link_stack: list[str | None] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        tag = tag.lower()
        if tag in MEDIA_TAGS:
            self.skip_depth += 1
            return
        if self.skip_depth:
            return
        if tag == "br":
            self.parts.append("\n")
        elif tag in {"b", "strong"}:
            self.parts.append("**")
        elif tag in {"i", "em"}:
            self.parts.append("*")
        elif tag == "a":
            href = _external_href(attrs)
            self.link_stack.append(href)
            if href:
                self.parts.append("[")
        elif tag in BLOCK_TAGS and self.parts:
            self.parts.append("\n\n")

    def handle_endtag(self, tag: str) -> None:
        tag = tag.lower()
        if tag in MEDIA_TAGS and self.skip_depth:
            self.skip_depth -= 1
            return
        if self.skip_depth:
            return
        if tag in {"b", "strong"}:
            self.parts.append("**")
        elif tag in {"i", "em"}:
            self.parts.append("*")
        elif tag == "a":
            href = self.link_stack.pop() if self.link_stack else None
            if href:
                self.parts.append(f"]({href})")
        elif tag in BLOCK_TAGS:
            self.parts.append("\n\n")

    def handle_data(self, data: str) -> None:
        if not self.skip_depth:
            self.parts.append(data)

    def handle_entityref(self, name: str) -> None:
        if not self.skip_depth:
            self.parts.append(unescape(f"&{name};"))

    def handle_charref(self, name: str) -> None:
        if not self.skip_depth:
            self.parts.append(unescape(f"&#{name};"))

    def text(self) -> str:
        return "".join(self.parts)


def html_to_text(value: str) -> str:
    """Convert Anki field HTML into text-only Markdown-friendly content."""
    without_sound = re.sub(r"\[sound:[^\]]+\]", "", value or "", flags=re.IGNORECASE)
    parser = _TextOnlyParser()
    parser.feed(without_sound)
    parser.close()
    without_artifacts = _remove_bracket_artifacts(unescape(parser.text()))
    return _normalize_text(without_artifacts)


def _external_href(attrs: list[tuple[str, str | None]]) -> str | None:
    for name, value in attrs:
        if name.lower() == "href" and value and re.match(r"https?://", value, flags=re.IGNORECASE):
            return value
    return None


def _remove_bracket_artifacts(value: str) -> str:
    value = re.sub(r"\[[^\]\n]+\](?!\()(?::;)?", "", value)
    return value


def _normalize_text(value: str) -> str:
    value = value.replace("\r\n", "\n").replace("\r", "\n").replace("\xa0", " ")
    lines = [re.sub(r"[ \t\f\v]+", " ", line).strip() for line in value.split("\n")]

    normalized: list[str] = []
    blank_pending = False
    for line in lines:
        if not line:
            blank_pending = True
            continue
        if blank_pending and normalized:
            normalized.append("")
        normalized.append(line)
        blank_pending = False

    return "\n".join(normalized).strip()


def heading_text(value: str) -> str:
    text = html_to_text(value)
    first_line = next((line.strip() for line in text.splitlines() if line.strip()), "Untitled")
    first_line = re.sub(r"[*_`#>\[\]]", "", first_line)
    return first_line[:120].strip() or "Untitled"
