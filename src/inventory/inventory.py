"""
Inventory Module - Core Inventory Container

This module provides the core inventory system for storing and managing resources.

Design Patterns:
    - Composite: Inventory contains stacks (and could contain sub-inventories)
    - Observer: Notifies listeners of changes
    - Iterator: Supports iteration over stacks

SOLID Principles:
    - Single Responsibility: Manages only resource storage
    - Open/Closed: Extensible via observers and strategies
    - Liskov Substitution: Can be used anywhere storage is needed
    - Interface Segregation: Focused inventory interface
    - Dependency Inversion: Depends on abstract CapacityStrategy
"""

from __future__ import annotations
from typing import List, Optional, Dict
from resources.resource import ResourceType

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from inventory.resource_stack import ResourceStack
from inventory.capacity_strategy import CapacityStrategy
from inventory.observers import InventoryObserver, InventoryEvent
from inventory.exceptions import InsufficientResourcesException, CapacityExceededException
from world.markers import IObservable


class Inventory(IObservable):
    """
    Core inventory system for storing resources.

    Implements Composite and Observer patterns to provide a flexible,
    extensible resource storage system.

    The inventory:
    - Stores resources as immutable ResourceStack objects
    - Enforces capacity limits via CapacityStrategy
    - Notifies observers of changes
    - Automatically merges compatible stacks
    - Supports iteration and querying

    Attributes:
        owner_id: Unique ID of the owner (agent ID or stockpile ID)
        name: Human-readable inventory name
        capacity_strategy: Strategy for enforcing capacity limits
        stacks: List of resource stacks (internal)
        observers: List of change observers (internal)

    Examples:
        >>> from inventory import Inventory, SlotBasedCapacity, ResourceStack
        >>> capacity = SlotBasedCapacity(max_slots=20)
        >>> inventory = Inventory("agent_123", capacity, "Alice's Backpack")
        >>>
        >>> stack = ResourceStack(ResourceType.FOOD, 50.0, metadata)
        >>> inventory.add(stack)
        True
        >>> inventory.get_quantity(ResourceType.FOOD)
        50.0
    """

    def __init__(
        self,
        owner_id: str,
        capacity_strategy: CapacityStrategy,
        name: str = "Inventory"
    ):
        """
        Initialize an inventory.

        Args:
            owner_id: Unique identifier of the owner
            capacity_strategy: Strategy for capacity limits
            name: Human-readable name for this inventory
        """
        self._owner_id = owner_id
        self._name = name
        self._stacks: List[ResourceStack] = []
        self._capacity_strategy = capacity_strategy
        self._observers: List[InventoryObserver] = []

    # --- Properties ---

    @property
    def owner_id(self) -> str:
        """Get the owner's unique identifier."""
        return self._owner_id

    @property
    def name(self) -> str:
        """Get the inventory name."""
        return self._name

    @property
    def capacity_strategy(self) -> CapacityStrategy:
        """Get the capacity strategy."""
        return self._capacity_strategy

    @property
    def total_weight(self) -> float:
        """
        Calculate total weight of all items.

        Returns:
            float: Total weight in kilograms
        """
        return sum(stack.total_weight for stack in self._stacks)

    @property
    def total_volume(self) -> float:
        """
        Calculate total volume of all items.

        Returns:
            float: Total volume in cubic meters
        """
        return sum(stack.total_volume for stack in self._stacks)

    @property
    def is_empty(self) -> bool:
        """
        Check if inventory is empty.

        Returns:
            bool: True if no stacks present
        """
        return len(self._stacks) == 0

    @property
    def is_full(self) -> bool:
        """
        Check if inventory is at capacity.

        Returns:
            bool: True if no remaining capacity
        """
        return self._capacity_strategy.get_remaining_capacity(self) <= 0

    @property
    def stack_count(self) -> int:
        """
        Get number of stacks in inventory.

        Returns:
            int: Number of stacks
        """
        return len(self._stacks)

    # --- Query Methods ---

    def get_quantity(self, resource_type: ResourceType) -> float:
        """
        Get total quantity of a specific resource type.

        Args:
            resource_type: Type of resource to count

        Returns:
            float: Total quantity across all stacks of that type
        """
        total = 0.0
        for stack in self._stacks:
            if stack.resource_type == resource_type:
                total += stack.quantity
        return total

    def has_resource(self, resource_type: ResourceType, quantity: float = 1.0) -> bool:
        """
        Check if inventory contains at least the specified quantity.

        Args:
            resource_type: Type of resource
            quantity: Minimum quantity required (default 1.0)

        Returns:
            bool: True if inventory has >= quantity of resource
        """
        return self.get_quantity(resource_type) >= quantity

    def get_all_resource_types(self) -> List[ResourceType]:
        """
        Get list of all resource types in inventory.

        Returns:
            List[ResourceType]: Unique resource types present
        """
        return list(set(stack.resource_type for stack in self._stacks))

    def get_resource_summary(self) -> Dict[ResourceType, float]:
        """
        Get summary of all resources and quantities.

        Returns:
            Dict[ResourceType, float]: Mapping of types to total quantities
        """
        summary = {}
        for stack in self._stacks:
            if stack.resource_type in summary:
                summary[stack.resource_type] += stack.quantity
            else:
                summary[stack.resource_type] = stack.quantity
        return summary

    # --- Mutation Methods ---

    def add(self, stack: ResourceStack) -> bool:
        """
        Add a resource stack to inventory.

        Automatically merges with existing compatible stacks if possible.
        Notifies observers on successful addition.

        Args:
            stack: The resource stack to add

        Returns:
            bool: True if added successfully, False if capacity exceeded

        Examples:
            >>> stack = ResourceStack(ResourceType.FOOD, 25.0, metadata)
            >>> if inventory.add(stack):
            ...     print("Added successfully")
        """
        # Check capacity before adding
        if not self._capacity_strategy.can_add(self, stack):
            return False

        # Try to merge with existing stack of same type and metadata
        for i, existing in enumerate(self._stacks):
            if (existing.resource_type == stack.resource_type and
                existing.metadata == stack.metadata and
                existing.can_add(stack.quantity)):
                # Merge into existing stack
                merged = existing.merge(stack)
                self._stacks[i] = merged
                self._notify_observers(InventoryEvent.ITEM_ADDED, stack)
                return True

        # Add as new stack
        self._stacks.append(stack)
        self._notify_observers(InventoryEvent.ITEM_ADDED, stack)
        return True

    def remove(self, resource_type: ResourceType, quantity: float) -> Optional[ResourceStack]:
        """
        Remove specified quantity of a resource type.

        Removes from stacks until the requested quantity is collected.
        Notifies observers on successful removal.

        Args:
            resource_type: Type of resource to remove
            quantity: Amount to remove

        Returns:
            Optional[ResourceStack]: The removed resources as a stack, or None if insufficient

        Raises:
            InsufficientResourcesException: If not enough resources available

        Examples:
            >>> stack = inventory.remove(ResourceType.FOOD, 10.0)
            >>> if stack:
            ...     print(f"Removed {stack.quantity} food")
        """
        if not self.has_resource(resource_type, quantity):
            return None

        remaining = quantity
        removed_stacks = []

        # Remove from stacks until we have enough
        i = 0
        while i < len(self._stacks) and remaining > 0:
            stack = self._stacks[i]

            if stack.resource_type == resource_type:
                if stack.quantity <= remaining:
                    # Take entire stack
                    removed_stacks.append(stack)
                    self._stacks.pop(i)
                    remaining -= stack.quantity
                    continue  # Don't increment i, we removed this index
                else:
                    # Take partial stack
                    remaining_stack, taken_stack = stack.split(remaining)
                    self._stacks[i] = remaining_stack
                    removed_stacks.append(taken_stack)
                    remaining = 0

            i += 1

        # Combine all removed stacks into one
        if removed_stacks:
            total_removed = sum(s.quantity for s in removed_stacks)
            result = ResourceStack(
                resource_type=resource_type,
                quantity=total_removed,
                metadata=removed_stacks[0].metadata,
                max_stack_size=removed_stacks[0].max_stack_size,
                weight_per_unit=removed_stacks[0].weight_per_unit,
                volume_per_unit=removed_stacks[0].volume_per_unit
            )
            self._notify_observers(InventoryEvent.ITEM_REMOVED, result)
            return result

        return None

    def clear(self) -> None:
        """
        Remove all items from inventory.

        Notifies observers of clear event.
        """
        self._stacks.clear()
        self._notify_observers(InventoryEvent.CLEARED, None)

    def consolidate(self) -> None:
        """
        Consolidate stacks of the same type and metadata.

        Merges compatible stacks to reduce total stack count.
        Useful for defragmentation.
        """
        # Group stacks by (type, metadata)
        groups: Dict[tuple, List[int]] = {}

        for i, stack in enumerate(self._stacks):
            key = (stack.resource_type, stack.metadata,
                   stack.max_stack_size, stack.weight_per_unit, stack.volume_per_unit)
            if key not in groups:
                groups[key] = []
            groups[key].append(i)

        # Merge each group
        new_stacks = []
        for key, indices in groups.items():
            if len(indices) == 1:
                # Single stack, keep as is
                new_stacks.append(self._stacks[indices[0]])
            else:
                # Multiple stacks, merge them
                total_quantity = sum(self._stacks[i].quantity for i in indices)
                first_stack = self._stacks[indices[0]]

                merged = ResourceStack(
                    resource_type=first_stack.resource_type,
                    quantity=total_quantity,
                    metadata=first_stack.metadata,
                    max_stack_size=first_stack.max_stack_size,
                    weight_per_unit=first_stack.weight_per_unit,
                    volume_per_unit=first_stack.volume_per_unit
                )
                new_stacks.append(merged)

        self._stacks = new_stacks

    # --- Observer Pattern Methods ---

    def attach_observer(self, observer: InventoryObserver) -> None:
        """
        Attach an observer to receive change notifications.

        Args:
            observer: The observer to attach
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def detach_observer(self, observer: InventoryObserver) -> None:
        """
        Detach an observer.

        Args:
            observer: The observer to detach
        """
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify_observers(
        self,
        event: InventoryEvent,
        stack: Optional[ResourceStack]
    ) -> None:
        """
        Notify all observers of an inventory change.

        Args:
            event: Type of change
            stack: Stack involved in the change (if applicable)
        """
        for observer in self._observers:
            observer.on_inventory_changed(self, event, stack)

    # --- Iterator Support ---

    def __iter__(self):
        """
        Iterate over resource stacks.

        Returns:
            iterator: Iterator over stacks

        Examples:
            >>> for stack in inventory:
            ...     print(f"{stack.resource_type}: {stack.quantity}")
        """
        return iter(self._stacks)

    def __len__(self):
        """
        Get number of stacks.

        Returns:
            int: Number of stacks
        """
        return len(self._stacks)

    def __contains__(self, resource_type: ResourceType):
        """
        Check if inventory contains a resource type.

        Args:
            resource_type: Resource type to check

        Returns:
            bool: True if any stack of that type exists

        Examples:
            >>> if ResourceType.FOOD in inventory:
            ...     print("Has food")
        """
        return any(stack.resource_type == resource_type for stack in self._stacks)

    # --- String Representation ---

    def __repr__(self):
        """Developer-friendly representation."""
        capacity_pct = (1.0 - self._capacity_strategy.get_remaining_capacity(self)) * 100
        return (
            f"Inventory({self._name}, "
            f"{len(self._stacks)} stacks, "
            f"{self.total_weight:.1f}kg, "
            f"{capacity_pct:.0f}% full)"
        )

    def __str__(self):
        """User-friendly representation."""
        return f"{self._name}: {len(self._stacks)} items"
