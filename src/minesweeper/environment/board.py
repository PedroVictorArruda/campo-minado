"""Hidden board: where the mines are and how many surround each cell.

This is the "truth" of the environment. Agents must not read it; they only
receive an Observation (see observation.py).
"""

from __future__ import annotations

import random
from collections.abc import Iterator

Cell = tuple[int, int]


def neighbors(row: int, col: int, rows: int, cols: int) -> Iterator[Cell]:
    """Yield the up to 8 cells around (row, col) that are inside the board."""
    for row_offset in (-1, 0, 1):
        for col_offset in (-1, 0, 1):
            if row_offset == 0 and col_offset == 0:
                continue
            neighbor_row = row + row_offset
            neighbor_col = col + col_offset
            if 0 <= neighbor_row < rows and 0 <= neighbor_col < cols:
                yield neighbor_row, neighbor_col


class Board:
    """Mine positions and adjacent mine counts."""

    def __init__(self, rows: int, cols: int, mines: set[Cell]) -> None:
        self.rows = rows
        self.cols = cols
        self.mines = frozenset(mines)
        self._counts = [
            [self._count_adjacent(row, col) for col in range(cols)]
            for row in range(rows)
        ]

    @classmethod
    def generate(
        cls,
        rows: int,
        cols: int,
        num_mines: int,
        first_click: Cell,
        rng: random.Random,
    ) -> Board:
        """Place mines at random, keeping the first clicked cell safe.

        When there is room, the neighbors of the first click are also kept
        free of mines, so the first move opens a region (a zero) instead of a
        single number.
        """
        all_cells = [(row, col) for row in range(rows) for col in range(cols)]
        protected = {first_click, *neighbors(*first_click, rows, cols)}
        if rows * cols - len(protected) < num_mines:
            protected = {first_click}
        candidates = [cell for cell in all_cells if cell not in protected]
        mines = set(rng.sample(candidates, num_mines))
        return cls(rows, cols, mines)

    def _count_adjacent(self, row: int, col: int) -> int:
        return sum(
            1 for cell in neighbors(row, col, self.rows, self.cols) if cell in self.mines
        )

    def is_mine(self, row: int, col: int) -> bool:
        return (row, col) in self.mines

    def adjacent_mines(self, row: int, col: int) -> int:
        """Number of mines in the 8 neighbors of (row, col)."""
        return self._counts[row][col]
