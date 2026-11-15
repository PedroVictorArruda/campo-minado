"""Board configurations and difficulty presets."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class GameConfig:
    """Size and number of mines of a board."""

    rows: int
    cols: int
    mines: int

    def __post_init__(self) -> None:
        if self.rows < 1 or self.cols < 1:
            raise ValueError("rows and cols must be at least 1")
        if self.mines < 0:
            raise ValueError("mines cannot be negative")
        # At least the first revealed cell must be free of mines.
        if self.mines > self.rows * self.cols - 1:
            raise ValueError("too many mines for this board size")

    @property
    def total_cells(self) -> int:
        return self.rows * self.cols

    @property
    def safe_cells(self) -> int:
        return self.total_cells - self.mines


# Classic Minesweeper sizes.
DIFFICULTIES: dict[str, GameConfig] = {
    "easy": GameConfig(rows=9, cols=9, mines=10),
    "medium": GameConfig(rows=16, cols=16, mines=40),
    "hard": GameConfig(rows=16, cols=30, mines=99),
}


def get_config(difficulty: str) -> GameConfig:
    """Return the preset for 'easy', 'medium' or 'hard'."""
    try:
        return DIFFICULTIES[difficulty]
    except KeyError:
        options = ", ".join(DIFFICULTIES)
        raise ValueError(f"unknown difficulty '{difficulty}' (options: {options})") from None
