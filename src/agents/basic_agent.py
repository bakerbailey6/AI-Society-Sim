"""
BasicAgent Module - Simple Rule-Based Agent

This module provides a straightforward concrete implementation of the Agent
abstract base class, demonstrating simple rule-based decision making.

Design Patterns:
    - Concrete Implementation of Abstract Base Class
    - Rule-Based System: Simple if-then decision logic

SOLID Principles:
    - Single Responsibility: Simple survival and gathering behavior
    - Liskov Substitution: Can be used anywhere Agent is expected
    - Dependency Inversion: Depends on Agent abstraction
"""

from __future__ import annotations
from typing import Optional, Any, TYPE_CHECKING

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import Agent
from traits import AgentTraits
from world.position import Position

if TYPE_CHECKING:
    from world.world import World


class BasicAgent(Agent):
    """
    Simple rule-based agent with straightforward behavior.

    BasicAgent follows simple heuristics in priority order:
    1. If low energy (< 30) → seek food
    2. If low health (< 30) → avoid threats and heal
    3. If sees valuable resource → gather it
    4. Otherwise → explore randomly

    This agent demonstrates the simplest implementation of the Agent
    interface, suitable for basic simulations and testing.

    Note:
        Actual implementation of sense/decide/act will be completed
        once the behavior system (SensorData, Action classes) is implemented.
        For now, methods raise NotImplementedError.
    """

    def __init__(
        self,
        name: str,
        position: Position,
        traits: AgentTraits
    ) -> None:
        """
        Initialize a BasicAgent.

        Args:
            name (str): Agent's name
            position (Position): Starting position
            traits (AgentTraits): Agent characteristics

        Examples:
            >>> from traits import TraitGenerator
            >>> traits = TraitGenerator.balanced_traits()
            >>> agent = BasicAgent("Alice", Position(10, 10), traits)
        """
        super().__init__(name, position, traits)

    def sense(self, world: World) -> Any:
        """
        Sense nearby entities within vision radius.

        Implementation will:
        - Use world.get_cells_in_radius() to get nearby cells
        - Collect visible resources
        - Detect other agents
        - Gather terrain information

        Args:
            world (World): The world instance

        Returns:
            Any: Perceived information (SensorData once behavior system exists)

        Note:
            To be implemented once behavior system exists.
        """
        raise NotImplementedError(
            "sense() will be implemented once behavior system (SensorData) exists"
        )

    def decide(self, sensor_data: Any) -> Optional[Any]:
        """
        Simple rule-based decision making.

        Decision logic (priority order):
        1. SURVIVAL: If energy < 30, find nearest food
        2. SAFETY: If health < 30 and threats nearby, flee
        3. OPPORTUNITY: If valuable resource nearby, gather it
        4. EXPLORATION: Move randomly to explore

        Args:
            sensor_data (Any): Sensed information from environment

        Returns:
            Optional[Any]: Chosen action (Action class once behavior system exists)

        Note:
            To be implemented once behavior system (Action classes) exists.
        """
        raise NotImplementedError(
            "decide() will be implemented once behavior system (Action classes) exists"
        )

    def act(self, action: Any, world: World) -> None:
        """
        Execute the chosen action.

        Implementation will:
        - Validate action can be executed
        - Execute action (move, gather, etc.)
        - Consume energy based on action cost
        - Update world state

        Args:
            action (Any): The action to execute
            world (World): The world instance

        Note:
            To be implemented once behavior system (Action classes) exists.
        """
        raise NotImplementedError(
            "act() will be implemented once behavior system (Action classes) exists"
        )

    def __repr__(self) -> str:
        """
        String representation of BasicAgent.

        Returns:
            str: Detailed representation
        """
        return (
            f"BasicAgent("
            f"name={self.name}, "
            f"pos={self.position}, "
            f"health={self.health:.1f}, "
            f"energy={self.energy:.1f})"
        )
