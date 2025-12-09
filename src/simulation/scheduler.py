"""
Scheduler Module

This module provides scheduling strategies for agent updates.
Different strategies determine the order agents are updated
each simulation step.

Design Patterns:
    - Strategy Pattern: Interchangeable scheduling algorithms
    - Iterator Pattern: Yields agents in scheduled order

SOLID Principles:
    - Single Responsibility: Each scheduler handles one approach
    - Open/Closed: New schedulers can be added without modification
    - Liskov Substitution: All schedulers are interchangeable

Integration:
    - Uses agents/agent.py for Agent type
    - Uses world/world.py for World context
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, List, Optional, Iterator, Callable
import random

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if TYPE_CHECKING:
    from agents.agent import Agent
    from world.world import World


class PriorityLevel(Enum):
    """Priority levels for agent scheduling."""
    CRITICAL = 0    # Highest priority (e.g., dying agents)
    HIGH = 1        # High priority (e.g., in combat)
    NORMAL = 2      # Normal priority
    LOW = 3         # Low priority (e.g., idle agents)
    BACKGROUND = 4  # Lowest priority


@dataclass
class ScheduledAgent:
    """
    Agent with scheduling metadata.

    Attributes:
        agent: The agent to schedule
        priority: Priority level
        last_updated: Last update timestamp
        update_count: Number of times updated
    """
    agent: Agent
    priority: PriorityLevel = PriorityLevel.NORMAL
    last_updated: float = 0.0
    update_count: int = 0


class SchedulingStrategy(ABC):
    """
    Abstract base for scheduling strategies.

    Defines interface for determining agent update order.
    Different strategies optimize for fairness, priority,
    or other goals.

    Design Pattern: Strategy

    Subclasses:
        - SequentialScheduler: Fixed order
        - RandomScheduler: Random order each step
        - PriorityScheduler: By priority level
        - RoundRobinScheduler: Fair rotation

    Examples:
        >>> scheduler = PriorityScheduler()
        >>> for agent in scheduler.get_update_order(agents, world):
        ...     agent.update(world)
    """

    @abstractmethod
    def get_update_order(
        self,
        agents: List[Agent],
        world: World
    ) -> Iterator[Agent]:
        """
        Get agents in update order.

        Args:
            agents: List of agents to schedule
            world: World context for scheduling decisions

        Yields:
            Agent: Agents in scheduled order
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """
        Get scheduler name.

        Returns:
            str: Scheduler identifier
        """
        pass

    def on_step_start(self, step_number: int) -> None:
        """
        Called at start of each simulation step.

        Override to reset per-step state.

        Args:
            step_number: Current step number
        """
        pass

    def on_step_end(self, step_number: int) -> None:
        """
        Called at end of each simulation step.

        Override to finalize per-step state.

        Args:
            step_number: Current step number
        """
        pass


class SequentialScheduler(SchedulingStrategy):
    """
    Sequential scheduling by agent order.

    Processes agents in the order they appear in the list.
    Simple and deterministic.

    Attributes:
        reverse: If True, process in reverse order

    Examples:
        >>> scheduler = SequentialScheduler()
        >>> # Agents processed in list order
    """

    def __init__(self, reverse: bool = False) -> None:
        """
        Initialize SequentialScheduler.

        Args:
            reverse: Process in reverse order
        """
        self._reverse = reverse

    def get_update_order(
        self,
        agents: List[Agent],
        world: World
    ) -> Iterator[Agent]:
        """
        Yield agents in sequential order.

        Args:
            agents: Agents to schedule
            world: World context (unused)

        Yields:
            Agent: Agents in list order
        """
        if self._reverse:
            yield from reversed(agents)
        else:
            yield from agents

    def get_name(self) -> str:
        """Return scheduler name."""
        return f"SequentialScheduler(reverse={self._reverse})"


