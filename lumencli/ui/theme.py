from rich.style import Style
from rich.theme import Theme


# ─── Color Palette ─────────────────────────────────────────────

COLORS = {
    "bg":            "#1a1b26",
    "fg":            "#c0caf5",
    "dim":           "#565f89",
    "border":        "#3b4261",
    "accent_cyan":   "#7dcfff",
    "accent_blue":   "#7aa2f7",
    "accent_magenta":"#bb9af7",
    "accent_green":  "#9ece6a",
    "accent_yellow": "#e0af68",
    "accent_red":    "#f7768e",
    "accent_orange": "#ff9e64",
    "accent_teal":   "#2ac3de",
    "white":         "#ffffff",
}


# ─── Named Styles ──────────────────────────────────────────────

STYLES = {
    # Brand / chrome
    "brand":           Style(color=COLORS["accent_cyan"], bold=True),
    "brand.dim":       Style(color=COLORS["accent_blue"]),

    # Headers
    "heading.h1":      Style(color=COLORS["accent_magenta"], bold=True),
    "heading.h2":      Style(color=COLORS["accent_blue"], bold=True),
    "heading.h3":      Style(color=COLORS["accent_teal"], bold=True),
    "heading.h4":      Style(color=COLORS["accent_yellow"]),
    "heading.h5":      Style(color=COLORS["accent_orange"]),
    "heading.h6":      Style(color=COLORS["dim"]),

    # Content
    "text":            Style(color=COLORS["fg"]),
    "text.dim":        Style(color=COLORS["dim"]),
    "text.bold":       Style(color=COLORS["fg"], bold=True),

    # Links
    "link":            Style(color=COLORS["accent_cyan"], underline=True),
    "link.number":     Style(color=COLORS["accent_yellow"], bold=True),
    "link.text":       Style(color=COLORS["accent_cyan"]),

    # Code
    "code":            Style(color=COLORS["accent_green"]),
    "code.block":      Style(color=COLORS["accent_green"]),

    # Blockquote
    "blockquote":      Style(color=COLORS["dim"], italic=True),

    # Status bar
    "status":          Style(color=COLORS["accent_green"], bold=True),
    "status.dim":      Style(color=COLORS["dim"]),
    "status.error":    Style(color=COLORS["accent_red"], bold=True),
    "status.warn":     Style(color=COLORS["accent_yellow"]),
    "status.url":      Style(color=COLORS["accent_blue"], underline=True),

    # Borders / panels
    "border":          Style(color=COLORS["border"]),
    "panel.border":    Style(color=COLORS["accent_blue"]),

    # Errors
    "error":           Style(color=COLORS["accent_red"], bold=True),
    "success":         Style(color=COLORS["accent_green"], bold=True),

    # Prompt
    "prompt":          Style(color=COLORS["accent_cyan"], bold=True),
    "prompt.url":      Style(color=COLORS["accent_blue"]),

    # Section labels
    "section":         Style(color=COLORS["accent_yellow"], bold=True),
    "section.icon":    Style(color=COLORS["accent_orange"]),

    # List bullets
    "bullet":          Style(color=COLORS["accent_teal"]),

    # Table
    "table.header":    Style(color=COLORS["accent_magenta"], bold=True),
    "table.cell":      Style(color=COLORS["fg"]),
}


LUMEN_THEME = Theme(STYLES)


# ─── Emoji / Icon Constants ───────────────────────────────────

ICONS = {
    "brand":     "",
    "pin":       "",
    "content":   "",
    "link":      "",
    "command":   "",
    "status":    "",
    "bookmark":  "",
    "history":   "",
    "search":    "",
    "error":     "",
    "success":   "",
    "warning":   "",
    "loading":   "",
    "back":      "",
    "forward":   "",
    "reload":    "",
    "divider":   "─",
}
