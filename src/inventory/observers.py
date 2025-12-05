"""
Inventory Observers Module - Observer Pattern

This module provides observer interfaces for monitoring inventory changes.

Design Patterns:
    - Observer: Listeners receive notifications of inventory changes

SOLID Principles:
    - Interface Segregation: Focused observer interface
    - Open/Closed: Easy to add new observer types
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from enum import Enum
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from inventory.inventory import Inventory
    from inventory.resource_stack import ResourceStack


class InventoryEvent(Enum):
    """
    Enumeration of inventory events.

    Attributes:
        ITEM_ADDED: Resource stack added to inventory
        ITEM_REMOVED: Resource stack removed from inventory
        ITEM_CONSUMED: Resource consumed/used from inventory
        CAPACITY_CHANGED: Inventory capacity modified
        CLEARED: All items removed from inventory
    """
    ITEM_ADDED = "item_added"
    ITEM_REMOVED = "item_removed"
    ITEM_CONSUMED = "item_consumed"
    CAPACITY_CHANGED = "capacity_changed"
    CLEARED = "cleared"


class InventoryObserver(ABC):
    """
    Abstract observer for inventory changes.

    Observers implement this interface to receive notifications when
    inventory contents change.

    Examples:
        >>> class LoggingObserver(InventoryObserver):
        ...     def on_inventory_changed(self, inventory, event, stack):
        ...         print(f"Inventory changed: {event.value}")
        ...
        >>> observer = LoggingObserver()
        >>> inventory.attach_observer(observer)
    """

    @abstractmethod
    def on_inventory_changed(
        self,
        inventory: Inventory,
        event: InventoryEvent,
        stack: Optional[ResourceStack]
    ) -> None:
        """
        Called when inventory changes.

        Args:
            inventory: The inventory that changed
            event: Type of change that occurred
            stack: The resource stack involved (if applicable)
        """
        pass


class LoggingInventoryObserver(InventoryObserver):
    """
    Concrete observer that logs inventory changes.

    Useful for debugging and event tracking.
    """

    def __init__(self, logger=None):
        """
        Initialize logging observer.

        Args:
            logger: Optional logger instance (uses print if None)
        """
        self.logger = logger

    def on_inventory_changed(
        self,
        inventory: Inventory,
        event: InventoryEvent,
        stack: Optional[ResourceStack]
    ) -> None:
        """Log inventory change."""
        msg = f"[Inventory {inventory.owner_id}] {event.value}"
        if stack:
            msg += f": {stack}"

        if self.logger:
            self.logger.info(msg)
        else:
            print(msg)


class StatisticsInventoryObserver(InventoryObserver):
    """
    Concrete observer that tracks inventory statistics.

    Maintains counters for adds, removes, and other operations.
    """

    def __init__(self):
        """Initialize statistics observer."""
        self.add_count = 0
        self.remove_count = 0
        self.consume_count = 0
        self.clear_count = 0

    def on_inventory_changed(
        self,
        inventory: Inventory,
        event: InventoryEvent,
        stack: Optional[ResourceStack]
    ) -> None:
        """Update statistics based on event."""
        if event == InventoryEvent.ITEM_ADDED:
            self.add_count += 1
        elif event == InventoryEvent.ITEM_REMOVED:
            self.remove_count += 1
        elif event == InventoryEvent.ITEM_CONSUMED:
            self.consume_count += 1
        elif event == InventoryEvent.CLEARED:
            self.clear_count += 1

    def get_stats(self) -> dict:
        """
        Get current statistics.

        Returns:
            dict: Statistics dictionary
        """
        return {
            "adds": self.add_count,
            "removes": self.remove_count,
            "consumes": self.consume_count,
            "clears": self.clear_count
        }

    def reset(self) -> None:
        """Reset all statistics to zero."""
        self.add_count = 0
        self.remove_count = 0
        self.consume_count = 0
        self.clear_count = 0
