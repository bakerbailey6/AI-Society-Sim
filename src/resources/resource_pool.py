"""
Resource Pool Module - Object Pool Pattern

This module demonstrates the **Object Pool Pattern** by managing a pool
of reusable resource objects. This is an optimization pattern that reduces
the cost of creating and destroying objects frequently.

Design Patterns:
    - Object Pool Pattern: Reuses objects instead of creating new ones

SOLID Principles:
    - Single Responsibility: Manages only object pooling
    - Open/Closed: New pool types can be added without modification
    - Dependency Inversion: Depends on abstract Resource, not concrete types
"""

from __future__ import annotations
from typing import Optional, List, Set
from abc import ABC, abstractmethod

from resources.resource import Resource, ResourceType
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from world.markers import IPoolable


class ObjectPool(ABC):
    """
    Abstract base class for object pools.

    The Object Pool pattern manages a collection of reusable objects,
    allowing them to be borrowed and returned rather than created and
    destroyed repeatedly.

    This is particularly useful for:
    - Expensive-to-create objects
    - Frequently created/destroyed objects
    - Limiting the number of instances
    """

    @abstractmethod
    def acquire(self) -> Optional[object]:
        """
        Acquire an object from the pool.

        Returns:
            Optional[object]: An available object, or None if pool is empty

        Note:
            Subclasses implement specific acquisition logic.
        """
        pass

    @abstractmethod
    def release(self, obj: object) -> bool:
        """
        Return an object to the pool for reuse.

        Args:
            obj (object): The object to return

        Returns:
            bool: True if successfully returned, False otherwise

        Note:
            Objects should be reset to a clean state before reuse.
        """
        pass

    @abstractmethod
    def size(self) -> int:
        """
        Get the current pool size.

        Returns:
            int: Number of objects in the pool
        """
        pass


class ResourcePool(ObjectPool):
    """
    Object pool for managing reusable Resource instances.

    This pool maintains a collection of resource objects that can be
    reset and reused, reducing the overhead of frequent creation and
    garbage collection.

    The pool is particularly useful for resources that are frequently
    depleted and recreated in the same locations (like food sources).

    Attributes:
        _available (List[Resource]): Pool of available resources
        _in_use (Set[str]): IDs of resources currently in use
        _max_size (int): Maximum pool size (0 = unlimited)
        _resource_type (ResourceType): Type of resources in this pool
    """

    def __init__(self, resource_type: ResourceType, max_size: int = 0) -> None:
        """
        Initialize a resource pool.

        Args:
            resource_type (ResourceType): The type of resources to pool
            max_size (int): Maximum pool size (0 for unlimited)

        Examples:
            >>> pool = ResourcePool(ResourceType.FOOD, max_size=50)
        """
        self._available: List[Resource] = []
        self._in_use: Set[str] = set()
        self._max_size: int = max_size
        self._resource_type: ResourceType = resource_type

    @property
    def resource_type(self) -> ResourceType:
        """Get the resource type managed by this pool."""
        return self._resource_type

    @property
    def max_size(self) -> int:
        """Get the maximum pool size."""
        return self._max_size

    def acquire(self) -> Optional[Resource]:
        """
        Acquire a resource from the pool.

        Returns:
            Optional[Resource]: A resource from the pool, or None if empty

        Note:
            The returned resource should be configured (position, amount)
            before use.

        Examples:
            >>> pool = ResourcePool(ResourceType.FOOD)
            >>> resource = pool.acquire()
            >>> if resource:
            ...     resource._position = (5, 5)
            ...     resource._amount = 100.0
        """
        if not self._available:
            return None

        resource = self._available.pop()
        self._in_use.add(resource.resource_id)
        return resource

    def release(self, resource: Resource) -> bool:
        """
        Return a resource to the pool for reuse.

        Args:
            resource (Resource): The resource to return

        Returns:
            bool: True if accepted, False if rejected (wrong type or pool full)

        Note:
            The resource is reset to a clean state before being added back.

        Examples:
            >>> pool.release(used_resource)
        """
        # Verify resource type matches pool
        if resource.resource_type != self._resource_type:
            return False

        # Check if resource was from this pool
        if resource.resource_id not in self._in_use:
            return False

        # Check pool size limit
        if self._max_size > 0 and len(self._available) >= self._max_size:
            return False

        # Reset resource to clean state
        self._reset_resource(resource)

        # Return to pool
        self._in_use.remove(resource.resource_id)
        self._available.append(resource)
        return True

    def _reset_resource(self, resource: Resource) -> None:
        """
        Reset a resource to a clean state for reuse.

        Args:
            resource (Resource): The resource to reset

        Note:
            This resets position and amount. Subclasses may override
            for type-specific reset behavior.
        """
        resource._position = (0, 0)  # Default position
        resource._amount = 0.0        # Reset amount

    def size(self) -> int:
        """
        Get the number of available resources in the pool.

        Returns:
            int: Number of available resources
        """
        return len(self._available)

    def total_size(self) -> int:
        """
        Get the total number of pooled resources (available + in use).

        Returns:
            int: Total pooled resources
        """
        return len(self._available) + len(self._in_use)

    def in_use_count(self) -> int:
        """
        Get the number of resources currently in use.

        Returns:
            int: Number of resources checked out from pool
        """
        return len(self._in_use)

    def add_to_pool(self, resource: Resource) -> bool:
        """
        Add a new resource to the pool.

        This allows the pool to be pre-populated or grown dynamically.

        Args:
            resource (Resource): The resource to add

        Returns:
            bool: True if added, False if rejected (wrong type or pool full)

        Examples:
            >>> pool = ResourcePool(ResourceType.FOOD)
            >>> food = Food(100.0, 100.0, (0, 0))
            >>> pool.add_to_pool(food)
        """
        # Verify type
        if resource.resource_type != self._resource_type:
            return False

        # Check if already in pool
        if resource.resource_id in self._in_use:
            return False

        # Check size limit
        if self._max_size > 0 and len(self._available) >= self._max_size:
            return False

        # Reset and add
        self._reset_resource(resource)
        self._available.append(resource)
        return True

    def clear(self) -> None:
        """
        Clear the pool, removing all available resources.

        Note:
            This only clears available resources. Resources currently
            in use are not affected but can no longer be returned.
        """
        self._available.clear()
        self._in_use.clear()

    def is_empty(self) -> bool:
        """
        Check if the pool has no available resources.

        Returns:
            bool: True if no resources available
        """
        return len(self._available) == 0

    def is_full(self) -> bool:
        """
        Check if the pool is at maximum capacity.

        Returns:
            bool: True if pool is full (when max_size > 0)

        Note:
            Returns False if max_size is 0 (unlimited).
        """
        if self._max_size == 0:
            return False
        return len(self._available) >= self._max_size


