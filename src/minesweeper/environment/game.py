"""Game rules: reveal, flag, cascade of zeros, win and loss.

Typical loop (agent or interface):

    game = Game(get_config("easy"), seed=42)
    while not game.is_over:
        obs = game.observe()
        row, col = agent.choose(obs)
        game.reveal(row, col)
    print(game.status)
"""

from __future__ import annotations

import random
from collections import deque
from dataclasses import dataclass, field

from .board import Board, Cell, neighbors
from .config import GameConfig
from .observation import FLAGGED, HIDDEN, GameStatus, Observation


class InvalidMoveError(Exception):
    """Raised for moves outside the board or after the game has ended."""


@dataclass(frozen=True)
class MoveResult:
    """What happened after one action."""

    action: str  # "reveal", "flag" or "unflag"
    cell: Cell
    revealed: tuple[Cell, ...] = field(default_factory=tuple)
    hit_mine: bool = False
    status: GameStatus = GameStatus.IN_PROGRESS
    changed: bool = True  # False when the action had no effect


class Game:
    """One Minesweeper match.

    The mines are only placed on the first reveal, so the first move is
    always safe. With the same seed and the same first move the board is
    always the same, which makes experiments reproducible.
    """

    def __init__(self, config: GameConfig, seed: int | None = None) -> None:
        self.config = config
        self.seed = seed
        self._rng = random.Random(seed)
        self._board: Board | None = None
        self._grid: list[list[int]] = [
            [HIDDEN] * config.cols for _ in range(config.rows)
        ]
        self._revealed_count = 0
        self._status = GameStatus.IN_PROGRESS
        self._moves = 0
        self._exploded: Cell | None = None

    # ----- public state ------------------------------------------------

    @property
    def rows(self) -> int:
        return self.config.rows

    @property
    def cols(self) -> int:
        return self.config.cols

    @property
    def status(self) -> GameStatus:
        return self._status

    @property
    def is_over(self) -> bool:
        return self._status is not GameStatus.IN_PROGRESS

    @property
    def moves(self) -> int:
        """Number of actions that changed the board (reveals and flags)."""
        return self._moves

    @property
    def revealed_count(self) -> int:
        return self._revealed_count

    @property
    def safe_cells_left(self) -> int:
        return self.config.safe_cells - self._revealed_count

    @property
    def exploded_cell(self) -> Cell | None:
        """Cell of the mine that ended the game, if it was lost."""
        return self._exploded

    def observe(self) -> Observation:
        """What the agent is allowed to see. Never includes the mines."""
        return Observation(
            rows=self.rows,
            cols=self.cols,
            total_mines=self.config.mines,
            grid=tuple(tuple(row) for row in self._grid),
            status=self._status,
            moves=self._moves,
        )

    def mine_positions(self) -> frozenset[Cell]:
        """Real mine positions, only available after the game ends.

        Meant for the interface (show the board at the end) and for
        experiments. Agents must use observe() instead.
        """
        if not self.is_over:
            raise RuntimeError("mine positions are hidden while the game is running")
        return self._board.mines if self._board else frozenset()

    # ----- actions (the "Actuators" in the PEAS model) ------------------

    def reveal(self, row: int, col: int) -> MoveResult:
        """Open a cell. A zero opens its neighbors recursively.

        Revealing a flagged or already opened cell does nothing
        (changed=False).
        """
        self._check_move(row, col)
        if self._grid[row][col] != HIDDEN:
            return MoveResult("reveal", (row, col), status=self._status, changed=False)

        if self._board is None:
            self._board = Board.generate(
                self.rows, self.cols, self.config.mines, (row, col), self._rng
            )

        self._moves += 1

        if self._board.is_mine(row, col):
            self._status = GameStatus.LOST
            self._exploded = (row, col)
            return MoveResult("reveal", (row, col), hit_mine=True, status=self._status)

        opened = self._flood_reveal(row, col)
        if self._revealed_count == self.config.safe_cells:
            self._status = GameStatus.WON
        return MoveResult("reveal", (row, col), revealed=tuple(opened), status=self._status)

    def flag(self, row: int, col: int) -> MoveResult:
        """Put a flag on a closed cell."""
        self._check_move(row, col)
        if self._grid[row][col] != HIDDEN:
            return MoveResult("flag", (row, col), status=self._status, changed=False)
        self._grid[row][col] = FLAGGED
        self._moves += 1
        return MoveResult("flag", (row, col), status=self._status)

    def unflag(self, row: int, col: int) -> MoveResult:
        """Remove a flag."""
        self._check_move(row, col)
        if self._grid[row][col] != FLAGGED:
            return MoveResult("unflag", (row, col), status=self._status, changed=False)
        self._grid[row][col] = HIDDEN
        self._moves += 1
        return MoveResult("unflag", (row, col), status=self._status)

    def toggle_flag(self, row: int, col: int) -> MoveResult:
        """Flag a closed cell or remove its flag (handy for the human CLI)."""
        if self.in_bounds(row, col) and self._grid[row][col] == FLAGGED:
            return self.unflag(row, col)
        return self.flag(row, col)

    # ----- helpers -------------------------------------------------------

    def in_bounds(self, row: int, col: int) -> bool:
        return 0 <= row < self.rows and 0 <= col < self.cols

    def _check_move(self, row: int, col: int) -> None:
        if self.is_over:
            raise InvalidMoveError("the game is over")
        if not self.in_bounds(row, col):
            raise InvalidMoveError(f"cell ({row}, {col}) is outside the board")

    def _flood_reveal(self, row: int, col: int) -> list[Cell]:
        """Open (row, col) and, while the opened cells are zeros, their neighbors.

        Uses a queue (BFS) instead of recursion so large boards do not hit
        Python's recursion limit. Flagged cells are never opened.
        """
        assert self._board is not None
        opened: list[Cell] = []
        queue = deque([(row, col)])
        while queue:
            current_row, current_col = queue.popleft()
            if self._grid[current_row][current_col] != HIDDEN:
                continue
            value = self._board.adjacent_mines(current_row, current_col)
            self._grid[current_row][current_col] = value
            self._revealed_count += 1
            opened.append((current_row, current_col))
            if value == 0:
                for neighbor in neighbors(current_row, current_col, self.rows, self.cols):
                    neighbor_row, neighbor_col = neighbor
                    if self._grid[neighbor_row][neighbor_col] == HIDDEN:
                        queue.append(neighbor)
        return opened
