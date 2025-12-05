"""
Inventory Package - Resource Storage and Management System

This package provides a comprehensive inventory system for agents and stockpiles
to store, manage, and transfer resources.

Design Patterns:
    - Composite: Inventory can contain nested containers
    - Strategy: Different capacity calculation strategies
    - Observer: Notify listeners of inventory changes
    - Flyweight: Share immutable resource metadata
    - Iterator: Iterate through inventory contents

SOLID Principles:
    - Single Responsibility: Each class has one clear purpose
    - Open/Closed: Easy to extend with new capacity strategies
    - Liskov Substitution: All strategies are substitutable
    - Interface Segregation: Focused interfaces
    - Dependency Inversion: Depend on abstractions

Modules:
    - resource_stack: Stackable resource representation
    - capacity_strategy: Capacity limit strategies
    - inventory: Core inventory container
    - stockpile: Shared storage locations
    - transfer: Resource transfer operations
    - observers: Observer pattern for changes
    - exceptions: Custom exceptions
"""

from inventory.resource_stack import ResourceStack, ResourceMetadata
from inventory.capacity_strategy import (
    CapacityStrategy,
    SlotBasedCapacity,
    WeightBasedCapacity,
    VolumeBasedCapacity,
    CompositeCapacity,
    UnlimitedCapacity
)
from inventory.inventory import Inventory, InventoryEvent
from inventory.observers import InventoryObserver
from inventory.exceptions import (
    InventoryException,
    InsufficientResourcesException,
    CapacityExceededException,
    InvalidStackException
)

__all__ = [
    # Resource Stack
    "ResourceStack",
    "ResourceMetadata",

    # Capacity Strategies
    "CapacityStrategy",
    "SlotBasedCapacity",
    "WeightBasedCapacity",
    "VolumeBasedCapacity",
    "CompositeCapacity",
    "UnlimitedCapacity",

    # Core Inventory
    "Inventory",
    "InventoryEvent",

    # Observers
    "InventoryObserver",

    # Exceptions
    "InventoryException",
    "InsufficientResourcesException",
    "CapacityExceededException",
    "InvalidStackException",
]
