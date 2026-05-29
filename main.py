#!/usr/bin/env python3
"""
main.py — LUMENCLI Terminal Web Browser

Entry point: runs the interactive REPL command loop.
Supports: open, click, back, forward, reload, search,
          bookmark, history, help, quit.
"""

import sys
from urllib.parse import quote_plus

from rich.text import Text
from rich.table import Table
from rich import box

from lumencli.core.fetch import fetch_page, normalize_url, FetchResult
from lumencli.core.parser import parse_html, ParsedPage
from lumencli.core.history import History
from lumencli.core.bookmarks import BookmarkManager
from lumencli.ui.theme import ICONS, LUMEN_THEME
from lumencli.ui.components import (
    console,
    render_splash,
    render_error,
    render_success,
    render_info,
    render_command_bar,
    render_header,
)
from lumencli.ui.layout import render_page, render_error_page


# ─── Browser State ─────────────────────────────────────────────

class Browser:
    """Main browser state and command dispatcher."""

    def __init__(self):
        self.history = History()
        self.bookmarks = BookmarkManager()
        self.current_page: ParsedPage | None = None
        self.current_fetch: FetchResult | None = None
        self.running = True

    # ── Navigation ─────────────────────────────────────────────

    def navigate(self, url: str):
        """Fetch and display a page."""
        url = normalize_url(url)
        if not url:
            render_error("Please provide a URL. Usage: open <url>")
            return

        console.print(f"\n  {ICONS['loading']} Fetching {url} ...\n", style="text.dim")

        result = fetch_page(url)
        self.current_fetch = result

        if not result.ok:
            self.current_page = None
            render_error_page(result)
            return

        # Parse and render
        page = parse_html(result.html, base_url=result.final_url or url)
        self.current_page = page

        # Record in history
        self.history.visit(result.final_url or url)

        render_page(page, result)

    def click_link(self, number: int):
        """Navigate to a link by its number."""
        if not self.current_page:
            render_error("No page loaded. Use 'open <url>' first.")
            return

        link_url = self.current_page.get_link_url(number)
        if not link_url:
            render_error(
                f"Link [{number}] not found. "
                f"Valid range: 1–{self.current_page.link_count}"
            )
            return

        self.navigate(link_url)

    def go_back(self):
        """Navigate back in history."""
        url = self.history.back()
        if url:
            self.navigate(url)
        else:
            render_error("No previous page in history.")

    def go_forward(self):
        """Navigate forward in history."""
        url = self.history.forward()
        if url:
            self.navigate(url)
        else:
            render_error("No next page in history.")

    def reload(self):
        """Reload the current page."""
        url = self.history.current_url
        if url:
            self.navigate(url)
        else:
            render_error("No page to reload.")

    def search(self, query: str):
        """Search via DuckDuckGo HTML."""
        if not query.strip():
            render_error("Usage: search <query>")
            return
        encoded = quote_plus(query)
        url = f"https://html.duckduckgo.com/html/?q={encoded}"
        self.navigate(url)

    # ── Bookmarks ──────────────────────────────────────────────

    def bookmark_add(self):
        """Bookmark the current page."""
        url = self.history.current_url
        if not url:
            render_error("No page to bookmark.")
            return
        title = self.current_page.title if self.current_page else url
        bm = self.bookmarks.add(url, title)
        render_success(f"Bookmarked: {bm.title}")

    def bookmark_show(self):
        """Show all bookmarks."""
        bms = self.bookmarks.list_all()
        if not bms:
            render_info("No bookmarks saved yet.")
            return

        table = Table(
            title=f"{ICONS['bookmark']} Bookmarks",
            box=box.ROUNDED,
            title_style="section",
            border_style="border",
            padding=(0, 1),
        )
        table.add_column("#", style="link.number", width=4)
        table.add_column("Title", style="link.text")
        table.add_column("URL", style="status.url")
        table.add_column("Added", style="text.dim")

        for i, bm in enumerate(bms, 1):
            table.add_row(str(i), bm.title, bm.url, bm.added)

        console.print()
        console.print(table)
        console.print(
            "  Type [prompt]open <url>[/prompt] or "
            "[prompt]bookmark open <n>[/prompt] to visit.",
            style="text.dim",
        )
        console.print()

    def bookmark_open(self, number: int):
        """Open a bookmark by number."""
        bm = self.bookmarks.get(number)
        if bm:
            self.navigate(bm.url)
        else:
            render_error(f"Bookmark #{number} not found.")

    # ── History Display ────────────────────────────────────────

    def show_history(self):
        """Display browsing history."""
        entries = self.history.list_all()
        if not entries:
            render_info("No history yet.")
            return

        table = Table(
            title=f"{ICONS['history']} History",
            box=box.ROUNDED,
            title_style="section",
            border_style="border",
            padding=(0, 1),
        )
        table.add_column("#", style="link.number", width=4)
        table.add_column("URL", style="status.url")
        table.add_column("", width=3)

        for idx, url, is_current in entries:
            marker = "◀" if is_current else ""
            table.add_row(str(idx + 1), url, marker)

        console.print()
        console.print(table)
        console.print()

    # ── Help ───────────────────────────────────────────────────

    def show_help(self):
        """Show all available commands."""
        console.print()
        table = Table(
            title=f"{ICONS['command']} LUMENCLI Commands",
            box=box.ROUNDED,
            title_style="section",
            border_style="border",
            padding=(0, 1),
        )
        table.add_column("Command", style="prompt", min_width=22)
        table.add_column("Description", style="text")

        commands = [
            ("open <url>",          "Navigate to a website"),
            ("click <number>",      "Follow a numbered link on the page"),
            ("back",                "Go to previous page"),
            ("forward",             "Go to next page"),
            ("reload",              "Reload current page"),
            ("search <query>",      "Search the web via DuckDuckGo"),
            ("bookmark add",        "Bookmark the current page"),
            ("bookmark show",       "List all bookmarks"),
            ("bookmark open <n>",   "Open a bookmark by number"),
            ("history",             "Show browsing history"),
            ("help",                "Show this help message"),
            ("quit / exit",         "Exit LUMENCLI"),
        ]

        for cmd, desc in commands:
            table.add_row(cmd, desc)

        console.print(table)
        console.print()

    # ── Command Dispatcher ────────────────────────────────────

    def dispatch(self, raw_input: str):
        """Parse and dispatch a user command."""
        raw = raw_input.strip()
        if not raw:
            return

        parts = raw.split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1].strip() if len(parts) > 1 else ""

        if cmd == "open":
            if arg:
                self.navigate(arg)
            else:
                render_error("Usage: open <url>")

        elif cmd == "click":
            try:
                num = int(arg)
                self.click_link(num)
            except (ValueError, TypeError):
                render_error("Usage: click <number>")

        elif cmd == "back":
            self.go_back()

        elif cmd == "forward":
            self.go_forward()

        elif cmd == "reload":
            self.reload()

        elif cmd == "search":
            self.search(arg)

        elif cmd == "bookmark":
            sub_parts = arg.split(maxsplit=1)
            sub_cmd = sub_parts[0].lower() if sub_parts else ""
            sub_arg = sub_parts[1] if len(sub_parts) > 1 else ""

            if sub_cmd == "add":
                self.bookmark_add()
            elif sub_cmd == "show" or sub_cmd == "list":
                self.bookmark_show()
            elif sub_cmd == "open":
                try:
                    self.bookmark_open(int(sub_arg))
                except (ValueError, TypeError):
                    render_error("Usage: bookmark open <number>")
            else:
                render_error("Usage: bookmark add | show | open <n>")

        elif cmd == "history":
            self.show_history()

        elif cmd == "help":
            self.show_help()

        elif cmd in ("quit", "exit", "q"):
            console.print(
                f"\n  {ICONS['brand']} Goodbye! Thanks for using LUMENCLI.\n",
                style="brand",
            )
            self.running = False

        else:
            render_error(
                f"Unknown command: '{cmd}'. Type 'help' for available commands."
            )


# ─── Main Loop ─────────────────────────────────────────────────

def main():
    """Run the LUMENCLI interactive browser loop."""
    browser = Browser()
    render_splash()

    while browser.running:
        # Build prompt
        prompt = Text()
        prompt.append("LUMEN", style="prompt")
        current = browser.history.current_url
        if current:
            # Show just the domain for compactness
            from urllib.parse import urlparse
            domain = urlparse(current).netloc or current
            prompt.append(f" [{domain}]", style="prompt.url")
        prompt.append("> ", style="prompt")

        try:
            user_input = console.input(prompt)
            browser.dispatch(user_input)
        except KeyboardInterrupt:
            console.print(
                f"\n\n  {ICONS['brand']} Press Ctrl+C again or type 'quit' to exit.\n",
                style="text.dim",
            )
            try:
                user_input = console.input(prompt)
                browser.dispatch(user_input)
            except KeyboardInterrupt:
                console.print(
                    f"\n  {ICONS['brand']} Goodbye!\n",
                    style="brand",
                )
                break
        except EOFError:
            console.print(
                f"\n  {ICONS['brand']} Goodbye!\n",
                style="brand",
            )
            break


if __name__ == "__main__":
    main()
