"""
Position Module - Immutable Position Value Object

This module demonstrates the **Immutable Pattern** by providing an immutable
coordinate representation for the grid-based world.

Design Patterns:
    - Immutable Pattern: Position objects cannot be modified after creation

SOLID Principles:
    - Single Responsibility: Manages only coordinate representation and operations
    - Open/Closed: Extensible through new methods without modifying existing ones
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Tuple
import math


@dataclass(frozen=True)
class Position:
    """
    Immutable value object representing a position in 2D grid space.

    The frozen=True parameter makes this class immutable, preventing
    modification after instantiation. This ensures thread-safety and
    predictable behavior when positions are shared across the system.

    Attributes:
        x (int): The x-coordinate in the grid
        y (int): The y-coordinate in the grid

    Examples:
        >>> pos1 = Position(5, 10)
        >>> pos2 = Position(8, 14)
        >>> distance = pos1.distance_to(pos2)
        >>> neighbors = pos1.get_neighbors()
    """

    x: int
    y: int

    def distance_to(self, other: Position) -> float:
        """
        Calculate Euclidean distance to another position.

        Args:
            other (Position): The target position

        Returns:
            float: The Euclidean distance between positions

        Examples:
            >>> pos1 = Position(0, 0)
            >>> pos2 = Position(3, 4)
            >>> pos1.distance_to(pos2)
            5.0
        """
        dx = self.x - other.x
        dy = self.y - other.y
        return math.sqrt(dx * dx + dy * dy)

    def manhattan_distance_to(self, other: Position) -> int:
        """
        Calculate Manhattan (grid) distance to another position.

        Manhattan distance is the sum of absolute differences in coordinates,
        representing the distance when movement is restricted to grid lines.

        Args:
            other (Position): The target position

        Returns:
            int: The Manhattan distance between positions

        Examples:
            >>> pos1 = Position(0, 0)
            >>> pos2 = Position(3, 4)
            >>> pos1.manhattan_distance_to(pos2)
            7
        """
        return abs(self.x - other.x) + abs(self.y - other.y)

    def get_neighbors(self, include_diagonals: bool = False) -> List[Position]:
        """
        Get all neighboring positions.

        Args:
            include_diagonals (bool): If True, includes diagonal neighbors (8 total).
                                     If False, only includes cardinal directions (4 total).

        Returns:
            List[Position]: List of neighboring positions

        Examples:
            >>> pos = Position(5, 5)
            >>> len(pos.get_neighbors(include_diagonals=False))
            4
            >>> len(pos.get_neighbors(include_diagonals=True))
            8
        """
        neighbors = [
            Position(self.x + 1, self.y),      # East
            Position(self.x - 1, self.y),      # West
            Position(self.x, self.y + 1),      # North
            Position(self.x, self.y - 1),      # South
        ]

        if include_diagonals:
            neighbors.extend([
                Position(self.x + 1, self.y + 1),  # Northeast
                Position(self.x + 1, self.y - 1),  # Southeast
                Position(self.x - 1, self.y + 1),  # Northwest
                Position(self.x - 1, self.y - 1),  # Southwest
            ])

        return neighbors

    def is_adjacent_to(self, other: Position, include_diagonals: bool = False) -> bool:
        """
        Check if another position is adjacent to this one.

        Args:
            other (Position): The position to check
            include_diagonals (bool): If True, diagonal positions count as adjacent

        Returns:
            bool: True if positions are adjacent, False otherwise
        """
        return other in self.get_neighbors(include_diagonals)

    def is_within_bounds(self, width: int, height: int) -> bool:
        """
        Check if this position is within given bounds.

        Args:
            width (int): Maximum x-coordinate (exclusive)
            height (int): Maximum y-coordinate (exclusive)

        Returns:
            bool: True if position is within bounds [0, width) x [0, height)

        Examples:
            >>> pos = Position(5, 5)
            >>> pos.is_within_bounds(10, 10)
            True
            >>> pos.is_within_bounds(5, 5)
            False
        """
        return 0 <= self.x < width and 0 <= self.y < height

    def to_tuple(self) -> Tuple[int, int]:
        """
        Convert position to a tuple.

        Returns:
            Tuple[int, int]: The (x, y) coordinates as a tuple
        """
        return (self.x, self.y)

    def __str__(self) -> str:
        """String representation of the position."""
        return f"({self.x}, {self.y})"

    def __repr__(self) -> str:
        """Developer-friendly representation of the position."""
        return f"Position(x={self.x}, y={self.y})"
