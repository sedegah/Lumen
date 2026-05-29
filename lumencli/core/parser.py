from dataclasses import dataclass, field
from typing import Optional
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup, NavigableString, Tag


# ─── Data Structures ───────────────────────────────────────────

@dataclass
class LinkItem:
    """A single extracted link with its number and URL."""
    number: int
    text: str
    url: str


@dataclass
class ContentBlock:
    """A block of rendered content for display."""
    kind: str  # "heading", "paragraph", "code", "list", "link_ref", "hr", "table", "blockquote"
    text: str
    level: int = 0  # heading level (1-6), list nesting depth


@dataclass
class ParsedPage:
    """The result of parsing an HTML page."""
    title: str = ""
    url: str = ""
    blocks: list[ContentBlock] = field(default_factory=list)
    links: list[LinkItem] = field(default_factory=list)

    @property
    def link_count(self) -> int:
        return len(self.links)

    def get_link_url(self, number: int) -> Optional[str]:
        """Get the URL for a given link number."""
        for link in self.links:
            if link.number == number:
                return link.url
        return None


# ─── Tags to skip entirely ─────────────────────────────────────

SKIP_TAGS = {
    "script", "style", "noscript", "iframe", "svg", "path",
    "meta", "link", "head", "button", "input", "select",
    "textarea", "form", "nav", "footer", "aside", "figure",
    "figcaption", "picture", "source", "video", "audio",
    "canvas", "map", "area",
}

HEADING_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6"}
BLOCK_TAGS = {"p", "div", "section", "article", "main", "header"}
LIST_TAGS = {"ul", "ol"}


# ─── Parser ────────────────────────────────────────────────────

