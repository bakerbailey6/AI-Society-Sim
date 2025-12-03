"""
Action Module - Abstract Base Class for Agent Actions

This module provides the abstract base class for all agent actions,
demonstrating the Command pattern.

Design Patterns:
    - Command Pattern: Actions are encapsulated as objects with execute()
    - Template Method: Base class defines action execution structure

SOLID Principles:
    - Single Responsibility: Actions only encapsulate behavior
    - Open/Closed: New actions extend without modifying base
    - Liskov Substitution: All actions substitutable for Action
    - Dependency Inversion: Depends on Agent/World abstractions
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from agents.agent import Agent
    from world.world import World


class Action(ABC):
    """
    Abstract base class for all agent actions.

    This class demonstrates the Command pattern by encapsulating
    agent actions as first-class objects. Each action knows how to
    execute itself, validate preconditions, and optionally undo itself.

    The Command pattern enables:
    - Parameterization of objects with operations
    - Queuing and scheduling of operations
    - Undoable operations
    - Logging and auditing of operations

    Attributes:
        name (str): Human-readable name of the action
        description (str): Detailed description of what the action does

    Note:
        This is an abstract class demonstrating the Command pattern.
        Concrete action subclasses must implement execute(), can_execute(),
        and energy_cost.

    Examples:
        >>> # Concrete action implementation
        >>> class MyAction(Action):
        ...     def execute(self, agent, world):
        ...         # Perform action logic
        ...         return True
        ...     def can_execute(self, agent, world):
        ...         return agent.energy > self.energy_cost
        ...     @property
        ...     def energy_cost(self):
        ...         return 5.0
    """

    def __init__(self, name: str, description: str = "") -> None:
        """
        Initialize an action.

        Args:
            name (str): Action name
            description (str, optional): Action description
        """
        self._name: str = name
        self._description: str = description

    @property
    def name(self) -> str:
        """Get the action name."""
        return self._name

    @property
    def description(self) -> str:
        """Get the action description."""
        return self._description

    @abstractmethod
    def execute(self, agent: Agent, world: World) -> bool:
        """
        Execute the action (Command pattern core method).

        This is the primary method of the Command pattern. It encapsulates
        the request as an object, allowing for parameterization and queuing.

        Args:
            agent (Agent): The agent performing the action
            world (World): The world in which the action occurs

        Returns:
            bool: True if action executed successfully, False otherwise

        Note:
            Subclasses must implement this method with their specific
            action logic. The method should:
            1. Validate preconditions (or rely on can_execute())
            2. Perform the action
            3. Update agent/world state
            4. Consume energy (via agent.consume_energy())
            5. Return success/failure status
        """
        pass

    @abstractmethod
    def can_execute(self, agent: Agent, world: World) -> bool:
        """
        Check if the action can be executed (precondition validation).

        This method validates all preconditions before attempting to
        execute the action. Common checks include:
        - Sufficient energy
        - Valid target position/agent/resource
        - Agent is alive and active
        - World state allows the action

        Args:
            agent (Agent): The agent attempting the action
            world (World): The world context

        Returns:
            bool: True if action can be executed, False otherwise

        Note:
            Subclasses should implement comprehensive validation here.
            This method should NOT modify any state - it's purely
            for checking preconditions.
        """
        pass

    def undo(self, agent: Agent, world: World) -> None:
        """
        Undo the action (optional Command pattern feature).

        This method provides the ability to reverse an action,
        demonstrating the undoable operations feature of the
        Command pattern.

        By default, actions are not undoable. Subclasses that
        represent reversible actions (like MoveAction) can override
        this method to provide undo functionality.

        Args:
            agent (Agent): The agent whose action to undo
            world (World): The world context

        Note:
            Not all actions are reversible. For example:
            - MoveAction: Can undo by moving back
            - GatherAction: Could undo by replacing resource
            - AttackAction: Cannot undo (irreversible damage)

            Subclasses should raise NotImplementedError if undo
            is not supported for that action type.
        """
        raise NotImplementedError(
            f"{self.__class__.__name__} does not support undo operations"
        )

    @property
    @abstractmethod
    def energy_cost(self) -> float:
        """
        Get the energy cost of this action.

        Different actions require different amounts of energy.
        This property defines the base energy cost.

        Returns:
            float: Energy required to perform the action

        Note:
            Subclasses must define their energy cost.
            Common ranges:
            - RestAction: 0.0 (recovers energy)
            - MoveAction: 1.0 (low cost)
            - GatherAction: 2.0 (moderate cost)
            - AttackAction: 5.0 (high cost)
        """
        pass

    def __repr__(self) -> str:
        """
        String representation of the action.

        Returns:
            str: Human-readable representation
        """
        return f"{self.__class__.__name__}(name='{self._name}')"

    def __str__(self) -> str:
        """
        String representation for display.

        Returns:
            str: Display string
        """
        return self._name
