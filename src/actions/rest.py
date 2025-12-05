"""
RestAction Module - Concrete Command for Agent Resting

This module provides the RestAction class, demonstrating the Command
pattern for agents resting to recover energy.

Design Patterns:
    - Command: RestAction is a concrete command
    - Template Method: Inherits execution structure from Action base

SOLID Principles:
    - Single Responsibility: Only handles agent resting
    - Open/Closed: Can extend resting behavior without modification
    - Liskov Substitution: Substitutable for Action base class
"""

from __future__ import annotations
from typing import TYPE_CHECKING

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from actions.action import Action

if TYPE_CHECKING:
    from agents.agent import Agent
    from world.world import World


class RestAction(Action):
    """
    Concrete command for resting to recover energy.

    RestAction demonstrates the Command pattern by encapsulating
    the rest request as an object. Unlike most actions:
    - It has zero energy cost
    - It restores energy instead of consuming it
    - It can always be executed (no preconditions except being alive)

    This action is useful when an agent needs to recover before
    performing more energy-intensive actions.

    Examples:
        >>> action = RestAction()
        >>> if action.can_execute(agent, world):
        ...     success = action.execute(agent, world)
        ...     # Agent's energy increased
    """

    def __init__(self) -> None:
        """Initialize a RestAction."""
        super().__init__(
            name="Rest",
            description="Rest to recover energy"
        )

    def execute(self, agent: Agent, world: World) -> bool:
        """
        Execute the rest action.

        Restores energy to the agent. The amount restored depends on
        the agent's current state and traits.

        Args:
            agent (Agent): The agent resting
            world (World): The world context

        Returns:
            bool: Always returns True (rest always succeeds)

        Note:
            This method demonstrates a Command with no side effects
            on the world - only on the agent's internal state.
            It:
            1. Validates agent is alive
            2. Calculates energy restoration
            3. Restores energy
        """
        # Validate can execute
        if not self.can_execute(agent, world):
            return False

        # Calculate energy restoration
        # Base restoration is 10.0, modified by agent's strength trait
        base_restoration = 10.0
        trait_modifier = 1.0 + (agent.traits.strength / 100.0)
        energy_restored = base_restoration * trait_modifier

        # Restore energy
        agent.restore_energy(energy_restored)

        return True

    def can_execute(self, agent: Agent, world: World) -> bool:
        """
        Check if rest action can be executed.

        Rest can almost always be executed - the only requirement
        is that the agent is alive.

        Args:
            agent (Agent): The agent attempting to rest
            world (World): The world context

        Returns:
            bool: True if agent is alive, False otherwise
        """
        # Only check that agent is alive
        return agent.is_alive()

    @property
    def energy_cost(self) -> float:
        """
        Get the energy cost of resting.

        Resting has zero energy cost - it restores energy instead.

        Returns:
            float: Energy cost (0.0)
        """
        return 0.0

    def __repr__(self) -> str:
        """
        String representation.

        Returns:
            str: Detailed representation
        """
        return f"RestAction(cost={self.energy_cost})"
