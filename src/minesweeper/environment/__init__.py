"""Environment: board, game rules and what the agent can perceive.

    import from here:
    from minesweeper.environment import Game, get_config, HIDDEN, FLAGGED
"""

from .board import Cell, neighbors
from .config import DIFFICULTIES, GameConfig, get_config
from .game import Game, InvalidMoveError, MoveResult
from .observation import FLAGGED, HIDDEN, GameStatus, Observation

__all__ = [
    "Cell",
    "DIFFICULTIES",
    "FLAGGED",
    "Game",
    "GameConfig",
    "GameStatus",
    "HIDDEN",
    "InvalidMoveError",
    "MoveResult",
    "Observation",
    "get_config",
    "neighbors",
]
