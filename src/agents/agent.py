"""
Agent Module - Abstract Agent Base Class

This module provides an abstract base class for all autonomous agents in the
simulation, demonstrating the Template Method pattern and inheritance hierarchies.

Design Patterns:
    - Template Method: update() method orchestrates sense-decide-act cycle
    - Abstract Base Class: Defines interface for all agents

SOLID Principles:
    - Single Responsibility: Manages only agent state and lifecycle
    - Open/Closed: New agent types can be added without modifying existing code
    - Liskov Substitution: All agent subclasses are substitutable for Agent
    - Dependency Inversion: Depends on abstractions (Position, World)
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, TYPE_CHECKING
from enum import Enum
import uuid

# Import marker interfaces
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from world.markers import IObservable
from world.position import Position

# Avoid circular imports with TYPE_CHECKING
if TYPE_CHECKING:
    from world.world import World
    from traits import AgentTraits


class AgentState(Enum):
    """
    Enumeration of possible agent states.

    Attributes:
        ALIVE: Agent is active and can perform actions
        DEAD: Agent is inactive and cannot perform actions
        INACTIVE: Agent is temporarily inactive (sleeping, stunned, etc.)
    """
    ALIVE = "alive"
    DEAD = "dead"
    INACTIVE = "inactive"


class Agent(IObservable, ABC):
    """
    Abstract base class for all agents in the simulation.

    Agents are autonomous entities that perceive their environment,
    make decisions, and execute actions. This class defines the core
    interface and lifecycle that all agents must implement.

    The agent lifecycle follows a sense-decide-act pattern:
    1. SENSE: Perceive the environment and gather information
    2. DECIDE: Choose an action based on perception and internal state
    3. ACT: Execute the chosen action in the world

    All agents are observable (IObservable marker), meaning they can
    be detected by other agents during their sensing phase.

    Attributes:
        agent_id (str): Unique identifier for this agent
        name (str): Human-readable name
        position (Position): Current position in the world
        state (AgentState): Current state (ALIVE, DEAD, or INACTIVE)
        traits (AgentTraits): Immutable characteristics
        energy (float): Current energy level (0-max_energy)
        max_energy (float): Maximum energy capacity
        health (float): Current health (0-max_health)
        max_health (float): Maximum health capacity
        age (int): Agent's age in timesteps

    Note:
        This class demonstrates the Template Method pattern through the
        update() method, which orchestrates the agent lifecycle while
        delegating specific implementations to subclasses.
    """

    def __init__(
        self,
        name: str,
        position: Position,
        traits: AgentTraits
    ) -> None:
        """
        Initialize an agent.

        Args:
            name (str): Agent's name
            position (Position): Starting position in the world
            traits (AgentTraits): Immutable agent characteristics

        Examples:
            >>> from traits import AgentTraits, TraitGenerator
            >>> traits = TraitGenerator.balanced_traits()
            >>> agent = ConcreteAgent("Alice", Position(10, 10), traits)
        """
        self._agent_id: str = str(uuid.uuid4())
        self._name: str = name
        self._position: Position = position
        self._traits: AgentTraits = traits
        self._state: AgentState = AgentState.ALIVE

        # Core attributes
        self._energy: float = 100.0
        self._max_energy: float = 100.0
        self._health: float = 100.0
        self._max_health: float = 100.0
        self._age: int = 0

        # Inventory placeholder (will integrate with economy system later)
        self._inventory: Dict[str, float] = {}

    # --- Properties ---

    @property
    def agent_id(self) -> str:
        """Get the unique agent identifier."""
        return self._agent_id

    @property
    def name(self) -> str:
        """Get the agent's name."""
        return self._name

    @property
    def position(self) -> Position:
        """Get the current position."""
        return self._position

    @position.setter
    def position(self, value: Position) -> None:
        """
        Set the agent's position.

        Args:
            value (Position): New position
        """
        self._position = value

    @property
    def state(self) -> AgentState:
        """Get the current agent state."""
        return self._state

    @property
    def traits(self) -> AgentTraits:
        """Get the immutable agent traits."""
        return self._traits

    @property
    def energy(self) -> float:
        """Get the current energy level."""
        return self._energy

    @property
    def max_energy(self) -> float:
        """Get the maximum energy capacity."""
        return self._max_energy

    @property
    def health(self) -> float:
        """Get the current health."""
        return self._health

    @property
    def max_health(self) -> float:
        """Get the maximum health capacity."""
        return self._max_health

    @property
    def age(self) -> int:
        """Get the agent's age in timesteps."""
        return self._age

    @property
    def inventory(self) -> Dict[str, float]:
        """
        Get a copy of the inventory.

        Returns:
            Dict[str, float]: Copy of inventory (modifications don't affect agent)
        """
        return self._inventory.copy()

    # --- Template Method Pattern ---

    def update(self, world: World) -> None:
        """
        Template method defining the agent update lifecycle.

        This method orchestrates the sense-decide-act cycle:
        1. SENSE: Perceive the environment
        2. DECIDE: Choose an action based on perception
        3. ACT: Execute the chosen action
        4. UPDATE: Update agent state (energy, health, age)

        Subclasses should NOT override this method. Instead,
        override the individual phase methods (sense, decide, act).

        Args:
            world (World): The world instance

        Note:
            This is the Template Method pattern - the algorithm structure
            is defined here, but specific steps are implemented by subclasses.
        """
        # Skip update if agent is not alive
        if self._state != AgentState.ALIVE:
            return

        # Phase 1: Sense
        sensor_data = self.sense(world)

        # Phase 2: Decide
        action = self.decide(sensor_data)

        # Phase 3: Act
        if action is not None:
            self.act(action, world)

        # Update agent state
        self._age += 1
        self._update_energy()
        self._update_health()

    # --- Abstract Methods (must be implemented by subclasses) ---

    @abstractmethod
    def sense(self, world: World) -> Any:
        """
        Phase 1: Sense the environment.

        Subclasses must implement their perception logic here.
        This method gathers information about the world that the
        agent can perceive based on its vision radius and capabilities.

        Args:
            world (World): The world instance

        Returns:
            Any: Perceived information (will be SensorData in behavior system)

        Note:
            The return type will be SensorData once the behavior system
            is implemented. For now, subclasses can return any structure.
        """
        pass

    @abstractmethod
    def decide(self, sensor_data: Any) -> Optional[Any]:
        """
        Phase 2: Decide on an action.

        Subclasses must implement their decision-making logic here.
        Based on sensed information and internal state, choose the
        best action to execute.

        Args:
            sensor_data (Any): Information from the sensing phase

        Returns:
            Optional[Any]: Chosen action to execute, or None for no action
                          (will be Action type once behavior system is implemented)

        Note:
            The parameter and return types will be more specific once
            the behavior system (SensorData, Action) is implemented.
        """
        pass

    @abstractmethod
    def act(self, action: Any, world: World) -> None:
        """
        Phase 3: Execute the chosen action.

        Subclasses must implement their action execution logic here.

        Args:
            action (Any): The action to execute (will be Action type)
            world (World): The world instance

        Note:
            The action parameter type will be more specific once
            the behavior system is implemented.
        """
        pass

    # --- Concrete Methods (default implementations) ---

    def consume_energy(self, amount: float) -> bool:
        """
        Consume energy for performing actions.

        Args:
            amount (float): Amount of energy to consume

        Returns:
            bool: True if sufficient energy was available, False otherwise

        Examples:
            >>> if agent.consume_energy(5.0):
            ...     # Perform action
            ...     pass
        """
        if self._energy >= amount:
            self._energy -= amount
            return True
        return False

    def restore_energy(self, amount: float) -> None:
        """
        Restore energy (from eating, resting, etc.).

        Args:
            amount (float): Amount of energy to restore

        Note:
            Energy cannot exceed max_energy.
        """
        self._energy = min(self._max_energy, self._energy + amount)

    def take_damage(self, amount: float) -> None:
        """
        Reduce health from damage.

        Args:
            amount (float): Damage amount

        Note:
            If health reaches 0, agent state becomes DEAD.
        """
        self._health -= amount
        if self._health <= 0:
            self._health = 0
            self._state = AgentState.DEAD

    def heal(self, amount: float) -> None:
        """
        Restore health.

        Args:
            amount (float): Amount of health to restore

        Note:
            Health cannot exceed max_health.
        """
        self._health = min(self._max_health, self._health + amount)

    def is_alive(self) -> bool:
        """
        Check if agent is alive.

        Returns:
            bool: True if agent state is ALIVE
        """
        return self._state == AgentState.ALIVE

    def die(self) -> None:
        """Mark agent as dead."""
        self._state = AgentState.DEAD
        self._health = 0

    def set_inactive(self) -> None:
        """Mark agent as temporarily inactive."""
        self._state = AgentState.INACTIVE

    def set_active(self) -> None:
        """Reactivate agent (if not dead)."""
        if self._state != AgentState.DEAD:
            self._state = AgentState.ALIVE

    # --- Private Helper Methods ---

    def _update_energy(self) -> None:
        """
        Update energy levels (passive consumption over time).

        Agents lose energy each timestep due to base metabolism.
        If energy reaches 0, health starts decreasing.
        """
        # Base metabolism: lose 0.5 energy per timestep
        base_metabolism = 0.5
        self._energy = max(0, self._energy - base_metabolism)

        # Starving reduces health
        if self._energy <= 0:
            self.take_damage(1.0)

    def _update_health(self) -> None:
        """
        Update health based on current conditions.

        Agents naturally regenerate health when well-fed.
        """
        # Natural regeneration if well-fed (energy > 50)
        if self._energy > 50:
            self.heal(0.1)

    def __repr__(self) -> str:
        """
        String representation of agent.

        Returns:
            str: Human-readable representation
        """
        return (
            f"{self.__class__.__name__}("
            f"id={self._agent_id[:8]}, "
            f"name={self._name}, "
            f"pos={self._position}, "
            f"health={self._health:.1f}, "
            f"energy={self._energy:.1f})"
        )

    def __str__(self) -> str:
        """
        String representation for display.

        Returns:
            str: Display string
        """
        return f"{self._name} at {self._position}"
