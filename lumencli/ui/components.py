"""
components.py — UI rendering components for LUMENCLI

Provides reusable Rich console components and rendering functions.
"""

from rich.console import Console
from rich.text import Text
from rich.panel import Panel
from rich.align import Align

from lumencli.ui.theme import ICONS, LUMEN_THEME


# ─── Console Instance ─────────────────────────────────────────────

console = Console(theme=LUMEN_THEME)


# ─── Rendering Functions ─────────────────────────────────────────

def render_splash():
    """Render the LUMENCLI splash screen."""
    console.clear()
    console.print()
    
    splash = Panel(
        Text.assemble(
            ("LUMEN", "brand"),
            ("CLI", "brand.dim"),
        ),
        title="Terminal Web Browser",
        border_style="border",
        padding=(1, 2),
    )
    console.print(splash)
    console.print()
    console.print(
        f"  {ICONS['command']} Type 'help' for available commands or 'open <url>' to start browsing.",
        style="text.dim",
    )
    console.print()


def render_error(message: str):
    """Render an error message."""
    console.print()
    console.print(
        f"  {ICONS['error']} {message}",
        style="error",
    )
    console.print()


def render_success(message: str):
    """Render a success message."""
    console.print()
    console.print(
        f"  {ICONS['success']} {message}",
        style="success",
    )
    console.print()


def render_info(message: str):
    """Render an info message."""
    console.print()
    console.print(
        f"  {ICONS['info']} {message}",
        style="text.dim",
    )
    console.print()


def render_header(url: str, title: str = "") -> Panel:
    """Render the page header with URL."""
    header_text = Text()
    header_text.append(f"{ICONS['brand']} ", style="brand")
    header_text.append(url, style="status.url")
    
    return Panel(
        Align.center(header_text),
        border_style="border",
        padding=(0, 1),
    )


def render_command_bar() -> Panel:
    """Render the command bar with available actions."""
    commands = "back | forward | reload | bookmark | history | help | quit"
    bar = Text(f"  {ICONS['command']} {commands}", style="text.dim")
    return Panel(bar, border_style="border", padding=(0, 1))


def render_status_bar(
    status_code: int,
    load_time: float,
    link_count: int,
    error: str = "",
) -> Panel:
    """Render the status bar with page metadata."""
    status = Panel(
        Text.assemble(
            (f"{ICONS['status']} ", "status"),
            (f"{status_code} ", "status" if 200 <= status_code < 300 else "status.error"),
            (f"• {load_time:.2f}s ", "status.dim"),
            (f"• {link_count} links ", "status.dim"),
        ),
        border_style="border",
        padding=(0, 1),
    )
    return status


def render_content_block(block) -> Text:
    """Render a single content block (heading, paragraph, etc.)."""
    text = Text()
    
    if block.kind == "heading":
        level = block.level or 1
        style = f"heading.h{min(level, 6)}"
        text.append(f"  {block.text}", style=style)
    
    elif block.kind == "paragraph":
        text.append(f"  {block.text}", style="text")
    
    elif block.kind == "code":
        text.append(f"  {block.text}", style="code")
    
    elif block.kind == "list":
        text.append(f"  • {block.text}", style="text")
    
    elif block.kind == "blockquote":
        text.append(f"  │ {block.text}", style="blockquote")
    
    elif block.kind == "hr":
        text.append(f"  {block.text}", style="border")
    
    elif block.kind == "link_ref":
        text.append(f"  {block.text}", style="link")
    
    else:
        text.append(f"  {block.text}", style="text")
    
    return text


def render_links_panel(page) -> Panel:
    """Render the links panel with numbered links."""
    from rich.table import Table
    
    table = Table(
        title=f"{ICONS['link']} Links",
        box=None,
        title_style="section",
        padding=(0, 0),
    )
    table.add_column("#", style="link.number", width=4)
    table.add_column("Text", style="link.text")
    table.add_column("URL", style="status.url")
    
    for link in page.links[:50]:  # Limit to 50 links
        table.add_row(str(link.number), link.text, link.url)
    
    return Panel(table, border_style="border", padding=(0, 1))
