"""What the agent perceives (the "Sensors" in the PEAS model).

An Observation only holds what a human player would see on the screen:
hidden cells, flags, opened numbers and the total number of mines.
It never contains the mine positions.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from .board import Cell, neighbors

# Values used in Observation.grid besides the numbers 0..8.
HIDDEN = -1
FLAGGED = -2


class GameStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    WON = "won"
    LOST = "lost"


@dataclass(frozen=True)
class Observation:
    """Immutable snapshot of the visible board.

    grid[row][col] is:
      * HIDDEN (-1)  for a closed cell,
      * FLAGGED (-2) for a closed cell with a flag,
      * 0..8         for an opened cell (number of adjacent mines).
    """

    rows: int
    cols: int
    total_mines: int
    grid: tuple[tuple[int, ...], ...]
    status: GameStatus
    moves: int

    # ----- single cells -------------------------------------------------

    def value(self, row: int, col: int) -> int:
        return self.grid[row][col]

    def is_hidden(self, row: int, col: int) -> bool:
        """True for closed cells, flagged or not."""
        return self.grid[row][col] in (HIDDEN, FLAGGED)

    def is_flagged(self, row: int, col: int) -> bool:
        return self.grid[row][col] == FLAGGED

    def is_revealed(self, row: int, col: int) -> bool:
        return self.grid[row][col] >= 0

    def neighbors(self, row: int, col: int) -> list[Cell]:
        return list(neighbors(row, col, self.rows, self.cols))

    # ----- collections of cells ----------------------------------------

    def cells(self) -> list[Cell]:
        return [(row, col) for row in range(self.rows) for col in range(self.cols)]

    def hidden_cells(self) -> list[Cell]:
        """Closed cells without a flag (the ones an agent can reveal)."""
        return [cell for cell in self.cells() if self.value(*cell) == HIDDEN]

    def flagged_cells(self) -> list[Cell]:
        return [cell for cell in self.cells() if self.value(*cell) == FLAGGED]

    def revealed_cells(self) -> list[Cell]:
        return [cell for cell in self.cells() if self.value(*cell) >= 0]

    def frontier(self) -> list[Cell]:
        """Opened numbers (> 0) that still touch at least one closed cell.

        Each of these cells gives a constraint: the number equals the count of
        mines among its closed neighbors.
        """
        result = []
        for row, col in self.revealed_cells():
            touches_hidden = any(
                self.is_hidden(*neighbor) for neighbor in self.neighbors(row, col)
            )
            if self.value(row, col) > 0 and touches_hidden:
                result.append((row, col))
        return result

    # ----- counters -----------------------------------------------------

    @property
    def flags_placed(self) -> int:
        return sum(row.count(FLAGGED) for row in self.grid)

    @property
    def mines_left(self) -> int:
        """Total mines minus flags placed (can be wrong if a flag is wrong)."""
        return self.total_mines - self.flags_placed

    @property
    def is_first_move(self) -> bool:
        return not self.revealed_cells()

    @property
    def is_over(self) -> bool:
        return self.status is not GameStatus.IN_PROGRESS
