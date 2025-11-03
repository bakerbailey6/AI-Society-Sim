"""
Markers Module - Marker Interface Pattern

This module demonstrates the **Marker Interface Pattern** by providing
empty interfaces that mark classes with specific capabilities or properties.

Marker interfaces allow type-based categorization without imposing
implementation requirements, supporting polymorphic behavior.

Design Patterns:
    - Marker Pattern: Interfaces that mark classes with special characteristics

SOLID Principles:
    - Interface Segregation: Small, focused interfaces for specific purposes
    - Dependency Inversion: Code depends on markers, not concrete implementations
"""

from abc import ABC


class IHarvestable(ABC):
    """
    Marker interface indicating that a resource can be harvested.

    Classes implementing this interface can be harvested by agents,
    meaning they can be collected and converted into inventory items.

    This marker allows code to check if something is harvestable without
    knowing the specific resource type:

    Examples:
        >>> if isinstance(resource, IHarvestable):
        ...     agent.harvest(resource)

    Note:
        This is a marker interface - it declares no methods.
        The mere presence of this interface indicates harvestability.
    """
    pass


class ITraversable(ABC):
    """
    Marker interface indicating that a cell can be traversed by agents.

    Cells marked with this interface allow agent movement. This is useful
    for distinguishing between passable terrain (plains, forest) and
    impassable terrain (water, cliffs).

    Examples:
        >>> if isinstance(cell, ITraversable):
        ...     agent.move_to(cell)

    Note:
        This is a marker interface with no method requirements.
    """
    pass


class IDepletable(ABC):
    """
    Marker interface indicating that a resource can be depleted.

    Resources marked with this interface have finite quantities that
    decrease when harvested. This distinguishes them from infinite or
    regenerating resources.

    Examples:
        >>> if isinstance(resource, IDepletable):
        ...     if resource.amount <= 0:
        ...         world.remove_resource(resource)

    Note:
        Marker interface - no methods required.
    """
    pass


class IRegenerative(ABC):
    """
    Marker interface indicating that a resource regenerates over time.

    Resources implementing this marker automatically restore their value
    at each time step, representing renewable resources like food or water.

    Examples:
        >>> if isinstance(resource, IRegenerative):
        ...     resource.regenerate()

    Note:
        This is a marker interface. Actual regeneration logic is
        implemented in the resource class itself.
    """
    pass


class IBlocksMovement(ABC):
    """
    Marker interface indicating that a cell blocks agent movement.

    Cells or objects marked with this interface prevent agents from
    entering or passing through. Useful for walls, water, or other barriers.

    Examples:
        >>> if isinstance(cell, IBlocksMovement):
        ...     return False  # Cannot move here

    Note:
        Marker interface with no method requirements.
    """
    pass


class IObservable(ABC):
    """
    Marker interface indicating that an object can be observed by agents.

    Objects marked with this interface can be detected by agent sensors,
    making them visible during the agent's "sense" phase.

    Examples:
        >>> observable_objects = [obj for obj in nearby if isinstance(obj, IObservable)]

    Note:
        This is a marker interface - no methods declared.
    """
    pass


class IPersistent(ABC):
    """
    Marker interface indicating that an object's state should be persisted.

    Objects implementing this marker should be saved when the simulation
    state is serialized, and restored when loading a saved simulation.

    This is useful for distinguishing between temporary objects and
    objects that should survive save/load cycles.

    Examples:
        >>> persistent_objects = [obj for obj in world if isinstance(obj, IPersistent)]
        >>> save_state(persistent_objects)

    Note:
        Marker interface - indicates persistence requirement only.
    """
    pass


class ICacheable(ABC):
    """
    Marker interface indicating that an object can be cached.

    Objects marked with this interface are safe to cache and reuse,
    typically because they are immutable or have no mutable state.

    This is useful for optimization, allowing frequently accessed
    objects to be stored and reused rather than recreated.

    Examples:
        >>> if isinstance(obj, ICacheable):
        ...     cache[obj.id] = obj

    Note:
        Marker interface with no method requirements.
    """
    pass


class IPoolable(ABC):
    """
    Marker interface indicating that an object can be pooled.

    Objects implementing this marker are suitable for object pooling,
    meaning they can be reset and reused rather than being recreated.

    This is particularly useful for frequently created/destroyed objects
    like resources or temporary entities.

    Examples:
        >>> if isinstance(resource, IPoolable):
        ...     pool.return_object(resource)
        ... else:
        ...     del resource

    Note:
        Marker interface - actual pooling logic is handled by the pool.
    """
    pass


class ILazyLoadable(ABC):
    """
    Marker interface indicating that an object supports lazy loading.

    Objects marked with this interface can be loaded on-demand rather
    than eagerly. This is useful for large worlds where not all data
    needs to be in memory simultaneously.

    Typically used with the Proxy pattern to defer expensive loading
    operations until actually needed.

    Examples:
        >>> if isinstance(cell, ILazyLoadable):
        ...     proxy = CellProxy(cell)

    Note:
        This is a marker interface with no method declarations.
    """
    pass
