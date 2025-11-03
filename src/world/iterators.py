"""
Iterators Module - Iterator Pattern for Grid Traversal

This module demonstrates the **Iterator Pattern** by providing different
ways to iterate over cells in the grid world.

Design Patterns:
    - Iterator Pattern: Provides sequential access without exposing internal structure

SOLID Principles:
    - Single Responsibility: Each iterator handles one traversal strategy
    - Open/Closed: New iterators can be added without modifying existing code
    - Interface Segregation: Minimal iterator interface
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Iterator, Optional
from position import Position
from cell import Cell


class GridIterator(ABC):
    """
    Abstract base class for grid iterators.

    The Iterator pattern provides a way to access elements of a collection
    sequentially without exposing the underlying representation.

    This allows different traversal strategies (all cells, radius, path)
    to be implemented independently.
    """

    @abstractmethod
    def __iter__(self) -> Iterator[Position]:
        """
        Get an iterator for positions.

        Returns:
            Iterator[Position]: Iterator over positions

        Note:
            Subclasses implement specific iteration strategies.
        """
        pass

    @abstractmethod
    def has_next(self) -> bool:
        """
        Check if there are more positions to iterate.

        Returns:
            bool: True if more positions remain
        """
        pass

    @abstractmethod
    def next(self) -> Optional[Position]:
        """
        Get the next position.

        Returns:
            Optional[Position]: Next position, or None if exhausted
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset the iterator to the beginning."""
        pass


class AllCellsIterator(GridIterator):
    """
    Iterator that traverses all cells in the grid.

    Iterates row by row from (0,0) to (width-1, height-1).

    Examples:
        >>> iterator = AllCellsIterator(10, 10)
        >>> for pos in iterator:
        ...     print(pos)  # Prints all positions from (0,0) to (9,9)
    """

    def __init__(self, width: int, height: int) -> None:
        """
        Initialize the all-cells iterator.

        Args:
            width (int): Grid width
            height (int): Grid height
        """
        self._width: int = width
        self._height: int = height
        self._current_x: int = 0
        self._current_y: int = 0

    def __iter__(self) -> Iterator[Position]:
        """Iterate over all positions."""
        for y in range(self._height):
            for x in range(self._width):
                yield Position(x, y)

    def has_next(self) -> bool:
        """Check if more positions remain."""
        return self._current_y < self._height

    def next(self) -> Optional[Position]:
        """Get the next position."""
        if not self.has_next():
            return None

        pos = Position(self._current_x, self._current_y)

        # Advance to next position
        self._current_x += 1
        if self._current_x >= self._width:
            self._current_x = 0
            self._current_y += 1

        return pos

    def reset(self) -> None:
        """Reset to the beginning."""
        self._current_x = 0
        self._current_y = 0


class RadiusIterator(GridIterator):
    """
    Iterator that traverses cells within a radius of a center point.

    Iterates in expanding circles from the center outward.

    Examples:
        >>> iterator = RadiusIterator(Position(5, 5), radius=3, width=10, height=10)
        >>> for pos in iterator:
        ...     print(pos)  # Prints positions within 3 cells of (5,5)
    """

    def __init__(
        self,
        center: Position,
        radius: int,
        width: int,
        height: int,
        include_center: bool = True
    ) -> None:
        """
        Initialize the radius iterator.

        Args:
            center (Position): Center position
            radius (int): Maximum distance from center
            width (int): Grid width (for bounds checking)
            height (int): Grid height (for bounds checking)
            include_center (bool): Whether to include the center position
        """
        self._center: Position = center
        self._radius: int = radius
        self._width: int = width
        self._height: int = height
        self._include_center: bool = include_center
        self._positions: List[Position] = self._calculate_positions()
        self._index: int = 0

    def _calculate_positions(self) -> List[Position]:
        """
        Calculate all positions within radius.

        Returns:
            List[Position]: Positions within radius, sorted by distance
        """
        positions = []

        for dy in range(-self._radius, self._radius + 1):
            for dx in range(-self._radius, self._radius + 1):
                # Skip center if not included
                if not self._include_center and dx == 0 and dy == 0:
                    continue

                # Check if within radius (using Manhattan distance)
                if abs(dx) + abs(dy) <= self._radius:
                    x = self._center.x + dx
                    y = self._center.y + dy

                    # Check bounds
                    if 0 <= x < self._width and 0 <= y < self._height:
                        positions.append(Position(x, y))

        return positions

    def __iter__(self) -> Iterator[Position]:
        """Iterate over positions within radius."""
        return iter(self._positions)

    def has_next(self) -> bool:
        """Check if more positions remain."""
        return self._index < len(self._positions)

    def next(self) -> Optional[Position]:
        """Get the next position."""
        if not self.has_next():
            return None

        pos = self._positions[self._index]
        self._index += 1
        return pos

    def reset(self) -> None:
        """Reset to the beginning."""
        self._index = 0


class PathIterator(GridIterator):
    """
    Iterator that follows a specific path of positions.

    Useful for iterating along agent movement paths or predefined routes.

    Examples:
        >>> path = [Position(0, 0), Position(1, 0), Position(2, 0)]
        >>> iterator = PathIterator(path)
        >>> for pos in iterator:
        ...     print(pos)
    """

    def __init__(self, path: List[Position]) -> None:
        """
        Initialize the path iterator.

        Args:
            path (List[Position]): The path to follow
        """
        self._path: List[Position] = path
        self._index: int = 0

    def __iter__(self) -> Iterator[Position]:
        """Iterate over the path."""
        return iter(self._path)

    def has_next(self) -> bool:
        """Check if more positions remain in the path."""
        return self._index < len(self._path)

    def next(self) -> Optional[Position]:
        """Get the next position in the path."""
        if not self.has_next():
            return None

        pos = self._path[self._index]
        self._index += 1
        return pos

    def reset(self) -> None:
        """Reset to the start of the path."""
        self._index = 0


class SpiralIterator(GridIterator):
    """
    Iterator that traverses cells in a spiral pattern from center outward.

    Moves in a spiral: right, down, left, left, up, up, right, right, right, ...

    Examples:
        >>> iterator = SpiralIterator(Position(5, 5), width=10, height=10)
        >>> for pos in iterator:
        ...     print(pos)  # Spirals outward from (5,5)
    """

    def __init__(self, center: Position, width: int, height: int, max_radius: int = -1) -> None:
        """
        Initialize the spiral iterator.

        Args:
            center (Position): Starting center position
            width (int): Grid width
            height (int): Grid height
            max_radius (int): Maximum spiral radius (-1 for entire grid)
        """
        self._center: Position = center
        self._width: int = width
        self._height: int = height
        self._max_radius: int = max_radius if max_radius >= 0 else max(width, height)
        self._positions: List[Position] = self._calculate_spiral()
        self._index: int = 0

    def _calculate_spiral(self) -> List[Position]:
        """
        Calculate spiral path positions.

        Returns:
            List[Position]: Positions in spiral order
        """
        positions = [self._center]
        x, y = self._center.x, self._center.y
        dx, dy = 1, 0  # Start moving right
        steps = 1
        step_count = 0

        while len(positions) < self._width * self._height:
            for _ in range(2):  # Two sides per ring
                for _ in range(steps):
                    x += dx
                    y += dy

                    if 0 <= x < self._width and 0 <= y < self._height:
                        pos = Position(x, y)
                        if pos.distance_to(self._center) <= self._max_radius:
                            positions.append(pos)

                # Turn 90 degrees counter-clockwise
                dx, dy = -dy, dx

                if len(positions) >= self._width * self._height:
                    break

            steps += 1

        return positions

    def __iter__(self) -> Iterator[Position]:
        """Iterate in spiral order."""
        return iter(self._positions)

    def has_next(self) -> bool:
        """Check if more positions remain."""
        return self._index < len(self._positions)

    def next(self) -> Optional[Position]:
        """Get the next position in the spiral."""
        if not self.has_next():
            return None

        pos = self._positions[self._index]
        self._index += 1
        return pos

    def reset(self) -> None:
        """Reset to the center."""
        self._index = 0
