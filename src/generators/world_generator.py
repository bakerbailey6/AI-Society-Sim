"""
World Generator Module - Abstract Generator and Concrete Implementations

This module provides abstract and concrete world generators,
demonstrating template method and factory method patterns.

Design Patterns:
    - Template Method (implicit in abstract generate method)
    - Factory Method (generate method creates world)

SOLID Principles:
    - Single Responsibility: Generates world only
    - Open/Closed: New generators can be added without modification
    - Liskov Substitution: All generators are interchangeable
"""

from __future__ import annotations
from abc import ABC, abstractmethod
import random

from config import WorldConfig
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from world.world import World, EagerWorld
from world.position import Position
from world.cell import StandardCell, BlockedCell
from world.terrain import TerrainTypeEnum
from resources.factory import FactoryRegistry
from resources.resource import ResourceType


class WorldGenerator(ABC):
    """
    Abstract base class for world generators.

    Generators create and populate World instances according to
    specific strategies and configurations.

    This demonstrates the Factory Method pattern - subclasses
    decide how to generate the world.
    """

    def __init__(self, config: WorldConfig) -> None:
        """
        Initialize the generator with configuration.

        Args:
            config (WorldConfig): Immutable world configuration
        """
        self._config: WorldConfig = config
        if config.seed is not None:
            random.seed(config.seed)

    @property
    def config(self) -> WorldConfig:
        """Get the configuration (immutable)."""
        return self._config

    @abstractmethod
    def generate(self) -> World:
        """
        Generate a world instance.

        Returns:
            World: The generated world

        Note:
            Subclasses implement specific generation algorithms.
        """
        pass

    def _create_world_instance(self) -> World:
        """
        Create an empty world instance.

        Returns:
            World: Empty world with configured dimensions
        """
        return EagerWorld(self._config.width, self._config.height)

    def _should_place_resource(self) -> bool:
        """
        Determine if a resource should be placed (based on density).

        Returns:
            bool: True if resource should be placed
        """
        return random.random() < self._config.resource_density


class RandomWorldGenerator(WorldGenerator):
    """
    Generator that creates worlds with random terrain and resources.

    Resources and terrain are distributed randomly across the grid
    according to the configuration probabilities.
    """

    def generate(self) -> World:
        """
        Generate a world with random distribution.

        Returns:
            World: Generated world
        """
        world = self._create_world_instance()
        resource_factory = FactoryRegistry()

        # Generate terrain and populate cells
        for x in range(self._config.width):
            for y in range(self._config.height):
                pos = Position(x, y)

                # Choose terrain type based on distribution
                terrain_type = self._choose_terrain_type()

                # Create cell based on terrain
                if terrain_type == TerrainTypeEnum.WATER:
                    cell = BlockedCell(pos, terrain_type)
                else:
                    cell = StandardCell(pos, terrain_type, max_resources=5)

                # Add resources randomly
                if self._should_place_resource() and terrain_type != TerrainTypeEnum.WATER:
                    resource_type = random.choice(list(ResourceType))
                    resource = resource_factory.create_resource(
                        resource_type,
                        pos.to_tuple()
                    )
                    if resource:
                        cell.add_resource(resource)

                world.set_cell(pos, cell)

        return world

    def _choose_terrain_type(self) -> TerrainTypeEnum:
        """
        Choose a terrain type based on configuration distribution.

        Returns:
            TerrainTypeEnum: Chosen terrain type
        """
        terrain_map = {
            'plains': TerrainTypeEnum.PLAINS,
            'forest': TerrainTypeEnum.FOREST,
            'mountain': TerrainTypeEnum.MOUNTAIN,
            'water': TerrainTypeEnum.WATER
        }

        dist = self._config.terrain_distribution
        terrain_names = list(dist.keys())
        weights = list(dist.values())

        chosen = random.choices(terrain_names, weights=weights)[0]
        return terrain_map.get(chosen, TerrainTypeEnum.PLAINS)


class ClusteredWorldGenerator(WorldGenerator):
    """
    Generator that creates worlds with clustered resources.

    Resources appear in clusters rather than being uniformly distributed,
    creating more realistic and interesting resource distributions.
    """

    def __init__(self, config: WorldConfig, cluster_size: int = 5) -> None:
        """
        Initialize clustered generator.

        Args:
            config (WorldConfig): World configuration
            cluster_size (int): Radius of resource clusters
        """
        super().__init__(config)
        self._cluster_size: int = cluster_size

    def generate(self) -> World:
        """
        Generate a world with clustered resources.

        Returns:
            World: Generated world
        """
        world = self._create_world_instance()
        resource_factory = FactoryRegistry()

        # First pass: generate terrain
        for x in range(self._config.width):
            for y in range(self._config.height):
                pos = Position(x, y)
                terrain_type = self._choose_terrain_type()

                if terrain_type == TerrainTypeEnum.WATER:
                    cell = BlockedCell(pos, terrain_type)
                else:
                    cell = StandardCell(pos, terrain_type, max_resources=5)

                world.set_cell(pos, cell)

        # Second pass: place clustered resources
        num_clusters = int(
            self._config.width * self._config.height * self._config.resource_density / (self._cluster_size ** 2)
        )

        for _ in range(num_clusters):
            self._place_resource_cluster(world, resource_factory)

        return world

    def _place_resource_cluster(self, world: World, factory: FactoryRegistry) -> None:
        """
        Place a cluster of resources in the world.

        Args:
            world (World): The world to modify
            factory (FactoryRegistry): Factory for creating resources
        """
        # Choose random center for cluster
        center_x = random.randint(0, self._config.width - 1)
        center_y = random.randint(0, self._config.height - 1)
        center = Position(center_x, center_y)

        # Choose resource type for this cluster
        resource_type = random.choice(list(ResourceType))

        # Place resources in cluster radius
        for dx in range(-self._cluster_size, self._cluster_size + 1):
            for dy in range(-self._cluster_size, self._cluster_size + 1):
                x = center_x + dx
                y = center_y + dy

                # Check bounds
                if not (0 <= x < self._config.width and 0 <= y < self._config.height):
                    continue

                # Check if within cluster radius
                dist = abs(dx) + abs(dy)
                if dist > self._cluster_size:
                    continue

                pos = Position(x, y)
                cell = world.get_cell(pos)

                if cell and cell.is_traversable():
                    resource = factory.create_resource(resource_type, pos.to_tuple())
                    if resource:
                        cell.add_resource(resource)

    def _choose_terrain_type(self) -> TerrainTypeEnum:
        """Choose terrain type based on distribution."""
        terrain_map = {
            'plains': TerrainTypeEnum.PLAINS,
            'forest': TerrainTypeEnum.FOREST,
            'mountain': TerrainTypeEnum.MOUNTAIN,
            'water': TerrainTypeEnum.WATER
        }

        dist = self._config.terrain_distribution
        terrain_names = list(dist.keys())
        weights = list(dist.values())

        chosen = random.choices(terrain_names, weights=weights)[0]
        return terrain_map.get(chosen, TerrainTypeEnum.PLAINS)
