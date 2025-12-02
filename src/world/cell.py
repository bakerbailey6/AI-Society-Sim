"""
Cell Module - Abstract Cell Class

This module provides an abstract representation of a single grid cell
in the world. Cells can contain resources, agents, and have terrain properties.

Design Patterns:
    - Template Method (implicit in abstract methods)
    - Marker Interfaces (ITraversable, IObservable)

SOLID Principles:
    - Single Responsibility: Manages only cell-level state and operations
    - Open/Closed: New cell types can be added without modifying existing code
    - Liskov Substitution: All cell subclasses are substitutable for Cell
    - Interface Segregation: Uses focused marker interfaces
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional, Set
from position import Position
from terrain import TerrainTypeEnum, TerrainProperties, TerrainFactory
from markers import ITraversable, IObservable, IBlocksMovement, ILazyLoadable

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from resources.resource import Resource


class Cell(IObservable, ABC):
    """
    Abstract base class for grid cells in the world.

    A cell represents a single position in the grid world and can contain
    resources, agents, and has a terrain type that affects behavior.

    All cells are observable (can be sensed by agents).

    Attributes:
        position (Position): Immutable position of this cell
        terrain_type (TerrainTypeEnum): Type of terrain in this cell
        resources (List[Resource]): Resources present in this cell
        occupants (Set[str]): IDs of agents currently in this cell
    """

    def __init__(
        self,
        position: Position,
        terrain_type: TerrainTypeEnum
    ) -> None:
        """
        Initialize a cell.

        Args:
            position (Position): The immutable cell position
            terrain_type (TerrainTypeEnum): The terrain type

        Examples:
            >>> pos = Position(5, 10)
            >>> cell = ConcreteCell(pos, TerrainTypeEnum.PLAINS)
        """
        self._position: Position = position
        self._terrain_type: TerrainTypeEnum = terrain_type
        self._resources: List[Resource] = []
        self._occupants: Set[str] = set()

    @property
    def position(self) -> Position:
        """Get the cell's position (immutable)."""
        return self._position

    @property
    def terrain_type(self) -> TerrainTypeEnum:
        """Get the terrain type."""
        return self._terrain_type

    @property
    def terrain_properties(self) -> TerrainProperties:
        """Get the terrain properties for this cell."""
        return TerrainFactory.get_properties(self._terrain_type)

    @property
    def resources(self) -> List[Resource]:
        """
        Get a copy of the resources list.

        Returns:
            List[Resource]: Copy of resources (modifications don't affect cell)
        """
        return self._resources.copy()

    @property
    def occupants(self) -> Set[str]:
        """
        Get a copy of the occupants set.

        Returns:
            Set[str]: Copy of occupant IDs
        """
        return self._occupants.copy()

    @abstractmethod
    def add_resource(self, resource: Resource) -> bool:
        """
        Add a resource to this cell.

        Args:
            resource (Resource): The resource to add

        Returns:
            bool: True if added successfully, False otherwise

        Note:
            Subclasses may implement capacity limits or type restrictions.
        """
        pass

    @abstractmethod
    def remove_resource(self, resource_id: str) -> Optional[Resource]:
        """
        Remove a resource from this cell by ID.

        Args:
            resource_id (str): Unique identifier of the resource

        Returns:
            Optional[Resource]: The removed resource, or None if not found

        Note:
            Subclasses handle the actual removal logic.
        """
        pass

    @abstractmethod
    def can_occupy(self, agent_id: str) -> bool:
        """
        Check if an agent can occupy this cell.

        Args:
            agent_id (str): The agent's unique identifier

        Returns:
            bool: True if agent can enter/occupy this cell

        Note:
            Considerations may include terrain traversability, current
            occupants, or cell-specific rules.
        """
        pass

    def add_occupant(self, agent_id: str) -> bool:
        """
        Add an agent to this cell's occupants.

        Args:
            agent_id (str): The agent's unique identifier

        Returns:
            bool: True if added, False if already present
        """
        if agent_id in self._occupants:
            return False
        self._occupants.add(agent_id)
        return True

    def remove_occupant(self, agent_id: str) -> bool:
        """
        Remove an agent from this cell's occupants.

        Args:
            agent_id (str): The agent's unique identifier

        Returns:
            bool: True if removed, False if not present
        """
        if agent_id not in self._occupants:
            return False
        self._occupants.remove(agent_id)
        return True

    def get_resource_by_id(self, resource_id: str) -> Optional[Resource]:
        """
        Get a resource by its ID.

        Args:
            resource_id (str): The resource's unique identifier

        Returns:
            Optional[Resource]: The resource if found, None otherwise
        """
        for resource in self._resources:
            if resource.resource_id == resource_id:
                return resource
        return None

    def is_traversable(self) -> bool:
        """
        Check if this cell can be traversed.

        Returns:
            bool: True if agents can move through this cell

        Note:
            Based on terrain properties.
        """
        return self.terrain_properties.traversable

    def is_occupied(self) -> bool:
        """
        Check if this cell has any occupants.

        Returns:
            bool: True if one or more agents are in this cell
        """
        return len(self._occupants) > 0

    def resource_count(self) -> int:
        """
        Get the number of resources in this cell.

        Returns:
            int: Number of resources
        """
        return len(self._resources)

    def occupant_count(self) -> int:
        """
        Get the number of occupants in this cell.

        Returns:
            int: Number of occupants
        """
        return len(self._occupants)

    def __str__(self) -> str:
        """String representation of the cell."""
        return (f"Cell@{self._position}: {self._terrain_type.value}, "
                f"{len(self._resources)} resources, {len(self._occupants)} occupants")

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (f"{self.__class__.__name__}(pos={self._position}, "
                f"terrain={self._terrain_type.value})")


