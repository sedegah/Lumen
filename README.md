# LUMENCLI — Terminal Web Browser

> *Lightweight web browsing, illuminated in your terminal.*

LUMENCLI is a command-line web browser that renders websites into a structured, readable terminal interface. Instead of raw HTML or messy dumps, pages are transformed into clean, navigable UI blocks with links, sections, and controls.

## Features

- **Web Browsing** — Fetch and render any website as clean terminal UI
- **Numbered Links** — All page links are numbered for easy navigation
- **History** — Full back/forward navigation like a real browser
- **Search** — Search the web directly via DuckDuckGo
- **Bookmarks** — Save and manage your favorite pages
- **Styled UI** — Beautiful Rich-powered panels, colors, and layout

## Quick Start

### Install dependencies

```bash
pip install -r requirements.txt
```

### Run

```bash
python main.py
```

### Example session

```
LUMEN> open wikipedia.org
LUMEN [wikipedia.org]> click 3
LUMEN [en.wikipedia.org]> back
LUMEN [wikipedia.org]> search python tutorials
LUMEN [html.duckduckgo.com]> bookmark add
LUMEN [html.duckduckgo.com]> quit
```

## Commands

| Command              | Description                        |
|----------------------|------------------------------------|
| `open <url>`         | Navigate to a website              |
| `click <number>`     | Follow a numbered link on the page |
| `back`               | Go to previous page                |
| `forward`            | Go to next page                    |
| `reload`             | Reload current page                |
| `search <query>`     | Search the web via DuckDuckGo      |
| `bookmark add`       | Bookmark the current page          |
| `bookmark show`      | List all bookmarks                 |
| `bookmark open <n>`  | Open a bookmark by number          |
| `history`            | Show browsing history              |
| `help`               | Show all commands                  |
| `quit`               | Exit LUMENCLI                      |

## Architecture

```
CLI Command Layer  →  Network Layer  →  HTML Parser  →  Layout Engine  →  Terminal Renderer
    (REPL)           (requests)       (BeautifulSoup)    (blocks)          (Rich)
```

## Project Structure

```
Lumen/
├── main.py                  # Entry point & REPL loop
├── requirements.txt         # Python dependencies
├── lumencli/
│   ├── core/
│   │   ├── fetch.py         # HTTP fetching with latency tracking
│   │   ├── parser.py        # HTML → structured content blocks
│   │   ├── history.py       # Back/forward navigation stack
│   │   └── bookmarks.py     # Bookmark persistence (JSON)
│   └── ui/
│       ├── theme.py         # Color palette & Rich styles
│       ├── components.py    # Panels, status bar, splash screen
│       └── layout.py        # Page assembly & rendering
```

## Tech Stack

- **Python 3.10+**
- **Requests** — HTTP fetching
- **BeautifulSoup** — HTML parsing
- **Rich** — Terminal UI styling

## License

MIT
