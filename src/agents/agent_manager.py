"""
AgentManager Module - Agent Lifecycle Management

This module provides centralized management of agent lifecycle,
batch operations, and queries using the Manager pattern.

Design Patterns:
    - Manager Pattern: Centralized lifecycle management
    - Repository Pattern: Agent storage and retrieval

SOLID Principles:
    - Single Responsibility: Only manages agent lifecycle
    - Dependency Inversion: Depends on Agent abstraction
"""

from __future__ import annotations
from typing import List, Dict, Optional, Callable, Set, TYPE_CHECKING

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import Agent, AgentState
from world.position import Position

if TYPE_CHECKING:
    from world.world import World


class AgentManager:
    """
    Manages agent lifecycle and batch operations.

    AgentManager handles:
    - Agent registration and deregistration
    - Batch updates for all agents
    - Agent queries and filtering
    - Position indexing for spatial queries
    - Death and cleanup

    The manager maintains both a primary agent registry (by ID)
    and a spatial index (by position) for efficient queries.

    Design Patterns:
        - Manager Pattern: Centralized lifecycle management
        - Repository Pattern: Agent storage and retrieval

    Attributes:
        _agents (Dict[str, Agent]): Primary agent registry by ID
        _agents_by_position (Dict[Position, List[Agent]]): Spatial index
    """

    def __init__(self):
        """
        Initialize AgentManager.

        Examples:
            >>> manager = AgentManager()
            >>> print(manager.count_agents())
            0
        """
        # Primary registry: agent_id -> Agent
        self._agents: Dict[str, Agent] = {}

        # Spatial index: Position -> List[Agent]
        # Allows efficient position-based queries
        self._agents_by_position: Dict[Position, List[Agent]] = {}

    # --- Registration Methods ---

    def register_agent(self, agent: Agent) -> None:
        """
        Register an agent with the manager.

        Args:
            agent (Agent): Agent to register

        Raises:
            ValueError: If agent already registered

        Examples:
            >>> manager = AgentManager()
            >>> agent = create_agent("basic", "Alice", Position(10, 10))
            >>> manager.register_agent(agent)
        """
        if agent.agent_id in self._agents:
            raise ValueError(
                f"Agent {agent.agent_id} ('{agent.name}') already registered"
            )

        self._agents[agent.agent_id] = agent
        self._add_to_position_index(agent)

    def unregister_agent(self, agent_id: str) -> Optional[Agent]:
        """
        Unregister an agent from the manager.

        Args:
            agent_id (str): Agent ID to unregister

        Returns:
            Optional[Agent]: Unregistered agent if found, None otherwise

        Examples:
            >>> agent = manager.unregister_agent("agent-id-123")
            >>> if agent:
            ...     print(f"Removed {agent.name}")
        """
        agent = self._agents.pop(agent_id, None)
        if agent:
            self._remove_from_position_index(agent)
        return agent

    def is_registered(self, agent_id: str) -> bool:
        """
        Check if an agent is registered.

        Args:
            agent_id (str): Agent ID to check

        Returns:
            bool: True if registered
        """
        return agent_id in self._agents

    # --- Retrieval Methods ---

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """
        Get agent by ID.

        Args:
            agent_id (str): Agent ID

        Returns:
            Optional[Agent]: Agent if found, None otherwise

        Examples:
            >>> agent = manager.get_agent("agent-id-123")
            >>> if agent:
            ...     print(agent.name)
        """
        return self._agents.get(agent_id)

    def get_all_agents(self) -> List[Agent]:
        """
        Get all registered agents.

        Returns:
            List[Agent]: List of all agents (copy, not live)

        Examples:
            >>> all_agents = manager.get_all_agents()
            >>> print(f"Total agents: {len(all_agents)}")
        """
        return list(self._agents.values())

    def get_living_agents(self) -> List[Agent]:
        """
        Get all living agents (state == ALIVE).

        Returns:
            List[Agent]: Living agents only

        Examples:
            >>> living = manager.get_living_agents()
            >>> print(f"Living agents: {len(living)}")
        """
        return [agent for agent in self._agents.values() if agent.is_alive()]

    def get_dead_agents(self) -> List[Agent]:
        """
        Get all dead agents (state == DEAD).

        Returns:
            List[Agent]: Dead agents only
        """
        return [agent for agent in self._agents.values()
                if agent.state == AgentState.DEAD]

    def get_agents_at_position(self, position: Position) -> List[Agent]:
        """
        Get agents at a specific position.

        Args:
            position (Position): Position to query

        Returns:
            List[Agent]: Agents at that position (copy)

        Examples:
            >>> agents = manager.get_agents_at_position(Position(10, 10))
            >>> print(f"Agents at (10,10): {len(agents)}")
        """
        return self._agents_by_position.get(position, []).copy()

    def get_agents_in_radius(
        self,
        position: Position,
        radius: int
    ) -> List[Agent]:
        """
        Get agents within radius of a position.

        Uses Euclidean distance for radius calculation.

        Args:
            position (Position): Center position
            radius (int): Search radius

        Returns:
            List[Agent]: Agents within radius

        Examples:
            >>> nearby = manager.get_agents_in_radius(Position(10, 10), radius=5)
            >>> print(f"Agents nearby: {len(nearby)}")
        """
        agents = []
        for agent in self._agents.values():
            if agent.position.distance_to(position) <= radius:
                agents.append(agent)
        return agents

    def filter_agents(self, predicate: Callable[[Agent], bool]) -> List[Agent]:
        """
        Filter agents by custom predicate.

        Args:
            predicate (Callable[[Agent], bool]): Filter function

        Returns:
            List[Agent]: Matching agents

        Examples:
            >>> # Get all agents with health < 50
            >>> low_health = manager.filter_agents(lambda a: a.health < 50)
            >>> # Get all agents of specific type
            >>> basic = manager.filter_agents(lambda a: isinstance(a, BasicAgent))
        """
        return [agent for agent in self._agents.values() if predicate(agent)]

    # --- Update Methods ---

    def update_all_agents(self, world: World) -> None:
        """
        Update all living agents.

        Calls update() on each living agent, then optionally
        cleans up dead agents.

        Args:
            world (World): World instance

        Examples:
            >>> manager.update_all_agents(world)
        """
        # Update only living agents
        for agent in self.get_living_agents():
            agent.update(world)

        # Optional: cleanup dead agents
        # Uncomment if you want automatic cleanup
        # self._cleanup_dead_agents()

    def update_agent_position(self, agent: Agent, old_position: Position) -> None:
        """
        Update position index when agent moves.

        Must be called when an agent's position changes to keep
        the spatial index in sync.

        Args:
            agent (Agent): Agent that moved
            old_position (Position): Previous position

        Examples:
            >>> old_pos = agent.position
            >>> agent.position = Position(11, 11)
            >>> manager.update_agent_position(agent, old_pos)
        """
        self._remove_from_position_index(agent, old_position)
        self._add_to_position_index(agent)

    # --- Statistics Methods ---

    def count_agents(self) -> int:
        """
        Get total agent count.

        Returns:
            int: Number of registered agents

        Examples:
            >>> print(f"Total agents: {manager.count_agents()}")
        """
        return len(self._agents)

    def count_living_agents(self) -> int:
        """
        Get living agent count.

        Returns:
            int: Number of living agents

        Examples:
            >>> print(f"Living: {manager.count_living_agents()}")
        """
        return len(self.get_living_agents())

    def count_dead_agents(self) -> int:
        """
        Get dead agent count.

        Returns:
            int: Number of dead agents
        """
        return len(self.get_dead_agents())

    def get_statistics(self) -> Dict[str, any]:
        """
        Get manager statistics.

        Returns:
            Dict[str, any]: Statistics including counts and averages

        Examples:
            >>> stats = manager.get_statistics()
            >>> print(f"Average health: {stats['avg_health']:.1f}")
        """
        living = self.get_living_agents()

        stats = {
            "total_agents": self.count_agents(),
            "living_agents": len(living),
            "dead_agents": self.count_dead_agents(),
            "avg_health": 0.0,
            "avg_energy": 0.0,
            "avg_age": 0.0
        }

        if living:
            stats["avg_health"] = sum(a.health for a in living) / len(living)
            stats["avg_energy"] = sum(a.energy for a in living) / len(living)
            stats["avg_age"] = sum(a.age for a in living) / len(living)

        return stats

    # --- Cleanup Methods ---

    def clear_all_agents(self) -> None:
        """
        Remove all agents from manager.

        Examples:
            >>> manager.clear_all_agents()
            >>> assert manager.count_agents() == 0
        """
        self._agents.clear()
        self._agents_by_position.clear()

    def cleanup_dead_agents(self) -> int:
        """
        Remove all dead agents from registry.

        Returns:
            int: Number of agents removed

        Examples:
            >>> removed = manager.cleanup_dead_agents()
            >>> print(f"Removed {removed} dead agents")
        """
        return self._cleanup_dead_agents()

    # --- Private Helper Methods ---

    def _add_to_position_index(self, agent: Agent) -> None:
        """
        Add agent to spatial index.

        Args:
            agent (Agent): Agent to add
        """
        pos = agent.position
        if pos not in self._agents_by_position:
            self._agents_by_position[pos] = []
        self._agents_by_position[pos].append(agent)

    def _remove_from_position_index(
        self,
        agent: Agent,
        position: Optional[Position] = None
    ) -> None:
        """
        Remove agent from spatial index.

        Args:
            agent (Agent): Agent to remove
            position (Optional[Position]): Position to remove from
                                          (uses agent.position if None)
        """
        pos = position or agent.position
        if pos in self._agents_by_position:
            try:
                self._agents_by_position[pos].remove(agent)
                # Clean up empty lists
                if not self._agents_by_position[pos]:
                    del self._agents_by_position[pos]
            except ValueError:
                # Agent not in list (shouldn't happen, but safe to ignore)
                pass

    def _cleanup_dead_agents(self) -> int:
        """
        Remove dead agents from registry.

        Returns:
            int: Number of agents removed
        """
        dead_ids = [
            agent_id for agent_id, agent in self._agents.items()
            if agent.state == AgentState.DEAD
        ]

        for agent_id in dead_ids:
            self.unregister_agent(agent_id)

        return len(dead_ids)

    def __repr__(self) -> str:
        """
        String representation of AgentManager.

        Returns:
            str: Summary of manager state
        """
        return (
            f"AgentManager("
            f"total={self.count_agents()}, "
            f"living={self.count_living_agents()}, "
            f"dead={self.count_dead_agents()})"
        )

    def __len__(self) -> int:
        """
        Get agent count (supports len(manager)).

        Returns:
            int: Number of agents
        """
        return self.count_agents()
