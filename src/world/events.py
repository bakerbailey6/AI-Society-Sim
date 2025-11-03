"""
Events Module - World Event Hierarchy

This module provides an event system for tracking and communicating
changes in the world state. Events are immutable records of what happened.

Design Patterns:
    - Immutable Pattern: Events cannot be modified after creation

SOLID Principles:
    - Single Responsibility: Each event type represents one kind of occurrence
    - Open/Closed: New event types can be added without modifying existing ones
    - Liskov Substitution: All event subclasses can be used wherever WorldEvent is expected
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Dict, Optional
from abc import ABC, abstractmethod
from datetime import datetime


@dataclass(frozen=True)
class WorldEvent(ABC):
    """
    Abstract base class for all world events.

    Events are immutable records of things that happened in the simulation.
    They can be logged, analyzed, or used to notify other systems of changes.

    Attributes:
        timestamp (int): The simulation time step when the event occurred
        event_type (str): String identifier for the event type
        description (str): Human-readable description of the event

    Note:
        All subclasses must be immutable (frozen=True) to ensure event
        history cannot be altered after the fact.
    """

    timestamp: int
    event_type: str
    description: str

    @abstractmethod
    def get_details(self) -> Dict[str, Any]:
        """
        Get detailed information about the event.

        Returns:
            Dict[str, Any]: Dictionary containing event-specific details

        Note:
            Subclasses must implement this to provide additional context
            beyond the basic event information.
        """
        pass

    def __str__(self) -> str:
        """Human-readable string representation of the event."""
        return f"[T={self.timestamp}] {self.event_type}: {self.description}"


@dataclass(frozen=True)
class ResourceDepletedEvent(WorldEvent):
    """
    Event triggered when a resource is completely depleted.

    Attributes:
        resource_id (str): Unique identifier of the depleted resource
        resource_type (str): Type of resource (e.g., "food", "material")
        position (tuple): Grid position where depletion occurred
        final_value (float): Final value before complete depletion
    """

    resource_id: str
    resource_type: str
    position: tuple
    final_value: float

    def get_details(self) -> Dict[str, Any]:
        """Get detailed information about resource depletion."""
        return {
            "resource_id": self.resource_id,
            "resource_type": self.resource_type,
            "position": self.position,
            "final_value": self.final_value,
            "timestamp": self.timestamp
        }


@dataclass(frozen=True)
class ResourceRegeneratedEvent(WorldEvent):
    """
    Event triggered when a resource regenerates.

    Attributes:
        resource_id (str): Unique identifier of the regenerated resource
        resource_type (str): Type of resource
        position (tuple): Grid position where regeneration occurred
        amount_regenerated (float): Amount of resource regenerated
        new_value (float): Total value after regeneration
    """

    resource_id: str
    resource_type: str
    position: tuple
    amount_regenerated: float
    new_value: float

    def get_details(self) -> Dict[str, Any]:
        """Get detailed information about resource regeneration."""
        return {
            "resource_id": self.resource_id,
            "resource_type": self.resource_type,
            "position": self.position,
            "amount_regenerated": self.amount_regenerated,
            "new_value": self.new_value,
            "timestamp": self.timestamp
        }


@dataclass(frozen=True)
class TimeStepEvent(WorldEvent):
    """
    Event triggered at the start of each simulation time step.

    Attributes:
        step_number (int): The current time step number
        total_agents (int): Number of active agents
        total_resources (int): Number of active resources
    """

    step_number: int
    total_agents: int
    total_resources: int

    def get_details(self) -> Dict[str, Any]:
        """Get detailed information about the time step."""
        return {
            "step_number": self.step_number,
            "total_agents": self.total_agents,
            "total_resources": self.total_resources,
            "timestamp": self.timestamp
        }


@dataclass(frozen=True)
class CellAccessedEvent(WorldEvent):
    """
    Event triggered when a cell is accessed (useful for proxy pattern).

    This event is particularly useful for tracking lazy-loading behavior
    when using the Proxy pattern for cells.

    Attributes:
        position (tuple): Position of the accessed cell
        was_loaded (bool): Whether the cell needed to be loaded from storage
        access_count (int): Number of times this cell has been accessed
    """

    position: tuple
    was_loaded: bool
    access_count: int

    def get_details(self) -> Dict[str, Any]:
        """Get detailed information about cell access."""
        return {
            "position": self.position,
            "was_loaded": self.was_loaded,
            "access_count": self.access_count,
            "timestamp": self.timestamp
        }


@dataclass(frozen=True)
class WorldStateChangedEvent(WorldEvent):
    """
    Generic event for world state changes.

    This flexible event type can represent various world changes that
    don't fit into more specific event categories.

    Attributes:
        change_type (str): Type of change that occurred
        affected_positions (tuple): Positions affected by the change
        metadata (Dict[str, Any]): Additional change-specific information
    """

    change_type: str
    affected_positions: tuple
    metadata: Dict[str, Any]

    def get_details(self) -> Dict[str, Any]:
        """Get detailed information about the world state change."""
        return {
            "change_type": self.change_type,
            "affected_positions": self.affected_positions,
            "metadata": self.metadata,
            "timestamp": self.timestamp
        }


class EventLogger:
    """
    Simple logger for recording world events.

    This class demonstrates the Single Responsibility Principle by
    focusing solely on event logging and retrieval.

    Note:
        This is a concrete utility class, not an abstract pattern demonstration,
        but it shows how events can be used in practice.
    """

    def __init__(self) -> None:
        """Initialize the event logger with an empty event history."""
        self._events: list[WorldEvent] = []

    def log_event(self, event: WorldEvent) -> None:
        """
        Record an event to the log.

        Args:
            event (WorldEvent): The event to log

        Note:
            Events are immutable, so they can be safely stored and shared.
        """
        self._events.append(event)

    def get_events(
        self,
        event_type: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> list[WorldEvent]:
        """
        Retrieve events matching given criteria.

        Args:
            event_type (Optional[str]): Filter by event type
            start_time (Optional[int]): Minimum timestamp (inclusive)
            end_time (Optional[int]): Maximum timestamp (inclusive)

        Returns:
            list[WorldEvent]: List of matching events
        """
        filtered = self._events

        if event_type:
            filtered = [e for e in filtered if e.event_type == event_type]

        if start_time is not None:
            filtered = [e for e in filtered if e.timestamp >= start_time]

        if end_time is not None:
            filtered = [e for e in filtered if e.timestamp <= end_time]

        return filtered

    def clear_events(self) -> None:
        """Clear all logged events."""
        self._events.clear()

    def get_event_count(self) -> int:
        """
        Get total number of logged events.

        Returns:
            int: Total event count
        """
        return len(self._events)
