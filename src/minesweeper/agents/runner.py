"""Game loop: makes an agent play one game until it wins or loses.

Used by the CLI (to watch an agent play) and by the experiments (to run
many games and collect the metrics).
"""

from __future__ import annotations

import time
from collections.abc import Callable
from dataclasses import dataclass

from minesweeper.environment import Game, GameConfig, GameStatus, MoveResult, Observation

from .base import Action, ActionType, Agent

StepCallback = Callable[[Observation, Action, MoveResult], None]


class AgentStuckError(Exception):
    """Raised when the agent goes past the move limit without finishing."""


@dataclass(frozen=True)
class GameResult:
    """Metrics of one finished game."""

    agent_name: str
    config: GameConfig
    seed: int | None
    status: GameStatus
    moves: int
    reveals: int
    flags: int
    guesses: int
    wasted_moves: int
    revealed_cells: int
    thinking_seconds: float

    @property
    def won(self) -> bool:
        return self.status is GameStatus.WON

    @property
    def revealed_ratio(self) -> float:
        """Fraction of the safe cells that were opened (1.0 when won)."""
        return self.revealed_cells / self.config.safe_cells

    @property
    def seconds_per_move(self) -> float:
        return self.thinking_seconds / self.moves if self.moves else 0.0


def play_game(
    agent: Agent,
    game: Game,
    on_step: StepCallback | None = None,
    max_moves: int | None = None,
) -> GameResult:
    """Run the agent on the game until it ends and return the metrics.

    on_step, if given, is called after every action with the observation the
    agent saw, the action it chose and the result. The CLI uses it to draw
    the board.

    max_moves protects against an agent that never finishes (for example,
    flagging and unflagging the same cell forever). The default is three
    times the number of cells.
    """
    if max_moves is None:
        max_moves = 3 * game.config.total_cells

    agent.reset(game.seed)
    reveals = flags = guesses = wasted_moves = 0
    thinking_seconds = 0.0

    for _ in range(max_moves):
        if game.is_over:
            break
        observation = game.observe()

        start = time.perf_counter()
        action = agent.choose_action(observation)
        thinking_seconds += time.perf_counter() - start

        result = _apply(game, action)
        if not result.changed:
            wasted_moves += 1
        elif action.type is ActionType.REVEAL:
            reveals += 1
            if action.is_guess:
                guesses += 1
        elif action.type is ActionType.FLAG:
            flags += 1

        if on_step is not None:
            on_step(observation, action, result)
    else:
        if not game.is_over:
            raise AgentStuckError(
                f"agent '{agent.name}' did not finish the game in {max_moves} moves"
            )

    return GameResult(
        agent_name=agent.name,
        config=game.config,
        seed=game.seed,
        status=game.status,
        moves=game.moves,
        reveals=reveals,
        flags=flags,
        guesses=guesses,
        wasted_moves=wasted_moves,
        revealed_cells=game.revealed_count,
        thinking_seconds=thinking_seconds,
    )


def _apply(game: Game, action: Action) -> MoveResult:
    if action.type is ActionType.REVEAL:
        return game.reveal(action.row, action.col)
    if action.type is ActionType.FLAG:
        return game.flag(action.row, action.col)
    return game.unflag(action.row, action.col)