class PoolManager:
    """
    Manager for multiple resource pools.

    This class manages separate pools for each resource type,
    demonstrating the Single Responsibility Principle through
    focused pool coordination.

    This simplifies pool management by providing a single interface
    for all resource types.
    """

    def __init__(self, default_max_size: int = 100) -> None:
        """
        Initialize the pool manager.

        Args:
            default_max_size (int): Default maximum size for each pool

        Examples:
            >>> manager = PoolManager(default_max_size=50)
        """
        self._pools: dict[ResourceType, ResourcePool] = {}
        self._default_max_size: int = default_max_size

        # Create pools for each resource type
        for resource_type in ResourceType:
            self._pools[resource_type] = ResourcePool(resource_type, default_max_size)

    def get_pool(self, resource_type: ResourceType) -> ResourcePool:
        """
        Get the pool for a specific resource type.

        Args:
            resource_type (ResourceType): The resource type

        Returns:
            ResourcePool: The pool for that resource type

        Examples:
            >>> manager = PoolManager()
            >>> food_pool = manager.get_pool(ResourceType.FOOD)
        """
        return self._pools[resource_type]

    def acquire_resource(self, resource_type: ResourceType) -> Optional[Resource]:
        """
        Acquire a resource from the appropriate pool.

        Args:
            resource_type (ResourceType): Type of resource needed

        Returns:
            Optional[Resource]: A resource from the pool, or None if unavailable

        Examples:
            >>> manager = PoolManager()
            >>> resource = manager.acquire_resource(ResourceType.FOOD)
        """
        pool = self.get_pool(resource_type)
        return pool.acquire()

    def release_resource(self, resource: Resource) -> bool:
        """
        Return a resource to its appropriate pool.

        Args:
            resource (Resource): The resource to return

        Returns:
            bool: True if successfully returned

        Examples:
            >>> manager.release_resource(used_resource)
        """
        pool = self.get_pool(resource.resource_type)
        return pool.release(resource)

    def get_pool_stats(self) -> dict[ResourceType, dict]:
        """
        Get statistics for all pools.

        Returns:
            dict: Statistics for each resource type pool

        Examples:
            >>> stats = manager.get_pool_stats()
            >>> print(f"Food pool: {stats[ResourceType.FOOD]['available']} available")
        """
        stats = {}
        for resource_type, pool in self._pools.items():
            stats[resource_type] = {
                'available': pool.size(),
                'in_use': pool.in_use_count(),
                'total': pool.total_size(),
                'max_size': pool.max_size
            }
        return stats

    def clear_all_pools(self) -> None:
        """Clear all resource pools."""
        for pool in self._pools.values():
            pool.clear()

    def populate_pool(
        self,
        resource_type: ResourceType,
        resources: List[Resource]
    ) -> int:
        """
        Pre-populate a pool with resources.

        Args:
            resource_type (ResourceType): Type of pool to populate
            resources (List[Resource]): Resources to add

        Returns:
            int: Number of resources successfully added

        Examples:
            >>> food_resources = [Food(...) for _ in range(10)]
            >>> count = manager.populate_pool(ResourceType.FOOD, food_resources)
        """
        pool = self.get_pool(resource_type)
        added = 0
        for resource in resources:
            if pool.add_to_pool(resource):
                added += 1
        return added