class RandomScheduler(SchedulingStrategy):
    """
    Random scheduling each step.

    Shuffles agents randomly each simulation step.
    Provides fairness through randomization.

    Attributes:
        seed: Optional random seed for reproducibility

    Examples:
        >>> scheduler = RandomScheduler(seed=42)
        >>> # Agents processed in random order each step
    """

    def __init__(self, seed: Optional[int] = None) -> None:
        """
        Initialize RandomScheduler.

        Args:
            seed: Random seed for reproducibility
        """
        self._seed = seed
        self._rng = random.Random(seed)

    def get_update_order(
        self,
        agents: List[Agent],
        world: World
    ) -> Iterator[Agent]:
        """
        Yield agents in random order.

        Args:
            agents: Agents to schedule
            world: World context (unused)

        Yields:
            Agent: Agents in random order
        """
        shuffled = list(agents)
        self._rng.shuffle(shuffled)
        yield from shuffled

    def on_step_start(self, step_number: int) -> None:
        """Optionally reseed at step start for reproducibility."""
        if self._seed is not None:
            # Use step number for deterministic randomness per step
            self._rng = random.Random(self._seed + step_number)

    def get_name(self) -> str:
        """Return scheduler name."""
        return f"RandomScheduler(seed={self._seed})"


class PriorityScheduler(SchedulingStrategy):
    """
    Priority-based scheduling.

    Updates agents by priority level, with higher priority
    agents updated first. Priority can be static or dynamic.

    Attributes:
        priority_function: Function to determine agent priority
        shuffle_within_priority: Randomize within same priority

    Priority Determination:
        - CRITICAL: Health < 10%
        - HIGH: In combat or health < 30%
        - NORMAL: Default
        - LOW: Energy > 80% and no nearby threats
        - BACKGROUND: Idle or far from action

    Examples:
        >>> scheduler = PriorityScheduler()
        >>> # Dying agents updated before healthy ones
    """

    def __init__(
        self,
        priority_function: Optional[Callable[[Agent, World], PriorityLevel]] = None,
        shuffle_within_priority: bool = True
    ) -> None:
        """
        Initialize PriorityScheduler.

        Args:
            priority_function: Custom priority calculator
            shuffle_within_priority: Randomize within priority
        """
        self._priority_function = priority_function or self._default_priority
        self._shuffle = shuffle_within_priority
        self._rng = random.Random()

    def get_update_order(
        self,
        agents: List[Agent],
        world: World
    ) -> Iterator[Agent]:
        """
        Yield agents by priority.

        Args:
            agents: Agents to schedule
            world: World context for priority calculation

        Yields:
            Agent: Agents in priority order
        """
        # Calculate priorities
        prioritized = [
            (agent, self._priority_function(agent, world))
            for agent in agents
        ]

        # Sort by priority (lower enum value = higher priority)
        prioritized.sort(key=lambda x: x[1].value)

        # Group by priority level
        current_priority = None
        current_group: List[Agent] = []

        for agent, priority in prioritized:
            if priority != current_priority:
                # Yield previous group
                if current_group:
                    if self._shuffle:
                        self._rng.shuffle(current_group)
                    yield from current_group

                current_priority = priority
                current_group = [agent]
            else:
                current_group.append(agent)

        # Yield final group
        if current_group:
            if self._shuffle:
                self._rng.shuffle(current_group)
            yield from current_group

    def _default_priority(self, agent: Agent, world: World) -> PriorityLevel:
        """
        Default priority calculation.

        Args:
            agent: Agent to prioritize
            world: World context

        Returns:
            PriorityLevel: Calculated priority
        """
        health_percent = (agent.health / agent.max_health * 100) if agent.max_health > 0 else 0

        if health_percent < 10:
            return PriorityLevel.CRITICAL
        elif health_percent < 30:
            return PriorityLevel.HIGH
        elif health_percent > 80:
            energy_percent = (agent.energy / agent.max_energy * 100) if agent.max_energy > 0 else 0
            if energy_percent > 80:
                return PriorityLevel.LOW
        return PriorityLevel.NORMAL

    def get_name(self) -> str:
        """Return scheduler name."""
        return "PriorityScheduler"


