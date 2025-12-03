"""
MoveAction Module - Concrete Command for Agent Movement

This module provides the MoveAction class, demonstrating the Command
pattern for agent movement through the world grid.

Design Patterns:
    - Command: MoveAction is a concrete command
    - Template Method: Inherits execution structure from Action base

SOLID Principles:
    - Single Responsibility: Only handles agent movement
    - Open/Closed: Can extend movement behavior without modification
    - Liskov Substitution: Substitutable for Action base class
"""

from __future__ import annotations
from typing import TYPE_CHECKING

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from actions.action import Action
from world.position import Position

if TYPE_CHECKING:
    from agents.agent import Agent
    from world.world import World


class MoveAction(Action):
    """
    Concrete command for moving an agent to a new position.

    MoveAction demonstrates the Command pattern by encapsulating
    the move request as an object. The action validates that:
    - Target position is within world bounds
    - Target cell is traversable
    - Agent has sufficient energy

    This action is reversible - undo() will move the agent back
    to their previous position.

    Attributes:
        target_position (Position): The destination position

    Examples:
        >>> from world.position import Position
        >>> action = MoveAction(Position(5, 5))
        >>> if action.can_execute(agent, world):
        ...     success = action.execute(agent, world)
        ...     if not success:
        ...         action.undo(agent, world)  # Move back
    """

    def __init__(self, target_position: Position) -> None:
        """
        Initialize a MoveAction.

        Args:
            target_position (Position): The destination position
        """
        super().__init__(
            name="Move",
            description=f"Move to position {target_position}"
        )
        self._target_position: Position = target_position
        self._previous_position: Position | None = None

    @property
    def target_position(self) -> Position:
        """Get the target position."""
        return self._target_position

    def execute(self, agent: Agent, world: World) -> bool:
        """
        Execute the move action.

        Moves the agent from their current position to the target position,
        consuming energy in the process.

        Args:
            agent (Agent): The agent to move
            world (World): The world containing the agent

        Returns:
            bool: True if move successful, False otherwise

        Note:
            This method demonstrates the Command pattern's execute()
            method. It:
            1. Stores current position (for undo support)
            2. Validates preconditions
            3. Consumes energy
            4. Updates agent position
            5. Updates world state (cell occupancy)
        """
        # Store previous position for undo support
        self._previous_position = agent.position

        # Validate can execute
        if not self.can_execute(agent, world):
            return False

        # Consume energy
        if not agent.consume_energy(self.energy_cost):
            return False

        # Get old and new cells
        old_cell = world.get_cell(agent.position)
        new_cell = world.get_cell(self._target_position)

        # Update cell occupancy
        if old_cell:
            old_cell.remove_occupant(agent.agent_id)

        if new_cell:
            new_cell.add_occupant(agent.agent_id)

        # Update agent position
        agent.position = self._target_position

        return True

    def can_execute(self, agent: Agent, world: World) -> bool:
        """
        Check if move action can be executed.

        Validates:
        - Agent is alive
        - Target position is in bounds
        - Target cell exists and is traversable
        - Agent has sufficient energy

        Args:
            agent (Agent): The agent attempting to move
            world (World): The world context

        Returns:
            bool: True if move is valid, False otherwise
        """
        # Check agent is alive
        if not agent.is_alive():
            return False

        # Check energy
        if agent.energy < self.energy_cost:
            return False

        # Check target is in bounds
        if not self._target_position.is_within_bounds(world.width, world.height):
            return False

        # Check target cell is traversable
        target_cell = world.get_cell(self._target_position)
        if not target_cell or not target_cell.is_traversable():
            return False

        return True

    def undo(self, agent: Agent, world: World) -> None:
        """
        Undo the move action by moving back to previous position.

        This demonstrates the undoable operations feature of the
        Command pattern.

        Args:
            agent (Agent): The agent to move back
            world (World): The world context

        Raises:
            RuntimeError: If action hasn't been executed yet
        """
        if self._previous_position is None:
            raise RuntimeError("Cannot undo action that hasn't been executed")

        # Get current and previous cells
        current_cell = world.get_cell(agent.position)
        previous_cell = world.get_cell(self._previous_position)

        # Update cell occupancy
        if current_cell:
            current_cell.remove_occupant(agent.agent_id)

        if previous_cell:
            previous_cell.add_occupant(agent.agent_id)

        # Move agent back
        agent.position = self._previous_position

        # Restore energy (no energy cost for undo)
        agent.restore_energy(self.energy_cost)

    @property
    def energy_cost(self) -> float:
        """
        Get the energy cost of moving.

        Movement has a low energy cost.

        Returns:
            float: Energy cost (1.0)
        """
        return 1.0

    def __repr__(self) -> str:
        """
        String representation.

        Returns:
            str: Detailed representation
        """
        return (
            f"MoveAction(target={self._target_position}, "
            f"cost={self.energy_cost})"
        )
