"""
BasicAgent Module - Simple Rule-Based Agent

This module provides a straightforward concrete implementation of the Agent
abstract base class, demonstrating simple rule-based decision making integrated
with the Strategy and Command patterns.

Design Patterns:
    - Concrete Implementation of Abstract Base Class
    - Strategy Pattern: Uses DecisionPolicy for behavior
    - Command Pattern: Returns Action objects from decisions

SOLID Principles:
    - Single Responsibility: Simple survival and gathering behavior
    - Liskov Substitution: Can be used anywhere Agent is expected
    - Dependency Inversion: Depends on Agent, Policy, and Action abstractions
"""

from __future__ import annotations
from typing import Optional, Any, TYPE_CHECKING

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import Agent
from traits import AgentTraits
from world.position import Position
from policies.policy import DecisionPolicy
from policies.selfish import SelfishPolicy

if TYPE_CHECKING:
    from world.world import World
    from actions.action import Action


class BasicAgent(Agent):
    """
    Simple rule-based agent demonstrating Strategy and Command patterns.

    BasicAgent uses a DecisionPolicy (Strategy pattern) to choose
    Actions (Command pattern) based on environmental conditions and
    internal state.

    By default, uses SelfishPolicy which prioritizes:
    1. If low energy (< 30) → rest or gather food
    2. If low health (< 30) → rest to recover
    3. If resources nearby → gather them
    4. Otherwise → explore randomly

    The policy can be swapped at runtime, demonstrating the Strategy
    pattern's flexibility:
        >>> agent.policy = CooperativePolicy()  # Change behavior

    This agent demonstrates integration of:
    - Template Method (inherited from Agent)
    - Strategy Pattern (swappable DecisionPolicy)
    - Command Pattern (returns Action objects)

    Attributes:
        policy (DecisionPolicy): The decision strategy (default: SelfishPolicy)
    """

    def __init__(
        self,
        name: str,
        position: Position,
        traits: AgentTraits,
        policy: Optional[DecisionPolicy] = None
    ) -> None:
        """
        Initialize a BasicAgent.

        Args:
            name (str): Agent's name
            position (Position): Starting position
            traits (AgentTraits): Agent characteristics
            policy (Optional[DecisionPolicy]): Decision policy (default: SelfishPolicy)

        Examples:
            >>> from traits import TraitGenerator
            >>> from policies.selfish import SelfishPolicy
            >>> traits = TraitGenerator.balanced_traits()
            >>> agent = BasicAgent("Alice", Position(10, 10), traits)
            >>> # Or with custom policy
            >>> agent = BasicAgent("Bob", Position(5, 5), traits, SelfishPolicy())
        """
        super().__init__(name, position, traits)
        self._policy: DecisionPolicy = policy if policy else SelfishPolicy()

    @property
    def policy(self) -> DecisionPolicy:
        """Get the current decision policy."""
        return self._policy

    @policy.setter
    def policy(self, value: DecisionPolicy) -> None:
        """
        Set a new decision policy (demonstrates Strategy pattern).

        Args:
            value (DecisionPolicy): The new policy
        """
        self._policy = value

    def sense(self, world: World) -> Any:
        """
        Sense nearby entities within vision radius.

        For BasicAgent, sensing is simplified - just returns a basic
        dictionary with nearby information. More sophisticated agents
        might use a SensorData object.

        Args:
            world (World): The world instance

        Returns:
            Any: Dictionary with sensor information (simplified for now)

        Note:
            Current implementation is simple. Future enhancements could:
            - Use vision radius based on agent traits
            - Create structured SensorData object
            - Filter information based on perception skills
        """
        # Simple sensing: just gather basic info about current cell
        current_cell = world.get_cell(self.position)

        sensor_data = {
            "current_cell": current_cell,
            "has_resources": bool(current_cell and current_cell.resources),
            "position": self.position,
            "world": world
        }

        return sensor_data

    def decide(self, sensor_data: Any) -> Optional[Action]:
        """
        Delegate decision to the policy (Strategy pattern).

        This demonstrates the Strategy pattern - the decision algorithm
        is delegated to the DecisionPolicy object, which can be swapped
        at runtime.

        Args:
            sensor_data (Any): Sensed information from environment

        Returns:
            Optional[Action]: Action chosen by the policy

        Note:
            This is the key integration point for the Strategy pattern.
            The agent doesn't contain decision logic - it delegates to
            the policy, allowing behavior to be changed by swapping policies.
        """
        return self._policy.choose_action(sensor_data, self)

    def act(self, action: Action, world: World) -> None:
        """
        Execute the chosen action (Command pattern).

        This demonstrates the Command pattern - the action object
        encapsulates the request and knows how to execute itself.

        Args:
            action (Action): The action to execute
            world (World): The world instance

        Note:
            The agent doesn't contain action execution logic - it
            delegates to the Action object's execute() method.
            This is the Command pattern in action.
        """
        if action is None:
            return

        # Execute the action (Command pattern)
        action.execute(self, world)

    def __repr__(self) -> str:
        """
        String representation of BasicAgent.

        Returns:
            str: Detailed representation
        """
        return (
            f"BasicAgent("
            f"name={self.name}, "
            f"policy={self._policy.name}, "
            f"pos={self.position}, "
            f"health={self.health:.1f}, "
            f"energy={self.energy:.1f})"
        )
