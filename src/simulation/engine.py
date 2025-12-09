"""
Simulation Engine Module

This module provides the main simulation engine that orchestrates
all simulation components.

Design Patterns:
    - Facade Pattern: Provides simple interface to complex subsystems
    - Observer Pattern: Notifies observers of simulation events
    - State Pattern: Manages simulation state transitions

SOLID Principles:
    - Single Responsibility: Orchestrates simulation lifecycle
    - Open/Closed: Extensible through observers and strategies
    - Dependency Inversion: Depends on abstract interfaces

Integration:
    - Uses agents/ for agent updates
    - Uses world/ for environment simulation
    - Uses economy/ for market updates
    - Uses simulation/scheduler.py for update ordering
    - Uses simulation/analytics.py for statistics
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Dict, List, Optional, Any, Set, Callable
import time

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from simulation.scheduler import SchedulingStrategy, RoundRobinScheduler
from simulation.analytics import AnalyticsCollector, StepStatistics

if TYPE_CHECKING:
    from agents.agent import Agent
    from world.world import World
    from economy.marketplace import Marketplace


class SimulationState(Enum):
    """Simulation lifecycle states."""
    UNINITIALIZED = auto()  # Not yet initialized
    INITIALIZED = auto()    # Ready to run
    RUNNING = auto()        # Currently executing
    PAUSED = auto()         # Temporarily stopped
    COMPLETED = auto()      # Finished normally
    ERROR = auto()          # Stopped due to error


class SimulationEventType(Enum):
    """Types of simulation events."""
    INITIALIZED = auto()
    STARTED = auto()
    STEP_COMPLETED = auto()
    PAUSED = auto()
    RESUMED = auto()
    COMPLETED = auto()
    ERROR = auto()
    AGENT_ADDED = auto()
    AGENT_REMOVED = auto()


@dataclass
class SimulationEvent:
    """
    An event in the simulation.

    Attributes:
        event_type: Type of event
        step_number: Step when event occurred
        timestamp: Wall clock time
        data: Event-specific data
    """
    event_type: SimulationEventType
    step_number: int
    timestamp: float
    data: Dict[str, Any] = field(default_factory=dict)


@dataclass
class StepResult:
    """
    Result of a single simulation step.

    Attributes:
        step_number: Step that completed
        duration_ms: Time taken in milliseconds
        agents_updated: Number of agents updated
        actions_taken: Total actions executed
        events: Events that occurred
        statistics: Step statistics
    """
    step_number: int
    duration_ms: float
    agents_updated: int
    actions_taken: int
    events: List[SimulationEvent] = field(default_factory=list)
    statistics: Optional[StepStatistics] = None


@dataclass
class SimulationConfig:
    """
    Configuration for simulation behavior.

    Attributes:
        max_steps: Maximum steps (None = unlimited)
        step_delay_ms: Delay between steps (0 = no delay)
        enable_analytics: Whether to collect analytics
        auto_save_interval: Steps between auto-saves (None = disabled)
        stop_on_extinction: Stop if all agents die
        random_seed: Seed for reproducibility
    """
    max_steps: Optional[int] = None
    step_delay_ms: float = 0.0
    enable_analytics: bool = True
    auto_save_interval: Optional[int] = None
    stop_on_extinction: bool = True
    random_seed: Optional[int] = None


class SimulationObserver(ABC):
    """
    Abstract observer for simulation events.

    Implementations receive simulation events for logging,
    visualization, or custom processing.

    Design Pattern: Observer

    Examples:
        >>> class ProgressLogger(SimulationObserver):
        ...     def on_event(self, event):
        ...         print(f"Step {event.step_number}: {event.event_type}")
    """

    @abstractmethod
    def on_event(self, event: SimulationEvent) -> None:
        """
        Handle a simulation event.

        Args:
            event: The event that occurred
        """
        pass


class SimulationEngine:
    """
    Main simulation engine.

    Orchestrates agents, world, economy, and analytics.
    Provides high-level control over simulation lifecycle.

    Design Patterns:
        - Facade: Simple interface to complex systems
        - Observer: Event notification
        - State: Lifecycle management

    Attributes:
        state: Current simulation state
        config: Simulation configuration
        scheduler: Agent scheduling strategy
        analytics: Analytics collector
        current_step: Current step number

    Examples:
        >>> engine = SimulationEngine(world, agents, config)
        >>> engine.initialize()
        >>> result = engine.run(steps=100)
        >>> summary = engine.get_summary()
    """

    def __init__(
        self,
        world: Optional[World] = None,
        agents: Optional[List[Agent]] = None,
        config: Optional[SimulationConfig] = None,
        scheduler: Optional[SchedulingStrategy] = None,
        marketplace: Optional[Marketplace] = None
    ) -> None:
        """
        Initialize SimulationEngine.

        Args:
            world: World instance
            agents: Initial agent list
            config: Simulation configuration
            scheduler: Agent scheduling strategy
            marketplace: Optional marketplace
        """
        self._world = world
        self._agents: List[Agent] = list(agents) if agents else []
        self._config = config or SimulationConfig()
        self._scheduler = scheduler or RoundRobinScheduler()
        self._marketplace = marketplace

        self._state = SimulationState.UNINITIALIZED
        self._current_step = 0
        self._start_time: Optional[float] = None
        self._end_time: Optional[float] = None

        # Analytics
        self._analytics: Optional[AnalyticsCollector] = None
        if self._config.enable_analytics:
            self._analytics = AnalyticsCollector()

        # Observers
        self._observers: List[SimulationObserver] = []

        # Event history
        self._events: List[SimulationEvent] = []

        # Stop conditions
        self._stop_requested = False

    @property
    def state(self) -> SimulationState:
        """Current simulation state."""
        return self._state

    @property
    def current_step(self) -> int:
        """Current step number."""
        return self._current_step

    @property
    def agents(self) -> List[Agent]:
        """List of active agents."""
        return self._agents.copy()

    @property
    def world(self) -> Optional[World]:
        """World instance."""
        return self._world

    @property
    def analytics(self) -> Optional[AnalyticsCollector]:
        """Analytics collector."""
        return self._analytics

    def initialize(self) -> bool:
        """
        Initialize the simulation.

        Prepares all components for running.

        Returns:
            bool: True if initialization successful

        Raises:
            RuntimeError: If already initialized
        """
        if self._state != SimulationState.UNINITIALIZED:
            raise RuntimeError("Simulation already initialized")

        # Validate world
        if self._world is None:
            self._emit_event(SimulationEventType.ERROR, {"error": "No world"})
            self._state = SimulationState.ERROR
            return False

        # Initialize analytics
        if self._analytics is not None:
            self._analytics.clear()

        # Set state
        self._state = SimulationState.INITIALIZED
        self._current_step = 0
        self._stop_requested = False

        self._emit_event(SimulationEventType.INITIALIZED, {
            "agent_count": len(self._agents),
            "config": str(self._config)
        })

        return True

    def step(self) -> StepResult:
        """
        Execute a single simulation step.

        Process:
        1. Update scheduler
        2. Each agent: sense -> decide -> act
        3. Update world
        4. Update economy (if present)
        5. Collect analytics
        6. Check stop conditions

        Returns:
            StepResult: Result of this step

        Raises:
            RuntimeError: If not in valid state

        Note:
            Implementation would execute full agent lifecycle.
        """
        if self._state not in (SimulationState.INITIALIZED, SimulationState.RUNNING):
            raise RuntimeError(f"Cannot step in state: {self._state}")

        if self._state == SimulationState.INITIALIZED:
            self._state = SimulationState.RUNNING
            self._start_time = time.time()
            self._emit_event(SimulationEventType.STARTED, {})

        step_start = time.time()
        self._current_step += 1

        # Notify scheduler
        self._scheduler.on_step_start(self._current_step)

        # Track step events
        step_events: Dict[str, Any] = {
            "births": 0,
            "deaths": 0,
            "trades": 0,
            "combats": 0,
        }

        agents_updated = 0
        actions_taken = 0

        # Implementation would:
        # for agent in self._scheduler.get_update_order(self._agents, self._world):
        #     # Sense
        #     sensor_data = agent.sense(self._world)
        #
        #     # Decide
        #     action = agent.decide(sensor_data)
        #
        #     # Act
        #     if action is not None:
        #         agent.act(action, self._world)
        #         actions_taken += 1
        #
        #     agents_updated += 1
        #
        # # Update world
        # self._world.update()
        #
        # # Update marketplace
        # if self._marketplace is not None:
        #     self._marketplace.cleanup_expired_offers()
        #
        # # Remove dead agents
        # dead_agents = [a for a in self._agents if a.health <= 0]
        # for agent in dead_agents:
        #     self._agents.remove(agent)
        #     step_events["deaths"] += 1
        #     if self._analytics:
        #         self._analytics.record_agent_death(agent.agent_id, self._current_step)

        # Notify scheduler
        self._scheduler.on_step_end(self._current_step)

        # Record analytics
        statistics = None
        if self._analytics is not None:
            statistics = self._analytics.record_step(
                self._current_step,
                self._agents,
                self._world,
                step_events
            )

        # Calculate duration
        step_duration = (time.time() - step_start) * 1000

        # Create result
        result = StepResult(
            step_number=self._current_step,
            duration_ms=step_duration,
            agents_updated=agents_updated,
            actions_taken=actions_taken,
            statistics=statistics
        )

        # Emit step completed event
        self._emit_event(SimulationEventType.STEP_COMPLETED, {
            "step": self._current_step,
            "duration_ms": step_duration,
            "agents": len(self._agents)
        })

        # Check stop conditions
        self._check_stop_conditions()

        return result

    def run(self, steps: Optional[int] = None) -> Dict[str, Any]:
        """
        Run simulation for specified steps.

        Args:
            steps: Steps to run (None = until max_steps or stop)

        Returns:
            Dict: Summary of simulation run

        Note:
            Use stop() to interrupt a running simulation.
        """
        if self._state == SimulationState.UNINITIALIZED:
            if not self.initialize():
                return {"error": "Initialization failed"}

        if self._state not in (SimulationState.INITIALIZED, SimulationState.PAUSED):
            return {"error": f"Cannot run in state: {self._state}"}

        if self._state == SimulationState.PAUSED:
            self._state = SimulationState.RUNNING
            self._emit_event(SimulationEventType.RESUMED, {})

        # Determine step count
        max_steps = steps
        if max_steps is None and self._config.max_steps is not None:
            max_steps = self._config.max_steps - self._current_step

        steps_run = 0
        results: List[StepResult] = []

        while not self._stop_requested:
            # Check max steps
            if max_steps is not None and steps_run >= max_steps:
                break

            # Execute step
            result = self.step()
            results.append(result)
            steps_run += 1

            # Apply step delay
            if self._config.step_delay_ms > 0:
                time.sleep(self._config.step_delay_ms / 1000)

            # Check if simulation completed
            if self._state == SimulationState.COMPLETED:
                break

        return {
            "steps_run": steps_run,
            "final_step": self._current_step,
            "state": self._state.name,
            "summary": self.get_summary() if self._analytics else None
        }

    def pause(self) -> bool:
        """
        Pause the simulation.

        Returns:
            bool: True if paused successfully
        """
        if self._state != SimulationState.RUNNING:
            return False

        self._state = SimulationState.PAUSED
        self._emit_event(SimulationEventType.PAUSED, {"step": self._current_step})
        return True

    def resume(self) -> bool:
        """
        Resume paused simulation.

        Returns:
            bool: True if resumed successfully
        """
        if self._state != SimulationState.PAUSED:
            return False

        self._state = SimulationState.RUNNING
        self._emit_event(SimulationEventType.RESUMED, {"step": self._current_step})
        return True

    def stop(self) -> None:
        """Request simulation stop after current step."""
        self._stop_requested = True

    def reset(self) -> None:
        """
        Reset simulation to initial state.

        Clears all progress and returns to UNINITIALIZED.
        """
        self._state = SimulationState.UNINITIALIZED
        self._current_step = 0
        self._start_time = None
        self._end_time = None
        self._stop_requested = False
        self._events.clear()

        if self._analytics is not None:
            self._analytics.clear()

    def add_agent(self, agent: Agent) -> None:
        """
        Add agent to simulation.

        Args:
            agent: Agent to add
        """
        if agent not in self._agents:
            self._agents.append(agent)
            self._emit_event(SimulationEventType.AGENT_ADDED, {
                "agent_id": agent.agent_id,
                "name": agent.name
            })

    def remove_agent(self, agent: Agent) -> bool:
        """
        Remove agent from simulation.

        Args:
            agent: Agent to remove

        Returns:
            bool: True if removed
        """
        if agent in self._agents:
            self._agents.remove(agent)
            self._emit_event(SimulationEventType.AGENT_REMOVED, {
                "agent_id": agent.agent_id,
                "name": agent.name
            })
            return True
        return False

    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """
        Get agent by ID.

        Args:
            agent_id: Agent ID to find

        Returns:
            Optional[Agent]: Agent or None
        """
        for agent in self._agents:
            if agent.agent_id == agent_id:
                return agent
        return None

    def set_world(self, world: World) -> None:
        """
        Set world instance.

        Args:
            world: World to use

        Raises:
            RuntimeError: If simulation is running
        """
        if self._state == SimulationState.RUNNING:
            raise RuntimeError("Cannot change world while running")
        self._world = world

    def set_scheduler(self, scheduler: SchedulingStrategy) -> None:
        """
        Set scheduling strategy.

        Args:
            scheduler: New scheduler
        """
        self._scheduler = scheduler

    def set_marketplace(self, marketplace: Marketplace) -> None:
        """
        Set marketplace instance.

        Args:
            marketplace: Marketplace to use
        """
        self._marketplace = marketplace

    def add_observer(self, observer: SimulationObserver) -> None:
        """Add simulation observer."""
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: SimulationObserver) -> None:
        """Remove simulation observer."""
        if observer in self._observers:
            self._observers.remove(observer)

    def get_summary(self) -> Dict[str, Any]:
        """
        Get simulation summary.

        Returns:
            Dict: Summary statistics
        """
        elapsed = 0.0
        if self._start_time is not None:
            end = self._end_time or time.time()
            elapsed = end - self._start_time

        summary = {
            "state": self._state.name,
            "current_step": self._current_step,
            "elapsed_seconds": elapsed,
            "agent_count": len(self._agents),
            "events_recorded": len(self._events),
        }

        if self._analytics is not None:
            summary["analytics"] = self._analytics.get_summary()

        return summary

    def get_events(
        self,
        event_type: Optional[SimulationEventType] = None,
        limit: Optional[int] = None
    ) -> List[SimulationEvent]:
        """
        Get simulation events.

        Args:
            event_type: Filter by type (None = all)
            limit: Max events to return

        Returns:
            List[SimulationEvent]: Matching events
        """
        events = self._events

        if event_type is not None:
            events = [e for e in events if e.event_type == event_type]

        if limit is not None:
            events = events[-limit:]

        return events

    def _check_stop_conditions(self) -> None:
        """Check if simulation should stop."""
        # Check extinction
        if self._config.stop_on_extinction and len(self._agents) == 0:
            self._complete_simulation("extinction")
            return

        # Check max steps
        if (self._config.max_steps is not None and
            self._current_step >= self._config.max_steps):
            self._complete_simulation("max_steps")
            return

    def _complete_simulation(self, reason: str) -> None:
        """Mark simulation as completed."""
        self._state = SimulationState.COMPLETED
        self._end_time = time.time()

        self._emit_event(SimulationEventType.COMPLETED, {
            "reason": reason,
            "final_step": self._current_step,
            "final_agent_count": len(self._agents)
        })

        # Notify analytics observers
        if self._analytics is not None:
            summary = self._analytics.get_summary()
            for observer in self._analytics._observers:
                try:
                    observer.on_simulation_complete(summary)
                except Exception:
                    pass

    def _emit_event(
        self,
        event_type: SimulationEventType,
        data: Dict[str, Any]
    ) -> None:
        """Emit simulation event."""
        event = SimulationEvent(
            event_type=event_type,
            step_number=self._current_step,
            timestamp=time.time(),
            data=data
        )

        self._events.append(event)

        # Notify observers
        for observer in self._observers:
            try:
                observer.on_event(event)
            except Exception:
                pass

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"SimulationEngine("
            f"state={self._state.name}, "
            f"step={self._current_step}, "
            f"agents={len(self._agents)})"
        )
