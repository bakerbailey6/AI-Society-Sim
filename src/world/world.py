"""
World Module - Singleton Pattern for World Management

This module demonstrates the **Singleton Pattern** by ensuring only one
World instance exists throughout the simulation.

Design Patterns:
    - Singleton Pattern: Ensures single instance of World

SOLID Principles:
    - Single Responsibility: Manages only world state and grid
    - Open/Closed: Can be extended without modification
    - Dependency Inversion: Depends on abstractions (Cell, Resource)
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List, Dict
from threading import Lock

from position import Position
from cell import Cell
from iterators import GridIterator, AllCellsIterator
from events import WorldEvent, TimeStepEvent, EventLogger


class SingletonMeta(type):
    """
    Metaclass for implementing the Singleton pattern.

    This metaclass ensures that only one instance of a class can exist.
    Thread-safe implementation using double-checked locking.

    Note:
        This is the recommended way to implement Singleton in Python,
        as it works correctly with inheritance and is thread-safe.
    """

    _instances: Dict[type, object] = {}
    _lock: Lock = Lock()

    def __call__(cls, *args, **kwargs):
        """
        Control instance creation to ensure singleton behavior.

        Returns:
            object: The single instance of the class
        """
        # Double-checked locking for thread safety
        if cls not in cls._instances:
            with cls._lock:
                if cls not in cls._instances:
                    instance = super().__call__(*args, **kwargs)
                    cls._instances[cls] = instance
        return cls._instances[cls]


class World(ABC, metaclass=SingletonMeta):
    """
    Abstract base class for the world (Singleton).

    The World class represents the entire simulation environment,
    managing the grid of cells, time progression, and global state.

    Only one World instance can exist at a time, enforced by the
    Singleton pattern through the SingletonMeta metaclass.

    Attributes:
        width (int): Width of the world grid
        height (int): Height of the world grid
        current_time (int): Current simulation time step
        _grid (Dict): Grid storage (implementation-dependent)
        _event_logger (EventLogger): Logger for world events
    """

    _initialized: bool = False  # Track initialization to prevent re-init

    def __init__(self, width: int, height: int) -> None:
        """
        Initialize the world (called only once due to Singleton).

        Args:
            width (int): Grid width
            height (int): Grid height

        Note:
            Due to Singleton pattern, this is only called once.
            Subsequent calls to World() return the same instance.

        Examples:
            >>> world1 = ConcreteWorld(100, 100)
            >>> world2 = ConcreteWorld(50, 50)  # Returns world1, ignores parameters
            >>> assert world1 is world2  # Same instance
        """
        # Only initialize once
        if not World._initialized:
            if width <= 0 or height <= 0:
                raise ValueError("World dimensions must be positive")

            self._width: int = width
            self._height: int = height
            self._current_time: int = 0
            self._grid: Dict[tuple, Cell] = {}
            self._event_logger: EventLogger = EventLogger()
            World._initialized = True

    @property
    def width(self) -> int:
        """Get the world width."""
        return self._width

    @property
    def height(self) -> int:
        """Get the world height."""
        return self._height

    @property
    def current_time(self) -> int:
        """Get the current simulation time step."""
        return self._current_time

    @property
    def event_logger(self) -> EventLogger:
        """Get the event logger."""
        return self._event_logger

    @abstractmethod
    def get_cell(self, position: Position) -> Optional[Cell]:
        """
        Get a cell at the given position.

        Args:
            position (Position): The grid position

        Returns:
            Optional[Cell]: The cell, or None if out of bounds

        Note:
            Subclasses implement specific cell retrieval (eager vs lazy loading).
        """
        pass

    @abstractmethod
    def set_cell(self, position: Position, cell: Cell) -> bool:
        """
        Set a cell at the given position.

        Args:
            position (Position): The grid position
            cell (Cell): The cell to place

        Returns:
            bool: True if set successfully, False if out of bounds

        Note:
            Subclasses implement specific cell storage strategies.
        """
        pass

    @abstractmethod
    def update(self) -> None:
        """
        Update the world for one time step.

        This method advances the simulation by one time step, updating
        all cells, resources, and agents.

        Note:
            Subclasses define specific update behavior.
        """
        pass

    def advance_time(self) -> None:
        """
        Advance the simulation time by one step.

        This is called by update() implementations and logs a time step event.
        """
        self._current_time += 1

        # Log time step event
        event = TimeStepEvent(
            timestamp=self._current_time,
            event_type="time_step",
            description=f"Advanced to time step {self._current_time}",
            step_number=self._current_time,
            total_agents=0,  # Would be populated by simulation
            total_resources=self._count_resources()
        )
        self._event_logger.log_event(event)

    def _count_resources(self) -> int:
        """
        Count total resources in the world.

        Returns:
            int: Total number of resources
        """
        count = 0
        iterator = self.get_all_cells_iterator()
        for pos in iterator:
            cell = self.get_cell(pos)
            if cell:
                count += cell.resource_count()
        return count

    def is_valid_position(self, position: Position) -> bool:
        """
        Check if a position is within world bounds.

        Args:
            position (Position): The position to check

        Returns:
            bool: True if within bounds
        """
        return position.is_within_bounds(self._width, self._height)

    def get_all_cells_iterator(self) -> GridIterator:
        """
        Get an iterator for all cells in the world.

        Returns:
            GridIterator: Iterator over all positions

        Examples:
            >>> world = ConcreteWorld(10, 10)
            >>> for pos in world.get_all_cells_iterator():
            ...     cell = world.get_cell(pos)
            ...     # Process cell
        """
        return AllCellsIterator(self._width, self._height)

    def log_event(self, event: WorldEvent) -> None:
        """
        Log an event to the world event logger.

        Args:
            event (WorldEvent): The event to log
        """
        self._event_logger.log_event(event)

    def get_events(
        self,
        event_type: Optional[str] = None,
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> List[WorldEvent]:
        """
        Retrieve logged events matching criteria.

        Args:
            event_type (Optional[str]): Filter by event type
            start_time (Optional[int]): Minimum timestamp
            end_time (Optional[int]): Maximum timestamp

        Returns:
            List[WorldEvent]: Matching events
        """
        return self._event_logger.get_events(event_type, start_time, end_time)

    @classmethod
    def reset_singleton(cls) -> None:
        """
        Reset the singleton instance (useful for testing).

        Warning:
            This should only be used in testing. In production,
            there should be no need to reset the singleton.

        Examples:
            >>> World.reset_singleton()
            >>> world = ConcreteWorld(50, 50)  # Creates new instance
        """
        if cls in SingletonMeta._instances:
            del SingletonMeta._instances[cls]
        World._initialized = False

    def __str__(self) -> str:
        """String representation of the world."""
        return f"World({self._width}x{self._height}, t={self._current_time})"

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return f"{self.__class__.__name__}(width={self._width}, height={self._height})"


class EagerWorld(World):
    """
    Concrete World implementation with eager cell loading.

    All cells are created and stored in memory immediately when the
    world is initialized. This is simpler but uses more memory.

    Best for small to medium-sized worlds.
    """

    def __init__(self, width: int, height: int) -> None:
        """
        Initialize an eager-loading world.

        Args:
            width (int): Grid width
            height (int): Grid height
        """
        super().__init__(width, height)

    def get_cell(self, position: Position) -> Optional[Cell]:
        """
        Get a cell at the position.

        Args:
            position (Position): Grid position

        Returns:
            Optional[Cell]: The cell, or None if not exists/out of bounds
        """
        if not self.is_valid_position(position):
            return None
        return self._grid.get(position.to_tuple())

    def set_cell(self, position: Position, cell: Cell) -> bool:
        """
        Set a cell at the position.

        Args:
            position (Position): Grid position
            cell (Cell): The cell to place

        Returns:
            bool: True if set successfully
        """
        if not self.is_valid_position(position):
            return False

        self._grid[position.to_tuple()] = cell
        return True

    def update(self) -> None:
        """
        Update the world for one time step.

        Updates all cells and advances time.
        """
        # Update each cell (e.g., regenerate resources)
        for pos in self.get_all_cells_iterator():
            cell = self.get_cell(pos)
            if cell:
                # Update cell resources (regeneration, etc.)
                for resource in cell.resources:
                    if hasattr(resource, 'regenerate'):
                        resource.regenerate()

        self.advance_time()


class LazyWorld(World):
    """
    Concrete World implementation with lazy cell loading.

    Cells are created on-demand when accessed, using proxies for
    unaccessed cells. This saves memory for large worlds.

    Best for very large worlds where not all cells are accessed.
    """

    def __init__(self, width: int, height: int) -> None:
        """
        Initialize a lazy-loading world.

        Args:
            width (int): Grid width
            height (int): Grid height
        """
        super().__init__(width, height)

    def get_cell(self, position: Position) -> Optional[Cell]:
        """
        Get a cell, creating it lazily if needed.

        Args:
            position (Position): Grid position

        Returns:
            Optional[Cell]: The cell, or None if out of bounds
        """
        if not self.is_valid_position(position):
            return None

        # Cell would be loaded via proxy here
        # For abstract implementation, return from grid if exists
        return self._grid.get(position.to_tuple())

    def set_cell(self, position: Position, cell: Cell) -> bool:
        """Set a cell at the position."""
        if not self.is_valid_position(position):
            return False

        self._grid[position.to_tuple()] = cell
        return True

    def update(self) -> None:
        """Update the world (only loaded cells)."""
        # Only update cells that have been loaded
        for cell in self._grid.values():
            for resource in cell.resources:
                if hasattr(resource, 'regenerate'):
                    resource.regenerate()

        self.advance_time()
