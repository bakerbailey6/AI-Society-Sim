"""
SelfishPolicy Module - Concrete Strategy for Individual Survival

This module provides the SelfishPolicy class, demonstrating the Strategy
pattern for self-interested decision making.

Design Patterns:
    - Strategy: SelfishPolicy is a concrete strategy
    - Template Method: Uses inherited decision structure

SOLID Principles:
    - Single Responsibility: Only implements selfish decision logic
    - Open/Closed: Can extend selfish behavior without modification
    - Liskov Substitution: Substitutable for DecisionPolicy base class
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Any
import random

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from policies.policy import DecisionPolicy
from actions.rest import RestAction
from actions.gather import GatherAction
from actions.move import MoveAction
from world.position import Position

if TYPE_CHECKING:
    from agents.agent import Agent
    from actions.action import Action


class SelfishPolicy(DecisionPolicy):
    """
    Concrete strategy for self-interested, survival-focused decisions.

    SelfishPolicy demonstrates the Strategy pattern with a decision
    algorithm that prioritizes individual survival and resource
    accumulation over group benefit or social interaction.

    Decision priorities (in order):
    1. **Survival**: If low energy (<30), rest or find food
    2. **Safety**: If low health (<30), rest and avoid threats
    3. **Resource Hoarding**: If resources nearby, gather them
    4. **Exploration**: Move randomly to find more resources

    This policy represents individualistic behavior:
    - Never shares resources
    - Avoids costly social interactions
    - Focuses on personal survival
    - Explores to maximize personal gain

    Examples:
        >>> policy = SelfishPolicy()
        >>> action = policy.choose_action(sensor_data, agent)
        >>> # Returns RestAction if low energy
        >>> # Returns GatherAction if resources nearby
        >>> # Returns MoveAction to explore otherwise
    """

    def __init__(self) -> None:
        """Initialize a SelfishPolicy."""
        super().__init__(
            name="Selfish",
            description="Prioritize individual survival and resource gathering"
        )

    def choose_action(
        self,
        sensor_data: Any,
        agent: Agent
    ) -> Optional[Action]:
        """
        Choose action based on selfish strategy.

        Implements the Strategy pattern's decision algorithm for
        self-interested behavior.

        Args:
            sensor_data (Any): Sensor information from environment
                              (currently simple dict, will be SensorData type)
            agent (Agent): The agent making the decision

        Returns:
            Optional[Action]: The chosen action based on selfish priorities

        Note:
            Decision logic:
            1. Check survival needs (energy, health)
            2. Look for resources to gather
            3. Explore for more opportunities
            4. Never collaborate or share
        """
        # Priority 1: Survival - Low Energy
        if agent.energy < 30:
            # If critical, rest immediately
            if agent.energy < 15:
                return RestAction()

            # Otherwise, try to find food
            # For now, just rest (will integrate with sensor data later)
            return RestAction()

        # Priority 2: Safety - Low Health
        if agent.health < 30:
            # Rest to recover
            return RestAction()

        # Priority 3: Resource Hoarding - Gather if available
        # Check if there are resources in current cell
        # Extract world from sensor_data
        world = sensor_data.get("world") if isinstance(sensor_data, dict) else None
        if not world:
            # Fallback: rest if we can't access world
            return RestAction()

        current_cell = world.get_cell(agent.position)

        if current_cell and current_cell.resources:
            # Gather any available resource
            return GatherAction()

        # Priority 4: Exploration - Move randomly to find resources
        # Get valid adjacent positions
        neighbors = agent.position.get_neighbors()
        valid_moves = []

        for neighbor_pos in neighbors:
            if neighbor_pos.is_within_bounds(world.width, world.height):
                cell = world.get_cell(neighbor_pos)
                if cell and cell.is_traversable():
                    valid_moves.append(neighbor_pos)

        if valid_moves:
            # Choose random direction to explore
            target = random.choice(valid_moves)
            return MoveAction(target)

        # Fallback: Rest if can't do anything else
        return RestAction()

    def __repr__(self) -> str:
        """
        String representation.

        Returns:
            str: Detailed representation
        """
        return f"SelfishPolicy(priority='survival,resources,exploration')"
