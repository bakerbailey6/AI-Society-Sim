"""
World Facade Module - Facade Pattern for Simplified World Access

This module demonstrates the **Facade Pattern** by providing a simplified
interface to the complex world subsystem.

Design Patterns:
    - Facade Pattern: Provides unified, simplified interface to complex subsystem

SOLID Principles:
    - Single Responsibility: Provides only simplified world access
    - Dependency Inversion: Depends on abstractions (World, Cell, Resource)
"""

from __future__ import annotations
from typing import Optional, List
from position import Position
from world import World
from cell import Cell
from iterators import RadiusIterator
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from resources.resource import Resource, ResourceType
from resources.factory import FactoryRegistry


class WorldFacade:
    """
    Facade providing simplified access to the world subsystem.

    The Facade pattern provides a simple interface to a complex subsystem.
    Instead of clients dealing with World, Cells, Resources, Factories, etc.,
    they can use this facade for common operations.

    This reduces coupling and makes the system easier to use.

    Examples:
        >>> facade = WorldFacade(world)
        >>> facade.place_resource_at((5, 5), ResourceType.FOOD)
        >>> resources = facade.get_nearby_resources((5, 5), radius=3)
    """

    def __init__(self, world: World) -> None:
        """
        Initialize the world facade.

        Args:
            world (World): The world instance to wrap
        """
        self._world: World = world
        self._resource_factory: FactoryRegistry = FactoryRegistry()

    # Simplified world queries

    def get_cell_at(self, position: tuple) -> Optional[Cell]:
        """
        Get a cell at coordinates (simplified interface).

        Args:
            position (tuple): (x, y) coordinates

        Returns:
            Optional[Cell]: The cell, or None if invalid

        Examples:
            >>> cell = facade.get_cell_at((10, 15))
        """
        pos = Position(position[0], position[1])
        return self._world.get_cell(pos)

    def is_position_traversable(self, position: tuple) -> bool:
        """
        Check if a position can be traversed.

        Args:
            position (tuple): (x, y) coordinates

        Returns:
            bool: True if traversable

        Examples:
            >>> if facade.is_position_traversable((5, 5)):
            ...     agent.move_to((5, 5))
        """
        cell = self.get_cell_at(position)
        return cell.is_traversable() if cell else False

    def is_position_occupied(self, position: tuple) -> bool:
        """
        Check if a position has occupants.

        Args:
            position (tuple): (x, y) coordinates

        Returns:
            bool: True if occupied
        """
        cell = self.get_cell_at(position)
        return cell.is_occupied() if cell else False

    # Simplified resource operations

    def place_resource_at(
        self,
        position: tuple,
        resource_type: ResourceType,
        amount: Optional[float] = None
    ) -> bool:
        """
        Place a resource at a position (simplified creation).

        Args:
            position (tuple): (x, y) coordinates
            resource_type (ResourceType): Type of resource to create
            amount (Optional[float]): Initial amount

        Returns:
            bool: True if placed successfully

        Examples:
            >>> facade.place_resource_at((5, 5), ResourceType.FOOD, amount=100.0)
        """
        cell = self.get_cell_at(position)
        if not cell:
            return False

        resource = self._resource_factory.create_resource(
            resource_type,
            position,
            amount
        )

        if resource:
            return cell.add_resource(resource)
        return False

    def get_resources_at(self, position: tuple) -> List[Resource]:
        """
        Get all resources at a position.

        Args:
            position (tuple): (x, y) coordinates

        Returns:
            List[Resource]: Resources at that position

        Examples:
            >>> resources = facade.get_resources_at((5, 5))
            >>> for resource in resources:
            ...     print(resource.resource_type)
        """
        cell = self.get_cell_at(position)
        return cell.resources if cell else []

    def get_nearby_resources(
        self,
        position: tuple,
        radius: int,
        resource_type: Optional[ResourceType] = None
    ) -> List[Resource]:
        """
        Get resources within a radius of a position.

        Args:
            position (tuple): Center (x, y) coordinates
            radius (int): Search radius
            resource_type (Optional[ResourceType]): Filter by type

        Returns:
            List[Resource]: All matching resources in radius

        Examples:
            >>> food_nearby = facade.get_nearby_resources((5, 5), radius=3, resource_type=ResourceType.FOOD)
        """
        center = Position(position[0], position[1])
        iterator = RadiusIterator(
            center,
            radius,
            self._world.width,
            self._world.height,
            include_center=True
        )

        resources = []
        for pos in iterator:
            cell = self._world.get_cell(pos)
            if cell:
                cell_resources = cell.resources
                if resource_type:
                    cell_resources = [r for r in cell_resources if r.resource_type == resource_type]
                resources.extend(cell_resources)

        return resources

    # Simplified agent operations

    def can_agent_move_to(self, agent_id: str, position: tuple) -> bool:
        """
        Check if an agent can move to a position.

        Args:
            agent_id (str): Agent identifier
            position (tuple): Target (x, y) coordinates

        Returns:
            bool: True if agent can move there

        Examples:
            >>> if facade.can_agent_move_to("agent_1", (10, 10)):
            ...     facade.move_agent_to("agent_1", (9, 9), (10, 10))
        """
        cell = self.get_cell_at(position)
        return cell.can_occupy(agent_id) if cell else False

    def move_agent_to(
        self,
        agent_id: str,
        from_position: tuple,
        to_position: tuple
    ) -> bool:
        """
        Move an agent from one position to another.

        Args:
            agent_id (str): Agent identifier
            from_position (tuple): Current (x, y)
            to_position (tuple): Target (x, y)

        Returns:
            bool: True if moved successfully

        Examples:
            >>> facade.move_agent_to("agent_1", (5, 5), (5, 6))
        """
        from_cell = self.get_cell_at(from_position)
        to_cell = self.get_cell_at(to_position)

        if not from_cell or not to_cell:
            return False

        if not to_cell.can_occupy(agent_id):
            return False

        from_cell.remove_occupant(agent_id)
        to_cell.add_occupant(agent_id)
        return True

    # Simplified world state queries

    def get_world_dimensions(self) -> tuple:
        """
        Get world dimensions.

        Returns:
            tuple: (width, height)

        Examples:
            >>> width, height = facade.get_world_dimensions()
        """
        return (self._world.width, self._world.height)

    def get_current_time(self) -> int:
        """
        Get current simulation time.

        Returns:
            int: Current time step

        Examples:
            >>> time = facade.get_current_time()
        """
        return self._world.current_time

    def advance_simulation(self) -> None:
        """
        Advance the simulation by one time step.

        Examples:
            >>> facade.advance_simulation()
        """
        self._world.update()

    # Simplified position utilities

    def get_distance_between(self, pos1: tuple, pos2: tuple) -> float:
        """
        Calculate distance between two positions.

        Args:
            pos1 (tuple): First (x, y)
            pos2 (tuple): Second (x, y)

        Returns:
            float: Euclidean distance

        Examples:
            >>> dist = facade.get_distance_between((0, 0), (3, 4))
            >>> assert dist == 5.0
        """
        p1 = Position(pos1[0], pos1[1])
        p2 = Position(pos2[0], pos2[1])
        return p1.distance_to(p2)

    def get_neighbors(self, position: tuple, include_diagonals: bool = False) -> List[tuple]:
        """
        Get neighboring positions.

        Args:
            position (tuple): Center (x, y)
            include_diagonals (bool): Include diagonal neighbors

        Returns:
            List[tuple]: List of neighboring (x, y) positions

        Examples:
            >>> neighbors = facade.get_neighbors((5, 5), include_diagonals=True)
        """
        pos = Position(position[0], position[1])
        neighbor_positions = pos.get_neighbors(include_diagonals)

        # Filter to valid positions only
        valid_neighbors = [
            (p.x, p.y) for p in neighbor_positions
            if self._world.is_valid_position(p)
        ]

        return valid_neighbors

    def __str__(self) -> str:
        """String representation."""
        return f"WorldFacade(world={self._world})"
