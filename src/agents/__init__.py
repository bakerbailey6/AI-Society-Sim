"""
Agents Package

Provides core agent abstractions, concrete implementations, and factory
patterns for creating autonomous agents in the simulation.

This package demonstrates multiple design patterns:
- Abstract Base Class (Agent)
- Template Method (Agent.update)
- Factory Method (AgentFactory)
- Value Object (AgentTraits)
- Registry Pattern (AgentFactoryRegistry)
- Manager Pattern (AgentManager)
- Strategy Pattern (Pluggable behaviors)

Modules:
    agent: Abstract Agent base class
    traits: Immutable agent characteristics
    basic_agent: Simple rule-based agent
    learning_agent: Q-learning reinforcement learning agent
    ai_agent: LLM-powered agent (optional)
    npc_agent: Scripted behavior agent
    agent_factory: Factory Method pattern for agent creation
    agent_manager: Centralized agent lifecycle management

SOLID Principles:
    All classes follow SOLID principles:
    - Single Responsibility
    - Open/Closed
    - Liskov Substitution
    - Interface Segregation
    - Dependency Inversion

Examples:
    >>> from agents import create_agent, AgentManager, TraitGenerator
    >>> from world.position import Position
    >>>
    >>> # Create agents
    >>> agent1 = create_agent("basic", "Alice", Position(10, 10))
    >>> agent2 = create_agent("learning", "Bob", Position(15, 15),
    ...                      learning_rate=0.15)
    >>>
    >>> # Manage agents
    >>> manager = AgentManager()
    >>> manager.register_agent(agent1)
    >>> manager.register_agent(agent2)
    >>>
    >>> # Update all agents
    >>> manager.update_all_agents(world)
"""

# Core abstractions
from .agent import Agent, AgentState

# Value objects
from .traits import AgentTraits, TraitGenerator

# Concrete agent implementations
from .basic_agent import BasicAgent
from .learning_agent import LearningAgent
from .ai_agent import AIAgent
from .npc_agent import NPCAgent

# Factories
from .agent_factory import (
    AgentFactory,
    BasicAgentFactory,
    LearningAgentFactory,
    AIAgentFactory,
    NPCAgentFactory,
    AgentFactoryRegistry,
    create_agent
)

# Management
from .agent_manager import AgentManager

# Define public API
__all__ = [
    # Core abstractions
    'Agent',
    'AgentState',

    # Value objects
    'AgentTraits',
    'TraitGenerator',

    # Concrete agent types
    'BasicAgent',
    'LearningAgent',
    'AIAgent',
    'NPCAgent',

    # Factory classes
    'AgentFactory',
    'BasicAgentFactory',
    'LearningAgentFactory',
    'AIAgentFactory',
    'NPCAgentFactory',
    'AgentFactoryRegistry',

    # Convenience functions
    'create_agent',

    # Management
    'AgentManager',
]

# Package metadata
__version__ = '0.1.0'
__author__ = 'CS455 Design Patterns - Final Project'
__description__ = 'Agent system for Emergent AI Society Simulator'
