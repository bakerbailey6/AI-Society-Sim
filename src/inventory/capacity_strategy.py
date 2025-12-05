"""
Capacity Strategy Module - Strategy Pattern for Inventory Limits

This module provides different strategies for calculating and enforcing
inventory capacity constraints.

Design Patterns:
    - Strategy: Different capacity calculation algorithms
    - Composite: Combine multiple strategies

SOLID Principles:
    - Single Responsibility: Each strategy handles one type of constraint
    - Open/Closed: New strategies can be added without modification
    - Liskov Substitution: All strategies are substitutable
    - Interface Segregation: Focused strategy interface
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, List

if TYPE_CHECKING:
    from inventory.inventory import Inventory
    from inventory.resource_stack import ResourceStack


class CapacityStrategy(ABC):
    """
    Abstract strategy for calculating inventory capacity.

    Implements Strategy pattern for different capacity limit types.

    Subclasses define specific capacity constraints like:
    - Slot-based (fixed number of stacks, like Minecraft)
    - Weight-based (total weight limit, affected by strength)
    - Volume-based (total volume limit, backpack size)
    - Composite (combination of multiple constraints)
    """

    @abstractmethod
    def can_add(self, inventory: Inventory, stack: ResourceStack) -> bool:
        """
        Check if a resource stack can be added to inventory.

        Args:
            inventory: The inventory to check
            stack: The stack to potentially add

        Returns:
            bool: True if stack can be added within capacity
        """
        pass

    @abstractmethod
    def get_remaining_capacity(self, inventory: Inventory) -> float:
        """
        Get remaining capacity as a percentage.

        Args:
            inventory: The inventory to check

        Returns:
            float: Remaining capacity (0.0 = full, 1.0 = empty)
        """
        pass

    @abstractmethod
    def get_capacity_info(self, inventory: Inventory) -> dict:
        """
        Get detailed capacity information.

        Args:
            inventory: The inventory to analyze

        Returns:
            dict: Capacity information
        """
        pass


class UnlimitedCapacity(CapacityStrategy):
    """
    Strategy with no capacity limits.

    Useful for stockpiles or admin inventories.
    """

    def can_add(self, inventory: Inventory, stack: ResourceStack) -> bool:
        """Always returns True (unlimited)."""
        return True

    def get_remaining_capacity(self, inventory: Inventory) -> float:
        """Always returns 1.0 (always has capacity)."""
        return 1.0

    def get_capacity_info(self, inventory: Inventory) -> dict:
        """Return unlimited capacity info."""
        return {
            "type": "unlimited",
            "used": "N/A",
            "max": "unlimited",
            "percentage": 100.0
        }


class SlotBasedCapacity(CapacityStrategy):
    """
    Slot-based capacity strategy (like Minecraft).

    Each stack occupies one slot regardless of quantity.
    Empty slots can accept new stacks.

    Attributes:
        max_slots: Maximum number of stacks allowed
    """

    def __init__(self, max_slots: int = 20):
        """
        Initialize slot-based capacity.

        Args:
            max_slots: Maximum number of stacks (default 20)

        Raises:
            ValueError: If max_slots < 1
        """
        if max_slots < 1:
            raise ValueError("max_slots must be at least 1")
        self.max_slots = max_slots

    def can_add(self, inventory: Inventory, stack: ResourceStack) -> bool:
        """
        Check if stack can be added.

        Tries to merge with existing stacks first.
        If no merge possible, checks for empty slots.

        Args:
            inventory: The inventory
            stack: Stack to add

        Returns:
            bool: True if can add
        """
        # Try to find existing stack to merge with
        for existing in inventory._stacks:
            if (existing.resource_type == stack.resource_type and
                existing.metadata == stack.metadata and
                existing.can_add(stack.quantity)):
                return True

        # Need new slot
        return len(inventory._stacks) < self.max_slots

    def get_remaining_capacity(self, inventory: Inventory) -> float:
        """
        Get remaining capacity as percentage.

        Args:
            inventory: The inventory

        Returns:
            float: Percentage of slots remaining (0.0-1.0)
        """
        used_slots = len(inventory._stacks)
        return (self.max_slots - used_slots) / self.max_slots

    def get_capacity_info(self, inventory: Inventory) -> dict:
        """Get slot capacity details."""
        used = len(inventory._stacks)
        return {
            "type": "slots",
            "used": used,
            "max": self.max_slots,
            "percentage": (used / self.max_slots) * 100
        }


class WeightBasedCapacity(CapacityStrategy):
    """
    Weight-based capacity strategy.

    Total weight of all items cannot exceed max_weight.
    Typically affected by agent strength attribute.

    Attributes:
        max_weight: Maximum weight in kilograms
    """

    def __init__(self, max_weight: float):
        """
        Initialize weight-based capacity.

        Args:
            max_weight: Maximum weight in kg

        Raises:
            ValueError: If max_weight <= 0
        """
        if max_weight <= 0:
            raise ValueError("max_weight must be positive")
        self.max_weight = max_weight

    def can_add(self, inventory: Inventory, stack: ResourceStack) -> bool:
        """
        Check if stack's weight can be added.

        Args:
            inventory: The inventory
            stack: Stack to add

        Returns:
            bool: True if adding won't exceed max_weight
        """
        current_weight = inventory.total_weight
        return current_weight + stack.total_weight <= self.max_weight

    def get_remaining_capacity(self, inventory: Inventory) -> float:
        """
        Get remaining weight capacity as percentage.

        Args:
            inventory: The inventory

        Returns:
            float: Percentage of weight remaining (0.0-1.0)
        """
        used = inventory.total_weight
        if self.max_weight == 0:
            return 0.0
        return (self.max_weight - used) / self.max_weight

    def get_capacity_info(self, inventory: Inventory) -> dict:
        """Get weight capacity details."""
        used = inventory.total_weight
        return {
            "type": "weight",
            "used": round(used, 2),
            "max": self.max_weight,
            "percentage": (used / self.max_weight) * 100
        }


class VolumeBasedCapacity(CapacityStrategy):
    """
    Volume-based capacity strategy.

    Total volume of all items cannot exceed max_volume.
    Represents physical backpack/container size.

    Attributes:
        max_volume: Maximum volume in cubic meters
    """

    def __init__(self, max_volume: float):
        """
        Initialize volume-based capacity.

        Args:
            max_volume: Maximum volume in m³

        Raises:
            ValueError: If max_volume <= 0
        """
        if max_volume <= 0:
            raise ValueError("max_volume must be positive")
        self.max_volume = max_volume

    def can_add(self, inventory: Inventory, stack: ResourceStack) -> bool:
        """
        Check if stack's volume can be added.

        Args:
            inventory: The inventory
            stack: Stack to add

        Returns:
            bool: True if adding won't exceed max_volume
        """
        current_volume = inventory.total_volume
        return current_volume + stack.total_volume <= self.max_volume

    def get_remaining_capacity(self, inventory: Inventory) -> float:
        """
        Get remaining volume capacity as percentage.

        Args:
            inventory: The inventory

        Returns:
            float: Percentage of volume remaining (0.0-1.0)
        """
        used = inventory.total_volume
        if self.max_volume == 0:
            return 0.0
        return (self.max_volume - used) / self.max_volume

    def get_capacity_info(self, inventory: Inventory) -> dict:
        """Get volume capacity details."""
        used = inventory.total_volume
        return {
            "type": "volume",
            "used": round(used, 2),
            "max": self.max_volume,
            "percentage": (used / self.max_volume) * 100
        }


class CompositeCapacity(CapacityStrategy):
    """
    Composite strategy combining multiple constraints (Composite pattern).

    All sub-strategies must allow addition for the composite to allow it.
    Remaining capacity is the minimum across all strategies.

    This allows realistic constraints like:
    - "I can only carry 50kg AND only have 20 slots"
    - Both constraints must be satisfied

    Attributes:
        strategies: List of capacity strategies to combine
    """

    def __init__(self, strategies: List[CapacityStrategy]):
        """
        Initialize composite capacity.

        Args:
            strategies: List of strategies to combine

        Raises:
            ValueError: If strategies list is empty
        """
        if not strategies:
            raise ValueError("Must provide at least one strategy")
        self.strategies = strategies

    def can_add(self, inventory: Inventory, stack: ResourceStack) -> bool:
        """
        Check if all strategies allow addition.

        Args:
            inventory: The inventory
            stack: Stack to add

        Returns:
            bool: True only if ALL strategies allow it
        """
        return all(s.can_add(inventory, stack) for s in self.strategies)

    def get_remaining_capacity(self, inventory: Inventory) -> float:
        """
        Get minimum remaining capacity across all strategies.

        The most restrictive constraint determines capacity.

        Args:
            inventory: The inventory

        Returns:
            float: Minimum percentage remaining (0.0-1.0)
        """
        return min(s.get_remaining_capacity(inventory) for s in self.strategies)

    def get_capacity_info(self, inventory: Inventory) -> dict:
        """Get combined capacity details."""
        return {
            "type": "composite",
            "strategies": [s.get_capacity_info(inventory) for s in self.strategies],
            "most_restrictive": min(
                (s.get_remaining_capacity(inventory), s.get_capacity_info(inventory)['type'])
                for s in self.strategies
            )[1]
        }
