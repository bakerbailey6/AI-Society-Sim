"""
Actions Package - Command Pattern Implementation

This package provides the action system for the AI Society Simulator,
demonstrating the Command pattern where agent actions are encapsulated
as objects.

Design Patterns:
    - Command: Each action is a self-contained command object
    - Template Method: Action base class defines execution template

SOLID Principles:
    - Single Responsibility: Each action does one thing
    - Open/Closed: New actions can be added without modifying existing code
    - Liskov Substitution: All actions are substitutable for Action base
    - Interface Segregation: Minimal, focused action interface
    - Dependency Inversion: Actions depend on abstractions (Agent, World)

Exports:
    Action: Abstract base class for all actions
    MoveAction: Move to a different position
    GatherAction: Collect resources from a cell
    RestAction: Recover energy
    TradeAction: Exchange resources (skeleton)
    AttackAction: Attack another agent (skeleton)
    FormAllianceAction: Create alliance with agents (skeleton)
"""

from .action import Action
from .move import MoveAction
from .gather import GatherAction
from .rest import RestAction
from .trade import TradeAction
from .attack import AttackAction
from .alliance import FormAllianceAction

__all__ = [
    "Action",
    "MoveAction",
    "GatherAction",
    "RestAction",
    "TradeAction",
    "AttackAction",
    "FormAllianceAction",
]
