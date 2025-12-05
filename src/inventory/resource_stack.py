"""
Resource Stack Module - Flyweight Pattern for Resource Storage

This module provides immutable resource stack representations that share
metadata while tracking quantities.

Design Patterns:
    - Flyweight: Share immutable resource metadata across instances
    - Immutable: Stacks are frozen dataclasses

SOLID Principles:
    - Single Responsibility: Only represents stackable resources
    - Open/Closed: Metadata can be extended without modifying stack
    - Liskov Substitution: All stacks are interchangeable
"""

from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from resources.resource import ResourceType, Resource
from inventory.exceptions import InvalidStackException


@dataclass(frozen=True)
class ResourceMetadata:
    """
    Immutable metadata for resources (Flyweight pattern).

    Shared across multiple ResourceStack instances to save memory.

    Attributes:
        quality: Resource quality multiplier (0.5-2.0)
        regeneration_rate: For regenerative resources
        terrain_multiplier: For terrain-dependent resources
        custom_properties: Extensible property dict
    """
    quality: float = 1.0
    regeneration_rate: float = 0.0
    terrain_multiplier: float = 1.0
    custom_properties: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def from_resource(resource: Resource) -> ResourceMetadata:
        """
        Extract metadata from a Resource instance.

        Args:
            resource: The resource to extract metadata from

        Returns:
            ResourceMetadata: Extracted metadata
        """
        quality = 1.0
        regen_rate = 0.0
        terrain_mult = 1.0

        # Extract type-specific properties
        if hasattr(resource, 'material_quality'):
            quality = resource.material_quality
        if hasattr(resource, 'regeneration_rate'):
            regen_rate = resource.regeneration_rate
        if hasattr(resource, 'terrain_multiplier'):
            terrain_mult = resource.terrain_multiplier

        return ResourceMetadata(
            quality=quality,
            regeneration_rate=regen_rate,
            terrain_multiplier=terrain_mult
        )


@dataclass(frozen=True)
class ResourceStack:
    """
    Immutable representation of a stack of identical resources.

    Uses Flyweight pattern to share resource metadata while tracking quantity.
    Frozen dataclass ensures immutability for thread safety and hashing.

    Attributes:
        resource_type: Type of resource (Food, Material, Water)
        quantity: Number of resources in this stack
        metadata: Immutable resource properties
        max_stack_size: Maximum items in one stack (0 = unlimited)
        weight_per_unit: Weight of each resource unit
        volume_per_unit: Volume of each resource unit

    Examples:
        >>> metadata = ResourceMetadata(quality=1.5)
        >>> stack = ResourceStack(ResourceType.MATERIAL, 50.0, metadata)
        >>> print(stack.total_weight)
        50.0
        >>> remaining, taken = stack.split(20.0)
        >>> print(taken.quantity)
        20.0
    """
    resource_type: ResourceType
    quantity: float
    metadata: ResourceMetadata
    max_stack_size: int = 100
    weight_per_unit: float = 1.0
    volume_per_unit: float = 1.0

    def __post_init__(self):
        """Validate stack parameters."""
        if self.quantity < 0:
            raise InvalidStackException("Quantity cannot be negative")
        if self.max_stack_size < 0:
            raise InvalidStackException("Max stack size cannot be negative")
        if self.max_stack_size > 0 and self.quantity > self.max_stack_size:
            raise InvalidStackException(
                f"Quantity {self.quantity} exceeds max stack size {self.max_stack_size}"
            )
        if self.weight_per_unit < 0 or self.volume_per_unit < 0:
            raise InvalidStackException("Weight and volume must be non-negative")

    @property
    def total_weight(self) -> float:
        """
        Calculate total weight of this stack.

        Returns:
            float: Total weight (quantity * weight_per_unit)
        """
        return self.quantity * self.weight_per_unit

    @property
    def total_volume(self) -> float:
        """
        Calculate total volume of this stack.

        Returns:
            float: Total volume (quantity * volume_per_unit)
        """
        return self.quantity * self.volume_per_unit

    @property
    def is_empty(self) -> bool:
        """
        Check if stack is empty.

        Returns:
            bool: True if quantity is zero
        """
        return self.quantity <= 0

    @property
    def is_full(self) -> bool:
        """
        Check if stack is at maximum capacity.

        Returns:
            bool: True if at max_stack_size (always False if unlimited)
        """
        if self.max_stack_size == 0:
            return False
        return self.quantity >= self.max_stack_size

    def can_add(self, amount: float) -> bool:
        """
        Check if amount can be added to this stack.

        Args:
            amount: Amount to potentially add

        Returns:
            bool: True if addition would not exceed max_stack_size
        """
        if self.max_stack_size == 0:
            return True
        return self.quantity + amount <= self.max_stack_size

    def can_remove(self, amount: float) -> bool:
        """
        Check if amount can be removed from this stack.

        Args:
            amount: Amount to potentially remove

        Returns:
            bool: True if stack contains at least amount
        """
        return self.quantity >= amount

    def with_quantity(self, new_quantity: float) -> ResourceStack:
        """
        Create a new stack with different quantity.

        Immutable pattern - returns new instance rather than modifying.

        Args:
            new_quantity: New quantity value

        Returns:
            ResourceStack: New stack with updated quantity
        """
        return ResourceStack(
            resource_type=self.resource_type,
            quantity=new_quantity,
            metadata=self.metadata,
            max_stack_size=self.max_stack_size,
            weight_per_unit=self.weight_per_unit,
            volume_per_unit=self.volume_per_unit
        )

    def split(self, amount: float) -> tuple[ResourceStack, ResourceStack]:
        """
        Split stack into two stacks.

        Immutable pattern - creates two new stacks rather than modifying.

        Args:
            amount: Amount to split off

        Returns:
            tuple[ResourceStack, ResourceStack]: (remaining_stack, split_stack)

        Raises:
            InvalidStackException: If amount > quantity

        Examples:
            >>> stack = ResourceStack(ResourceType.FOOD, 100.0, metadata)
            >>> remaining, taken = stack.split(30.0)
            >>> print(f"Remaining: {remaining.quantity}, Taken: {taken.quantity}")
            Remaining: 70.0, Taken: 30.0
        """
        if amount > self.quantity:
            raise InvalidStackException(
                f"Cannot split {amount} from stack containing {self.quantity}"
            )
        if amount < 0:
            raise InvalidStackException("Cannot split negative amount")

        remaining_stack = self.with_quantity(self.quantity - amount)
        split_stack = self.with_quantity(amount)

        return remaining_stack, split_stack

    def merge(self, other: ResourceStack) -> ResourceStack:
        """
        Merge another stack into this one.

        Immutable pattern - creates new merged stack.

        Args:
            other: Stack to merge with

        Returns:
            ResourceStack: New merged stack

        Raises:
            InvalidStackException: If stacks are incompatible or exceed max size
        """
        if self.resource_type != other.resource_type:
            raise InvalidStackException("Cannot merge different resource types")
        if self.metadata != other.metadata:
            raise InvalidStackException("Cannot merge stacks with different metadata")

        new_quantity = self.quantity + other.quantity

        if self.max_stack_size > 0 and new_quantity > self.max_stack_size:
            raise InvalidStackException(
                f"Merged quantity {new_quantity} exceeds max stack size {self.max_stack_size}"
            )

        return self.with_quantity(new_quantity)

    def __str__(self) -> str:
        """String representation."""
        return f"{self.resource_type.value} x{self.quantity:.1f}"

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (
            f"ResourceStack(type={self.resource_type.value}, "
            f"qty={self.quantity:.1f}, weight={self.total_weight:.1f}kg)"
        )
