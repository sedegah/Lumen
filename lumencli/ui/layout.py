from rich.console import Console
from rich.rule import Rule

from lumencli.core.parser import ParsedPage
from lumencli.core.fetch import FetchResult
from lumencli.ui.theme import LUMEN_THEME, ICONS
from lumencli.ui.components import (
    console,
    render_header,
    render_status_bar,
    render_content_block,
    render_links_panel,
    render_command_bar,
    render_error,
)


def render_page(page: ParsedPage, fetch_result: FetchResult):
    """
    Render a complete page view in the terminal.

    Assembles:
    1. Header panel (brand + URL)
    2. Page title
    3. Content blocks (headings, paragraphs, code, lists, etc.)
    4. Links panel (numbered)
    5. Command bar
    6. Status bar

    Args:
        page: The parsed page data.
        fetch_result: The raw fetch result with metadata.
    """
    console.clear()

    # ── Header ──
    console.print(render_header(
        url=fetch_result.final_url or fetch_result.url,
        title=page.title,
    ))

    # ── Page Title ──
    if page.title:
        console.print()
        console.print(f"  {ICONS['pin']} ", style="section.icon", end="")
        console.print(page.title.upper(), style="heading.h1")
        console.print()

    # ── Content Blocks ──
    if page.blocks:
        console.print(Rule(style="border"))
        console.print()
        prev_kind = None
        for block in page.blocks:
            rendered = render_content_block(block)
            # Add spacing between different block types
            if prev_kind and prev_kind != block.kind:
                console.print()
            console.print(rendered)
            prev_kind = block.kind
        console.print()
    else:
        console.print("\n  [text.dim]No readable content found.[/text.dim]\n")

    # ── Links Panel ──
    if page.links:
        console.print(render_links_panel(page))

    # ── Command Bar ──
    console.print(render_command_bar())

    # ── Status Bar ──
    console.print(render_status_bar(
        status_code=fetch_result.status_code,
        load_time=fetch_result.load_time,
        link_count=page.link_count,
        error=fetch_result.error or "",
    ))
    console.print()


def render_error_page(fetch_result: FetchResult):
    """Render an error page when fetching fails."""
    console.clear()
    console.print(render_header(url=fetch_result.url))
    console.print()
    render_error(fetch_result.error or "Unknown error occurred.")
    console.print(render_command_bar())
    console.print()
