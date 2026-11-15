"""Agents: random, logic-based, CSP and probabilistic.

Public API (import from here):

    from minesweeper.agents import Agent, Action, play_game
"""

from .base import Action, ActionType, Agent
from .runner import AgentStuckError, GameResult, play_game

__all__ = [
    "Action",
    "ActionType",
    "Agent",
    "AgentStuckError",
    "GameResult",
    "play_game",
]
