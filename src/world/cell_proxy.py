"""
Cell Proxy Module - Proxy Pattern for Lazy Loading

This module demonstrates the **Proxy Pattern** by providing a proxy
wrapper for Cell objects that enables lazy loading and access control.

Design Patterns:
    - Proxy Pattern: Controls access to the real cell object

SOLID Principles:
    - Single Responsibility: Manages only proxying and lazy loading
    - Open/Closed: New proxy behaviors can be added without modification
    - Liskov Substitution: CellProxy can be used wherever Cell is expected
    - Dependency Inversion: Depends on abstract Cell, not concrete types
"""

from __future__ import annotations
from typing import List, Optional, Set, Callable
from abc import ABC

from cell import Cell
from position import Position
from terrain import TerrainTypeEnum
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from resources.resource import Resource


class CellProxy(Cell):
    """
    Proxy for Cell objects that enables lazy loading.

    The Proxy pattern provides a surrogate or placeholder for another object
    to control access to it. In this case, the proxy delays loading the
    actual cell data until it's accessed.

    This is useful for large worlds where loading all cells at once would
    be memory-intensive. Cells are loaded on-demand as agents interact
    with them.

    Benefits:
    - Reduces initial memory usage
    - Faster world initialization
    - Only loads cells that are actually accessed

    Attributes:
        _real_cell (Optional[Cell]): The actual cell (None until loaded)
        _loader (Callable): Function to load the real cell when needed
        _access_count (int): Number of times this cell has been accessed
        _is_loaded (bool): Whether the real cell has been loaded
    """

    def __init__(
        self,
        position: Position,
        terrain_type: TerrainTypeEnum,
        loader: Callable[[Position], Cell]
    ) -> None:
        """
        Initialize a cell proxy.

        Args:
            position (Position): The cell position
            terrain_type (TerrainTypeEnum): The terrain type
            loader (Callable[[Position], Cell]): Function to load the real cell

        Note:
            The loader function should create or retrieve the actual Cell
            object when called. It receives the position as a parameter.

        Examples:
            >>> def load_cell(pos: Position) -> Cell:
            ...     # Load cell data from storage/generator
            ...     return StandardCell(pos, TerrainTypeEnum.PLAINS)
            >>> proxy = CellProxy(Position(5, 5), TerrainTypeEnum.PLAINS, load_cell)
        """
        # Initialize with basic info (don't call super().__init__ to avoid loading)
        self._position: Position = position
        self._terrain_type: TerrainTypeEnum = terrain_type
        self._resources: List[Resource] = []  # Placeholder
        self._occupants: Set[str] = set()      # Placeholder

        # Proxy-specific attributes
        self._real_cell: Optional[Cell] = None
        self._loader: Callable[[Position], Cell] = loader
        self._access_count: int = 0
        self._is_loaded: bool = False

    def _ensure_loaded(self) -> None:
        """
        Ensure the real cell is loaded.

        This is the core of the Proxy pattern - lazy initialization.
        The real cell is only loaded when actually needed.

        Note:
            This method is called before any operation that requires
            the real cell data.
        """
        if not self._is_loaded:
            self._real_cell = self._loader(self._position)
            self._is_loaded = True
            self._access_count = 1
        else:
            self._access_count += 1

    @property
    def access_count(self) -> int:
        """
        Get the number of times this cell has been accessed.

        Returns:
            int: Access count (useful for cache management)
        """
        return self._access_count

    @property
    def is_loaded(self) -> bool:
        """
        Check if the real cell has been loaded.

        Returns:
            bool: True if cell data is in memory
        """
        return self._is_loaded

    # Override Cell methods to proxy to the real cell

    @property
    def resources(self) -> List[Resource]:
        """
        Get resources (loads cell if needed).

        Returns:
            List[Resource]: Copy of resources list
        """
        self._ensure_loaded()
        return self._real_cell.resources

    @property
    def occupants(self) -> Set[str]:
        """
        Get occupants (loads cell if needed).

        Returns:
            Set[str]: Copy of occupants set
        """
        self._ensure_loaded()
        return self._real_cell.occupants

    def add_resource(self, resource: Resource) -> bool:
        """
        Add a resource (loads cell if needed).

        Args:
            resource (Resource): Resource to add

        Returns:
            bool: True if added successfully
        """
        self._ensure_loaded()
        return self._real_cell.add_resource(resource)

    def remove_resource(self, resource_id: str) -> Optional[Resource]:
        """
        Remove a resource (loads cell if needed).

        Args:
            resource_id (str): Resource identifier

        Returns:
            Optional[Resource]: Removed resource, or None
        """
        self._ensure_loaded()
        return self._real_cell.remove_resource(resource_id)

    def can_occupy(self, agent_id: str) -> bool:
        """
        Check if an agent can occupy (loads cell if needed).

        Args:
            agent_id (str): Agent identifier

        Returns:
            bool: True if agent can occupy
        """
        self._ensure_loaded()
        return self._real_cell.can_occupy(agent_id)

    def add_occupant(self, agent_id: str) -> bool:
        """
        Add an occupant (loads cell if needed).

        Args:
            agent_id (str): Agent identifier

        Returns:
            bool: True if added
        """
        self._ensure_loaded()
        return self._real_cell.add_occupant(agent_id)

    def remove_occupant(self, agent_id: str) -> bool:
        """
        Remove an occupant (loads cell if needed).

        Args:
            agent_id (str): Agent identifier

        Returns:
            bool: True if removed
        """
        self._ensure_loaded()
        return self._real_cell.remove_occupant(agent_id)

    def get_resource_by_id(self, resource_id: str) -> Optional[Resource]:
        """
        Get a resource by ID (loads cell if needed).

        Args:
            resource_id (str): Resource identifier

        Returns:
            Optional[Resource]: The resource, or None
        """
        self._ensure_loaded()
        return self._real_cell.get_resource_by_id(resource_id)

    def unload(self) -> bool:
        """
        Unload the real cell from memory to save space.

        This allows infrequently accessed cells to be unloaded,
        reducing memory usage. They can be reloaded later if needed.

        Returns:
            bool: True if unloaded, False if not loaded

        Note:
            This would typically be called by a cache manager based on
            access patterns (e.g., LRU eviction).

        Examples:
            >>> if proxy.access_count < 5:
            ...     proxy.unload()  # Unload rarely-accessed cells
        """
        if self._is_loaded:
            self._real_cell = None
            self._is_loaded = False
            return True
        return False

    def __str__(self) -> str:
        """String representation."""
        loaded_status = "loaded" if self._is_loaded else "not loaded"
        return f"CellProxy@{self._position}: {loaded_status}, accessed {self._access_count} times"


