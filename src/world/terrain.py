"""
Terrain Module - Immutable Terrain Type System

This module demonstrates the **Immutable Pattern** for terrain data.
TerrainType objects are immutable and shared, ensuring consistent
behavior across the simulation.

Design Patterns:
    - Immutable Pattern: TerrainProperties cannot be modified after creation

SOLID Principles:
    - Single Responsibility: Manages only terrain type information
    - Open/Closed: New terrain types can be added without modifying existing code
    - Dependency Inversion: Depends on abstract enum, not concrete implementations
"""

from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Dict


class TerrainTypeEnum(Enum):
    """
    Enumeration of all terrain types in the world.

    Each terrain type has different properties affecting resource
    generation, movement speed, and agent behavior.

    Attributes:
        PLAINS: Open grassland, easy traversal, moderate resources
        FOREST: Dense woods, slower movement, high food resources
        MOUNTAIN: Rocky terrain, difficult traversal, high material resources
        WATER: Lakes and rivers, blocks most movement, water resource source
        DESERT: Arid land, harsh conditions, scarce resources
    """

    PLAINS = "plains"
    FOREST = "forest"
    MOUNTAIN = "mountain"
    WATER = "water"
    DESERT = "desert"


@dataclass(frozen=True)
class TerrainProperties:
    """
    Immutable properties associated with a terrain type.

    The frozen=True parameter ensures these properties cannot be
    modified after creation, maintaining consistency across the simulation.

    Attributes:
        terrain_type (TerrainTypeEnum): The type of terrain
        movement_cost (float): Movement cost multiplier (1.0 = normal, >1.0 = slower)
        traversable (bool): Whether agents can move through this terrain
        resource_fertility (float): Multiplier for resource generation (0.0-2.0)
        description (str): Human-readable description of the terrain

    Examples:
        >>> props = TerrainProperties(
        ...     terrain_type=TerrainTypeEnum.FOREST,
        ...     movement_cost=1.5,
        ...     traversable=True,
        ...     resource_fertility=1.8,
        ...     description="Dense forest with abundant resources"
        ... )
    """

    terrain_type: TerrainTypeEnum
    movement_cost: float
    traversable: bool
    resource_fertility: float
    description: str

    def __post_init__(self) -> None:
        """
        Validate terrain properties after initialization.

        Raises:
            ValueError: If properties are outside valid ranges
        """
        if self.movement_cost < 0:
            raise ValueError("Movement cost cannot be negative")
        if not 0.0 <= self.resource_fertility <= 2.0:
            raise ValueError("Resource fertility must be between 0.0 and 2.0")


class TerrainFactory:
    """
    Factory for creating and caching immutable TerrainProperties.

    This class ensures that only one instance of each terrain type's
    properties exists, supporting the immutable pattern through caching.

    The factory pattern allows centralized creation of terrain properties
    while maintaining immutability guarantees.
    """

    # Class-level cache of terrain properties (shared across all instances)
    _terrain_cache: Dict[TerrainTypeEnum, TerrainProperties] = {}

    @classmethod
    def _initialize_defaults(cls) -> None:
        """
        Initialize default terrain properties for all terrain types.

        This method is called once to populate the cache with standard
        terrain configurations. These can be accessed but never modified.
        """
        if cls._terrain_cache:
            return  # Already initialized

        cls._terrain_cache = {
            TerrainTypeEnum.PLAINS: TerrainProperties(
                terrain_type=TerrainTypeEnum.PLAINS,
                movement_cost=1.0,
                traversable=True,
                resource_fertility=1.0,
                description="Open grassland with moderate resources and easy movement"
            ),
            TerrainTypeEnum.FOREST: TerrainProperties(
                terrain_type=TerrainTypeEnum.FOREST,
                movement_cost=1.5,
                traversable=True,
                resource_fertility=1.8,
                description="Dense woodland with abundant food but slower movement"
            ),
            TerrainTypeEnum.MOUNTAIN: TerrainProperties(
                terrain_type=TerrainTypeEnum.MOUNTAIN,
                movement_cost=2.5,
                traversable=True,
                resource_fertility=0.5,
                description="Rocky highlands rich in materials but difficult to traverse"
            ),
            TerrainTypeEnum.WATER: TerrainProperties(
                terrain_type=TerrainTypeEnum.WATER,
                movement_cost=float('inf'),
                traversable=False,
                resource_fertility=1.2,
                description="Rivers and lakes providing water but blocking passage"
            ),
            TerrainTypeEnum.DESERT: TerrainProperties(
                terrain_type=TerrainTypeEnum.DESERT,
                movement_cost=2.0,
                traversable=True,
                resource_fertility=0.3,
                description="Arid wasteland with scarce resources and harsh conditions"
            ),
        }

    @classmethod
    def get_properties(cls, terrain_type: TerrainTypeEnum) -> TerrainProperties:
        """
        Get the immutable properties for a given terrain type.

        This method implements lazy initialization and caching to ensure
        only one instance of each TerrainProperties exists.

        Args:
            terrain_type (TerrainTypeEnum): The terrain type to look up

        Returns:
            TerrainProperties: Immutable properties for the terrain type

        Examples:
            >>> props = TerrainFactory.get_properties(TerrainTypeEnum.FOREST)
            >>> print(props.movement_cost)
            1.5
        """
        cls._initialize_defaults()
        return cls._terrain_cache[terrain_type]

    @classmethod
    def register_custom_terrain(
        cls,
        terrain_type: TerrainTypeEnum,
        properties: TerrainProperties
    ) -> None:
        """
        Register custom terrain properties.

        Allows extension of terrain types without modifying existing code,
        demonstrating the Open/Closed Principle.

        Args:
            terrain_type (TerrainTypeEnum): The terrain type to register
            properties (TerrainProperties): The immutable properties to associate

        Raises:
            ValueError: If terrain type already exists in cache

        Note:
            This should only be called during initialization. Once the
            simulation starts, terrain properties should not change.
        """
        cls._initialize_defaults()
        if terrain_type in cls._terrain_cache:
            raise ValueError(f"Terrain type {terrain_type} already registered")
        cls._terrain_cache[terrain_type] = properties

    @classmethod
    def get_all_terrain_types(cls) -> Dict[TerrainTypeEnum, TerrainProperties]:
        """
        Get all registered terrain types and their properties.

        Returns:
            Dict[TerrainTypeEnum, TerrainProperties]: Mapping of all terrain types
        """
        cls._initialize_defaults()
        return cls._terrain_cache.copy()