class RoundRobinScheduler(SchedulingStrategy):
    """
    Round-robin fair scheduling.

    Ensures all agents get equal update opportunities over time.
    Tracks update counts and prioritizes least-updated agents.

    Attributes:
        updates_per_step: Max updates per agent per step
        track_updates: Whether to track update history

    Examples:
        >>> scheduler = RoundRobinScheduler()
        >>> # Agents updated in fair rotation
    """

    def __init__(
        self,
        updates_per_step: int = 1,
        track_updates: bool = True
    ) -> None:
        """
        Initialize RoundRobinScheduler.

        Args:
            updates_per_step: Updates allowed per agent per step
            track_updates: Track agent update counts
        """
        self._updates_per_step = updates_per_step
        self._track_updates = track_updates
        self._update_counts: dict = {}
        self._current_index = 0

    def get_update_order(
        self,
        agents: List[Agent],
        world: World
    ) -> Iterator[Agent]:
        """
        Yield agents in round-robin order.

        Starts from where previous step left off.

        Args:
            agents: Agents to schedule
            world: World context (unused)

        Yields:
            Agent: Agents in rotation order
        """
        if not agents:
            return

        n = len(agents)

        # Start from last position
        for i in range(n):
            idx = (self._current_index + i) % n
            agent = agents[idx]

            # Track update count
            if self._track_updates:
                agent_id = getattr(agent, 'agent_id', id(agent))
                self._update_counts[agent_id] = self._update_counts.get(agent_id, 0) + 1

            yield agent

        # Update position for next step
        self._current_index = (self._current_index + n) % n if n > 0 else 0

    def get_update_count(self, agent: Agent) -> int:
        """
        Get number of updates for an agent.

        Args:
            agent: Agent to check

        Returns:
            int: Update count
        """
        agent_id = getattr(agent, 'agent_id', id(agent))
        return self._update_counts.get(agent_id, 0)

    def reset_counts(self) -> None:
        """Reset all update counts."""
        self._update_counts.clear()
        self._current_index = 0

    def get_name(self) -> str:
        """Return scheduler name."""
        return "RoundRobinScheduler"


class AdaptiveScheduler(SchedulingStrategy):
    """
    Adaptive scheduling based on simulation state.

    Dynamically switches between scheduling strategies
    based on current simulation conditions.

    Conditions:
        - High conflict -> Priority scheduling
        - Stable -> Round robin
        - Many agents -> Random sampling

    Attributes:
        strategies: Available strategies to switch between
        current_strategy: Currently active strategy

    Examples:
        >>> scheduler = AdaptiveScheduler()
        >>> # Automatically adapts scheduling approach
    """

    # Thresholds for adaptation
    HIGH_CONFLICT_THRESHOLD: float = 0.3  # 30% of agents in conflict
    MANY_AGENTS_THRESHOLD: int = 100

    def __init__(self) -> None:
        """Initialize AdaptiveScheduler with strategy pool."""
        self._strategies = {
            "sequential": SequentialScheduler(),
            "random": RandomScheduler(),
            "priority": PriorityScheduler(),
            "round_robin": RoundRobinScheduler(),
        }
        self._current_strategy_name = "round_robin"

    @property
    def current_strategy(self) -> SchedulingStrategy:
        """Get current active strategy."""
        return self._strategies[self._current_strategy_name]

    def get_update_order(
        self,
        agents: List[Agent],
        world: World
    ) -> Iterator[Agent]:
        """
        Yield agents using adaptive strategy.

        Selects strategy based on current conditions.

        Args:
            agents: Agents to schedule
            world: World context for adaptation

        Yields:
            Agent: Agents in adapted order
        """
        # Adapt strategy based on conditions
        self._adapt_strategy(agents, world)

        # Use selected strategy
        yield from self.current_strategy.get_update_order(agents, world)

    def _adapt_strategy(self, agents: List[Agent], world: World) -> None:
        """
        Select appropriate strategy.

        Args:
            agents: Current agents
            world: World context
        """
        n_agents = len(agents)

        if n_agents == 0:
            return

        # Count agents in conflict (low health)
        conflict_count = sum(
            1 for a in agents
            if a.max_health > 0 and a.health / a.max_health < 0.5
        )

        conflict_ratio = conflict_count / n_agents

        # Select strategy
        if conflict_ratio > self.HIGH_CONFLICT_THRESHOLD:
            self._current_strategy_name = "priority"
        elif n_agents > self.MANY_AGENTS_THRESHOLD:
            self._current_strategy_name = "random"
        else:
            self._current_strategy_name = "round_robin"

    def on_step_start(self, step_number: int) -> None:
        """Forward to current strategy."""
        self.current_strategy.on_step_start(step_number)

    def on_step_end(self, step_number: int) -> None:
        """Forward to current strategy."""
        self.current_strategy.on_step_end(step_number)

    def get_name(self) -> str:
        """Return scheduler name."""
        return f"AdaptiveScheduler(current={self._current_strategy_name})"