class CachingCellProxy(CellProxy):
    """
    Enhanced proxy with caching policy.

    This proxy extends CellProxy with automatic cache management,
    unloading cells based on access patterns.

    Attributes:
        _max_idle_accesses (int): Unload if not accessed in this many cycles
        _cycles_since_access (int): Cycles since last access
    """

    def __init__(
        self,
        position: Position,
        terrain_type: TerrainTypeEnum,
        loader: Callable[[Position], Cell],
        max_idle_accesses: int = 100
    ) -> None:
        """
        Initialize a caching cell proxy.

        Args:
            position (Position): Cell position
            terrain_type (TerrainTypeEnum): Terrain type
            loader (Callable): Cell loader function
            max_idle_accesses (int): Unload after this many idle cycles

        Examples:
            >>> proxy = CachingCellProxy(pos, terrain, load_cell, max_idle_accesses=50)
        """
        super().__init__(position, terrain_type, loader)
        self._max_idle_accesses: int = max_idle_accesses
        self._cycles_since_access: int = 0

    def _ensure_loaded(self) -> None:
        """Ensure cell is loaded and reset idle counter."""
        super()._ensure_loaded()
        self._cycles_since_access = 0

    def tick(self) -> None:
        """
        Update the cache state for this time step.

        Call this each simulation step to update idle counters
        and potentially unload unused cells.

        Examples:
            >>> for proxy in all_proxies:
            ...     proxy.tick()  # Called each simulation step
        """
        if self._is_loaded:
            self._cycles_since_access += 1

            # Auto-unload if idle too long
            if self._cycles_since_access >= self._max_idle_accesses:
                self.unload()


class ProtectedCellProxy(CellProxy):
    """
    Proxy with access control and validation.

    This proxy adds permission checks and validation before
    allowing access to the real cell.

    Attributes:
        _access_validator (Callable): Function to validate access requests
    """

    def __init__(
        self,
        position: Position,
        terrain_type: TerrainTypeEnum,
        loader: Callable[[Position], Cell],
        access_validator: Optional[Callable[[str], bool]] = None
    ) -> None:
        """
        Initialize a protected cell proxy.

        Args:
            position (Position): Cell position
            terrain_type (TerrainTypeEnum): Terrain type
            loader (Callable): Cell loader function
            access_validator (Optional[Callable]): Function to validate access

        Note:
            The validator receives an operation name and returns True if allowed.

        Examples:
            >>> def validator(operation: str) -> bool:
            ...     return operation in ["read", "add_resource"]
            >>> proxy = ProtectedCellProxy(pos, terrain, loader, validator)
        """
        super().__init__(position, terrain_type, loader)
        self._access_validator: Optional[Callable[[str], bool]] = access_validator

    def _check_access(self, operation: str) -> bool:
        """
        Check if an operation is allowed.

        Args:
            operation (str): The operation name

        Returns:
            bool: True if allowed

        Raises:
            PermissionError: If operation is not allowed
        """
        if self._access_validator and not self._access_validator(operation):
            raise PermissionError(f"Access denied for operation: {operation}")
        return True

    def add_resource(self, resource: Resource) -> bool:
        """Add resource with permission check."""
        self._check_access("add_resource")
        return super().add_resource(resource)

    def remove_resource(self, resource_id: str) -> Optional[Resource]:
        """Remove resource with permission check."""
        self._check_access("remove_resource")
        return super().remove_resource(resource_id)

    def add_occupant(self, agent_id: str) -> bool:
        """Add occupant with permission check."""
        self._check_access("add_occupant")
        return super().add_occupant(agent_id)
