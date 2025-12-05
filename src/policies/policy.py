"""
DecisionPolicy Module - Abstract Base Class for Decision Strategies

This module provides the abstract base class for all decision policies,
demonstrating the Strategy pattern.

Design Patterns:
    - Strategy Pattern: Policies are interchangeable decision algorithms
    - Dependency Inversion: Depends on Agent/World abstractions

SOLID Principles:
    - Single Responsibility: Policies only make decisions
    - Open/Closed: New policies extend without modifying base
    - Liskov Substitution: All policies substitutable for DecisionPolicy
    - Interface Segregation: Minimal interface (choose_action only)
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Optional, Any

if TYPE_CHECKING:
    from agents.agent import Agent
    from actions.action import Action


class DecisionPolicy(ABC):
    """
    Abstract base class for all decision policies.

    This class demonstrates the Strategy pattern by defining a family
    of interchangeable decision algorithms. Each policy encapsulates
    a different strategy for choosing actions based on sensor data
    and agent state.

    The Strategy pattern enables:
    - Swapping decision algorithms at runtime
    - Adding new strategies without modifying existing code
    - Testing different strategies independently
    - Agents changing behavior based on context

    Decision policies represent different behavioral philosophies:
    - SelfishPolicy: Individual survival, resource hoarding
    - CooperativePolicy: Group benefit, sharing, collaboration
    - AggressivePolicy: Competition, conflict, territory control
    - LearningPolicy: Q-learning or other ML-based decisions
    - AIPolicy: LLM-driven decisions

    Note:
        This is an abstract class demonstrating the Strategy pattern.
        Concrete policy subclasses must implement choose_action().

    Examples:
        >>> # Concrete policy implementation
        >>> class MyPolicy(DecisionPolicy):
        ...     def choose_action(self, sensor_data, agent):
        ...         if agent.energy < 30:
        ...             return RestAction()
        ...         return GatherAction()
        ...
        >>> # Agents can swap policies dynamically
        >>> agent.policy = SelfishPolicy()  # Hoard resources
        >>> agent.policy = CooperativePolicy()  # Share resources
    """

    def __init__(self, name: str, description: str = "") -> None:
        """
        Initialize a decision policy.

        Args:
            name (str): Policy name
            description (str, optional): Policy description
        """
        self._name: str = name
        self._description: str = description

    @property
    def name(self) -> str:
        """Get the policy name."""
        return self._name

    @property
    def description(self) -> str:
        """Get the policy description."""
        return self._description

    @abstractmethod
    def choose_action(
        self,
        sensor_data: Any,
        agent: Agent
    ) -> Optional[Action]:
        """
        Choose an action based on the policy's strategy.

        This is the core method of the Strategy pattern. It encapsulates
        the decision algorithm, allowing different policies to make
        different choices given the same inputs.

        Args:
            sensor_data (Any): Information from agent's sense() method
                              (will be SensorData type when behavior system exists)
            agent (Agent): The agent making the decision

        Returns:
            Optional[Action]: The chosen action, or None for no action

        Note:
            Subclasses must implement their decision logic here.
            The method should:
            1. Analyze sensor data (nearby resources, agents, threats)
            2. Consider agent's internal state (energy, health, inventory)
            3. Apply the policy's strategy (selfish, cooperative, etc.)
            4. Return the best action according to that strategy

            Different policies will make different choices:
            - SelfishPolicy: Prioritize personal survival and resources
            - CooperativePolicy: Prioritize group benefit
            - AggressivePolicy: Prioritize competition and conflict

        Examples:
            >>> # Selfish policy prioritizes survival
            >>> selfish = SelfishPolicy()
            >>> action = selfish.choose_action(sensor_data, agent)
            >>> # Returns GatherAction if resources nearby
            >>>
            >>> # Cooperative policy prioritizes sharing
            >>> coop = CooperativePolicy()
            >>> action = coop.choose_action(sensor_data, agent)
            >>> # Returns TradeAction if ally nearby
        """
        pass

    def __repr__(self) -> str:
        """
        String representation of the policy.

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
