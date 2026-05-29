from dataclasses import dataclass, field


@dataclass
class History:
    """Browser-like navigation history with back/forward."""

    _stack: list[str] = field(default_factory=list)
    _index: int = -1

    @property
    def current_url(self) -> str:
        """Get the current URL, or empty string if no history."""
        if 0 <= self._index < len(self._stack):
            return self._stack[self._index]
        return ""

    @property
    def can_go_back(self) -> bool:
        return self._index > 0

    @property
    def can_go_forward(self) -> bool:
        return self._index < len(self._stack) - 1

    @property
    def size(self) -> int:
        return len(self._stack)

    def visit(self, url: str):
        """
        Navigate to a new URL.
        Truncates any forward history (like a real browser).
        """
        # If we went back and then visit a new page, discard forward history
        if self._index < len(self._stack) - 1:
            self._stack = self._stack[: self._index + 1]

        self._stack.append(url)
        self._index = len(self._stack) - 1

    def back(self) -> str:
        """Go back one page. Returns the URL or empty string."""
        if self.can_go_back:
            self._index -= 1
            return self._stack[self._index]
        return ""

    def forward(self) -> str:
        """Go forward one page. Returns the URL or empty string."""
        if self.can_go_forward:
            self._index += 1
            return self._stack[self._index]
        return ""

    def list_all(self) -> list[tuple[int, str, bool]]:
        """
        Return all history entries as (index, url, is_current) tuples.
        """
        return [
            (i, url, i == self._index)
            for i, url in enumerate(self._stack)
        ]