class HTMLParser:
    """
    Parses HTML into structured ContentBlocks and a link registry.
    """

    def __init__(self, html: str, base_url: str = ""):
        self.html = html
        self.base_url = base_url
        self._link_counter = 0
        self._links: list[LinkItem] = []
        self._blocks: list[ContentBlock] = []
        self._seen_texts: set[str] = set()  # deduplicate

    def parse(self) -> ParsedPage:
        """Parse the HTML and return a ParsedPage."""
        soup = BeautifulSoup(self.html, "html.parser")

        # Extract title
        title = ""
        title_tag = soup.find("title")
        if title_tag and title_tag.string:
            title = title_tag.string.strip()

        # Find the main content area, falling back to body
        content = (
            soup.find("main")
            or soup.find("article")
            or soup.find("div", {"id": "content"})
            or soup.find("div", {"id": "mw-content-text"})
            or soup.find("div", {"role": "main"})
            or soup.find("body")
            or soup
        )

        self._walk(content)

        return ParsedPage(
            title=title,
            url=self.base_url,
            blocks=self._blocks,
            links=self._links,
        )

    def _resolve_url(self, href: str) -> str:
        """Resolve a relative URL against the base URL."""
        if not href or href.startswith(("#", "javascript:", "mailto:")):
            return ""
        if href.startswith(("http://", "https://")):
            return href
        return urljoin(self.base_url, href)

    def _register_link(self, text: str, href: str) -> int:
        """Register a link and return its number."""
        url = self._resolve_url(href)
        if not url:
            return 0
        self._link_counter += 1
        self._links.append(LinkItem(
            number=self._link_counter,
            text=text.strip() or url,
            url=url,
        ))
        return self._link_counter

    def _clean_text(self, text: str) -> str:
        """Clean and normalize whitespace in text."""
        # Collapse whitespace runs
        parts = text.split()
        return " ".join(parts)

    def _add_block(self, kind: str, text: str, level: int = 0):
        """Add a content block, skipping empties and near-duplicates."""
        text = self._clean_text(text)
        if not text or len(text) < 2:
            return
        # Deduplicate very short repeated fragments
        sig = text[:80].lower()
        if sig in self._seen_texts and len(text) < 100:
            return
        self._seen_texts.add(sig)
        self._blocks.append(ContentBlock(kind=kind, text=text, level=level))

    def _extract_text(self, tag: Tag) -> str:
        """Extract visible text from a tag, ignoring nested block elements."""
        parts = []
        for child in tag.children:
            if isinstance(child, NavigableString):
                parts.append(str(child))
            elif isinstance(child, Tag):
                if child.name in SKIP_TAGS:
                    continue
                if child.name == "br":
                    parts.append("\n")
                elif child.name == "a":
                    link_text = child.get_text(strip=True)
                    href = child.get("href", "")
                    if link_text and href:
                        num = self._register_link(link_text, href)
                        if num:
                            parts.append(f"{link_text} [{num}]")
                        else:
                            parts.append(link_text)
                    elif link_text:
                        parts.append(link_text)
                elif child.name in ("strong", "b"):
                    parts.append(child.get_text(strip=True))
                elif child.name in ("em", "i"):
                    parts.append(child.get_text(strip=True))
                elif child.name in ("code", "kbd"):
                    parts.append(f"`{child.get_text(strip=True)}`")
                elif child.name == "span":
                    parts.append(self._extract_text(child))
                elif child.name not in HEADING_TAGS and child.name not in BLOCK_TAGS:
                    parts.append(child.get_text(strip=True))
        return " ".join(parts)

    def _walk(self, element):
        """Recursively walk the DOM tree and extract content blocks."""
        if element is None:
            return

        for child in element.children:
            if isinstance(child, NavigableString):
                text = str(child).strip()
                if text and len(text) > 2:
                    self._add_block("paragraph", text)
                continue

            if not isinstance(child, Tag):
                continue

            tag_name = child.name

            # Skip invisible / non-content tags
            if tag_name in SKIP_TAGS:
                continue

            # Headings
            if tag_name in HEADING_TAGS:
                level = int(tag_name[1])
                text = child.get_text(strip=True)
                # Also extract any links inside headings
                for a in child.find_all("a", href=True):
                    link_text = a.get_text(strip=True)
                    if link_text:
                        self._register_link(link_text, a["href"])
                self._add_block("heading", text, level=level)

            # Paragraphs
            elif tag_name == "p":
                text = self._extract_text(child)
                self._add_block("paragraph", text)

            # Preformatted / code blocks
            elif tag_name in ("pre", "code"):
                text = child.get_text(strip=False)
                self._add_block("code", text.strip())

            # Blockquotes
            elif tag_name == "blockquote":
                text = self._extract_text(child)
                self._add_block("blockquote", text)

            # Horizontal rules
            elif tag_name == "hr":
                self._add_block("hr", "─" * 50)

            # Lists
            elif tag_name in LIST_TAGS:
                for li in child.find_all("li", recursive=False):
                    text = self._extract_text(li)
                    self._add_block("list", text)

            # Definition lists
            elif tag_name == "dl":
                for dt in child.find_all("dt", recursive=False):
                    text = self._extract_text(dt)
                    self._add_block("heading", text, level=4)
                for dd in child.find_all("dd", recursive=False):
                    text = self._extract_text(dd)
                    self._add_block("paragraph", text)

            # Tables — simplified: extract rows as text
            elif tag_name == "table":
                self._parse_table(child)

            # Standalone links (not inside paragraphs)
            elif tag_name == "a":
                link_text = child.get_text(strip=True)
                href = child.get("href", "")
                if link_text and href:
                    num = self._register_link(link_text, href)
                    if num:
                        self._add_block("link_ref", f"[{num}] {link_text}")

            # Generic block containers — recurse
            elif tag_name in BLOCK_TAGS or tag_name in (
                "section", "article", "main", "header", "details", "summary"
            ):
                self._walk(child)

            # Other tags — try to extract any meaningful text
            else:
                if child.get_text(strip=True):
                    self._walk(child)

    def _parse_table(self, table_tag: Tag):
        """Extract a table into content blocks."""
        rows = table_tag.find_all("tr")
        if not rows:
            return

        self._add_block("hr", "─" * 50)

        for row in rows[:30]:  # limit rows to avoid enormous tables
            cells = row.find_all(["th", "td"])
            cell_texts = []
            for cell in cells:
                text = self._extract_text(cell)
                if text:
                    cell_texts.append(text)
            if cell_texts:
                self._add_block("paragraph", " │ ".join(cell_texts))

        self._add_block("hr", "─" * 50)


def parse_html(html: str, base_url: str = "") -> ParsedPage:
    """
    Convenience function: parse HTML and return a ParsedPage.

    Args:
        html: Raw HTML string.
        base_url: Base URL for resolving relative links.

    Returns:
        ParsedPage with extracted content blocks and links.
    """
    parser = HTMLParser(html, base_url)
    return parser.parse()
