"""
AgentFactory Module - Factory Method Pattern for Agent Creation

This module demonstrates the Factory Method pattern by providing abstract
and concrete factories for creating different types of agents.

Design Patterns:
    - Factory Method: Abstract creation interface with concrete implementations
    - Registry Pattern: Central factory lookup

SOLID Principles:
    - Open/Closed: New agent types via new factories, no modification needed
    - Dependency Inversion: Depends on Agent abstraction, not concrete types
    - Single Responsibility: Each factory creates one agent type
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Dict, List, Any

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import Agent
from basic_agent import BasicAgent
from learning_agent import LearningAgent
from ai_agent import AIAgent
from npc_agent import NPCAgent
from traits import AgentTraits, TraitGenerator
from world.position import Position


class AgentFactory(ABC):
    """
    Abstract factory for creating agents.

    This abstract base class defines the interface for agent creation,
    allowing subclasses to determine the specific agent type to create.

    Design Pattern:
        - Factory Method: Abstract creation interface
        - Template Method: Common setup logic in base class

    SOLID:
        - Open/Closed: Extend via subclassing, don't modify
        - Dependency Inversion: Returns Agent abstraction
    """

    @abstractmethod
    def create_agent(
        self,
        name: str,
        position: Position,
        traits: Optional[AgentTraits] = None,
        **kwargs
    ) -> Agent:
        """
        Create an agent.

        This is the factory method that subclasses must implement
        to create their specific agent type.

        Args:
            name (str): Agent's name
            position (Position): Starting position
            traits (Optional[AgentTraits]): Agent traits (None = random)
            **kwargs: Additional agent-specific parameters

        Returns:
            Agent: Created agent instance
        """
        pass

    def _generate_traits(self, traits: Optional[AgentTraits]) -> AgentTraits:
        """
        Generate or use provided traits.

        Helper method to ensure agent has traits, generating random
        traits if none provided.

        Args:
            traits (Optional[AgentTraits]): Provided traits or None

        Returns:
            AgentTraits: Traits to use
        """
        return traits if traits is not None else TraitGenerator.random_traits()


class BasicAgentFactory(AgentFactory):
    """
    Factory for creating BasicAgents.

    Creates simple rule-based agents with straightforward behavior.
    """

    def create_agent(
        self,
        name: str,
        position: Position,
        traits: Optional[AgentTraits] = None,
        **kwargs
    ) -> BasicAgent:
        """
        Create a BasicAgent.

        Args:
            name (str): Agent's name
            position (Position): Starting position
            traits (Optional[AgentTraits]): Agent traits
            **kwargs: Ignored for BasicAgent

        Returns:
            BasicAgent: Created basic agent

        Examples:
            >>> factory = BasicAgentFactory()
            >>> agent = factory.create_agent("Alice", Position(10, 10))
        """
        agent_traits = self._generate_traits(traits)
        return BasicAgent(name, position, agent_traits)


class LearningAgentFactory(AgentFactory):
    """
    Factory for creating LearningAgents.

    Creates agents that use Q-learning to adapt their behavior.
    """

    def create_agent(
        self,
        name: str,
        position: Position,
        traits: Optional[AgentTraits] = None,
        learning_rate: float = 0.1,
        discount_factor: float = 0.95,
        epsilon: float = 0.1,
        **kwargs
    ) -> LearningAgent:
        """
        Create a LearningAgent.

        Args:
            name (str): Agent's name
            position (Position): Starting position
            traits (Optional[AgentTraits]): Agent traits
            learning_rate (float): Q-learning learning rate
            discount_factor (float): Q-learning discount factor
            epsilon (float): Exploration rate
            **kwargs: Additional ignored parameters

        Returns:
            LearningAgent: Created learning agent

        Examples:
            >>> factory = LearningAgentFactory()
            >>> agent = factory.create_agent("Bob", Position(15, 15),
            ...                              learning_rate=0.15, epsilon=0.2)
        """
        agent_traits = self._generate_traits(traits)
        return LearningAgent(
            name, position, agent_traits,
            learning_rate, discount_factor, epsilon
        )


class AIAgentFactory(AgentFactory):
    """
    Factory for creating AIAgents.

    Creates agents powered by Large Language Models.

    Attributes:
        default_api_key (Optional[str]): Default API key for all created agents
    """

    def __init__(self, default_api_key: Optional[str] = None):
        """
        Initialize AIAgentFactory.

        Args:
            default_api_key (Optional[str]): Default API key for created agents
        """
        self.default_api_key = default_api_key

    def create_agent(
        self,
        name: str,
        position: Position,
        traits: Optional[AgentTraits] = None,
        api_key: Optional[str] = None,
        model: str = "claude-3-5-sonnet-20241022",
        **kwargs
    ) -> AIAgent:
        """
        Create an AIAgent.

        Args:
            name (str): Agent's name
            position (Position): Starting position
            traits (Optional[AgentTraits]): Agent traits
            api_key (Optional[str]): API key (uses default if not provided)
            model (str): LLM model identifier
            **kwargs: Additional ignored parameters

        Returns:
            AIAgent: Created AI agent

        Examples:
            >>> factory = AIAgentFactory(default_api_key="sk-...")
            >>> agent = factory.create_agent("Charlie", Position(20, 20))
        """
        agent_traits = self._generate_traits(traits)
        key = api_key or self.default_api_key
        return AIAgent(name, position, agent_traits, key, model)


class NPCAgentFactory(AgentFactory):
    """
    Factory for creating NPCAgents.

    Creates agents with scripted, predefined behaviors.
    """

    def create_agent(
        self,
        name: str,
        position: Position,
        traits: Optional[AgentTraits] = None,
        behavior_script: Optional[List] = None,
        loop_script: bool = True,
        **kwargs
    ) -> NPCAgent:
        """
        Create an NPCAgent.

        Args:
            name (str): Agent's name
            position (Position): Starting position
            traits (Optional[AgentTraits]): Agent traits
            behavior_script (Optional[List]): Behavior function sequence
            loop_script (bool): Whether to loop script
            **kwargs: Additional ignored parameters

        Returns:
            NPCAgent: Created NPC agent

        Examples:
            >>> factory = NPCAgentFactory()
            >>> agent = factory.create_agent("Guard", Position(30, 30))
        """
        agent_traits = self._generate_traits(traits)
        return NPCAgent(name, position, agent_traits, behavior_script, loop_script)


class AgentFactoryRegistry:
    """
    Registry for agent factories using Singleton pattern.

    Provides centralized factory lookup and management,
    allowing dynamic agent creation by type name.

    Design Pattern:
        - Registry Pattern: Central factory lookup
        - Singleton Pattern: Single registry instance

    Examples:
        >>> registry = AgentFactoryRegistry()
        >>> registry.register_factory("basic", BasicAgentFactory())
        >>> agent = registry.create_agent("basic", "Alice", Position(10, 10))
    """

    _instance: Optional[AgentFactoryRegistry] = None

    def __new__(cls):
        """
        Ensure single instance (Singleton pattern).

        Returns:
            AgentFactoryRegistry: The singleton instance
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._factories: Dict[str, AgentFactory] = {}
            cls._instance._initialize_default_factories()
        return cls._instance

    def _initialize_default_factories(self) -> None:
        """Initialize registry with default factories."""
        self._factories = {
            "basic": BasicAgentFactory(),
            "learning": LearningAgentFactory(),
            "ai": AIAgentFactory(),
            "npc": NPCAgentFactory()
        }

    def register_factory(self, agent_type: str, factory: AgentFactory) -> None:
        """
        Register a factory for an agent type.

        Args:
            agent_type (str): Type identifier (e.g., "basic", "learning")
            factory (AgentFactory): Factory instance

        Examples:
            >>> registry = AgentFactoryRegistry()
            >>> registry.register_factory("custom", CustomAgentFactory())
        """
        self._factories[agent_type] = factory

    def unregister_factory(self, agent_type: str) -> Optional[AgentFactory]:
        """
        Unregister a factory.

        Args:
            agent_type (str): Type identifier to remove

        Returns:
            Optional[AgentFactory]: Removed factory if it existed
        """
        return self._factories.pop(agent_type, None)

    def create_agent(
        self,
        agent_type: str,
        name: str,
        position: Position,
        **kwargs
    ) -> Agent:
        """
        Create agent using registered factory.

        Args:
            agent_type (str): Type identifier ("basic", "learning", "ai", "npc")
            name (str): Agent's name
            position (Position): Starting position
            **kwargs: Agent-specific parameters (passed to factory)

        Returns:
            Agent: Created agent

        Raises:
            ValueError: If agent_type not registered

        Examples:
            >>> registry = AgentFactoryRegistry()
            >>> agent = registry.create_agent("learning", "Bob", Position(10, 10),
            ...                              learning_rate=0.15)
        """
        if agent_type not in self._factories:
            raise ValueError(
                f"No factory registered for type: {agent_type}. "
                f"Available types: {list(self._factories.keys())}"
            )

        factory = self._factories[agent_type]
        return factory.create_agent(name, position, **kwargs)

    def get_registered_types(self) -> List[str]:
        """
        Get list of registered agent types.

        Returns:
            List[str]: Registered type identifiers

        Examples:
            >>> registry = AgentFactoryRegistry()
            >>> types = registry.get_registered_types()
            >>> print(types)
            ['basic', 'learning', 'ai', 'npc']
        """
        return list(self._factories.keys())

    def has_factory(self, agent_type: str) -> bool:
        """
        Check if a factory is registered for a type.

        Args:
            agent_type (str): Type identifier

        Returns:
            bool: True if factory is registered
        """
        return agent_type in self._factories

    def clear_registry(self) -> None:
        """Clear all registered factories."""
        self._factories.clear()

    def reset_to_defaults(self) -> None:
        """Reset registry to default factories."""
        self._initialize_default_factories()


# Convenience function for easy agent creation
def create_agent(
    agent_type: str,
    name: str,
    position: Position,
    **kwargs
) -> Agent:
    """
    Convenience function for creating agents.

    Uses the AgentFactoryRegistry singleton to create agents
    by type name.

    Args:
        agent_type (str): Agent type ("basic", "learning", "ai", "npc")
        name (str): Agent's name
        position (Position): Starting position
        **kwargs: Agent-specific parameters

    Returns:
        Agent: Created agent

    Raises:
        ValueError: If agent_type not registered

    Examples:
        >>> agent = create_agent("basic", "Alice", Position(10, 10))
        >>> agent = create_agent("learning", "Bob", Position(15, 15),
        ...                     learning_rate=0.15, epsilon=0.2)
    """
    registry = AgentFactoryRegistry()
    return registry.create_agent(agent_type, name, position, **kwargs)