class StandardCell(Cell, ITraversable):
    """
    Standard traversable cell implementation.

    This is the most common cell type, representing traversable terrain
    like plains, forests, or mountains.

    Implements ITraversable marker to indicate agents can move through it.

    Attributes:
        max_resources (int): Maximum number of resources allowed (0 = unlimited)
        max_occupants (int): Maximum number of occupants allowed (0 = unlimited)
    """

    def __init__(
        self,
        position: Position,
        terrain_type: TerrainTypeEnum,
        max_resources: int = 0,
        max_occupants: int = 0
    ) -> None:
        """
        Initialize a standard cell.

        Args:
            position (Position): Cell position
            terrain_type (TerrainTypeEnum): Terrain type
            max_resources (int): Resource capacity (0 = unlimited)
            max_occupants (int): Occupant capacity (0 = unlimited)

        Examples:
            >>> pos = Position(10, 15)
            >>> cell = StandardCell(pos, TerrainTypeEnum.FOREST, max_resources=5)
        """
        super().__init__(position, terrain_type)
        self._max_resources: int = max_resources
        self._max_occupants: int = max_occupants

    def add_resource(self, resource: Resource) -> bool:
        """
        Add a resource to this cell.

        Args:
            resource (Resource): The resource to add

        Returns:
            bool: True if added, False if at capacity
        """
        # Check capacity
        if self._max_resources > 0 and len(self._resources) >= self._max_resources:
            return False

        self._resources.append(resource)
        return True

    def remove_resource(self, resource_id: str) -> Optional[Resource]:
        """
        Remove a resource by ID.

        Args:
            resource_id (str): Resource identifier

        Returns:
            Optional[Resource]: Removed resource, or None if not found
        """
        for i, resource in enumerate(self._resources):
            if resource.resource_id == resource_id:
                return self._resources.pop(i)
        return None

    def can_occupy(self, agent_id: str) -> bool:
        """
        Check if an agent can occupy this cell.

        Args:
            agent_id (str): Agent identifier

        Returns:
            bool: True if can occupy (cell is traversable and has space)
        """
        # Check if terrain allows traversal
        if not self.is_traversable():
            return False

        # Check occupant capacity
        if self._max_occupants > 0 and len(self._occupants) >= self._max_occupants:
            return False

        return True


class BlockedCell(Cell, IBlocksMovement):
    """
    Cell that blocks agent movement.

    Represents impassable terrain like water or cliffs. Agents cannot
    enter these cells.

    Implements IBlocksMovement marker to indicate blocking behavior.
    """

    def __init__(
        self,
        position: Position,
        terrain_type: TerrainTypeEnum
    ) -> None:
        """
        Initialize a blocked cell.

        Args:
            position (Position): Cell position
            terrain_type (TerrainTypeEnum): Terrain type

        Note:
            Typically used with TerrainTypeEnum.WATER

        Examples:
            >>> pos = Position(3, 8)
            >>> cell = BlockedCell(pos, TerrainTypeEnum.WATER)
        """
        super().__init__(position, terrain_type)

    def add_resource(self, resource: Resource) -> bool:
        """
        Add a resource to this cell.

        Args:
            resource (Resource): The resource to add

        Returns:
            bool: True if added

        Note:
            Blocked cells can still contain resources (e.g., water resources
            in water cells) even though agents cannot enter.
        """
        self._resources.append(resource)
        return True

    def remove_resource(self, resource_id: str) -> Optional[Resource]:
        """
        Remove a resource by ID.

        Args:
            resource_id (str): Resource identifier

        Returns:
            Optional[Resource]: Removed resource, or None if not found
        """
        for i, resource in enumerate(self._resources):
            if resource.resource_id == resource_id:
                return self._resources.pop(i)
        return None

    def can_occupy(self, agent_id: str) -> bool:
        """
        Check if an agent can occupy this cell.

        Args:
            agent_id (str): Agent identifier

        Returns:
            bool: Always False (blocked cells cannot be occupied)
        """
        return False


class LazyCell(Cell, ILazyLoadable):
    """
    Cell that supports lazy loading (for use with Proxy pattern).

    This cell marks itself as lazy-loadable, indicating it can be
    loaded on-demand rather than all at once.

    Implements ILazyLoadable marker to indicate proxy compatibility.

    Note:
        This is primarily for demonstration. The actual lazy loading
        is handled by CellProxy in cell_proxy.py
    """

    def __init__(
        self,
        position: Position,
        terrain_type: TerrainTypeEnum
    ) -> None:
        """
        Initialize a lazy-loadable cell.

        Args:
            position (Position): Cell position
            terrain_type (TerrainTypeEnum): Terrain type
        """
        super().__init__(position, terrain_type)
        self._loaded: bool = False

    def add_resource(self, resource: Resource) -> bool:
        """Add a resource to this cell."""
        self._loaded = True
        self._resources.append(resource)
        return True

    def remove_resource(self, resource_id: str) -> Optional[Resource]:
        """Remove a resource by ID."""
        self._loaded = True
        for i, resource in enumerate(self._resources):
            if resource.resource_id == resource_id:
                return self._resources.pop(i)
        return None

    def can_occupy(self, agent_id: str) -> bool:
        """Check if an agent can occupy this cell."""
        self._loaded = True
        return self.is_traversable()

    def is_loaded(self) -> bool:
        """
        Check if this cell has been loaded.

        Returns:
            bool: True if cell data has been accessed
        """
        return self._loaded
