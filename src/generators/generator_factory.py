"""
Generator Factory Module - Abstract Factory Pattern

This module demonstrates the **Abstract Factory Pattern** by providing
factories that create families of related objects (world generators).

Design Patterns:
    - Abstract Factory Pattern: Creates families of related objects

SOLID Principles:
    - Single Responsibility: Creates only world generators
    - Open/Closed: New factories can be added without modification
    - Dependency Inversion: Depends on abstract WorldGenerator
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Type

from config import WorldConfig, create_small_world_config, create_medium_world_config, create_large_world_config
from world_generator import WorldGenerator, RandomWorldGenerator, ClusteredWorldGenerator


class GeneratorFactory(ABC):
    """
    Abstract factory for creating world generators.

    The Abstract Factory pattern provides an interface for creating
    families of related objects without specifying concrete classes.

    This allows clients to create generators without knowing the
    specific generator class.
    """

    @abstractmethod
    def create_generator(self, config: WorldConfig) -> WorldGenerator:
        """
        Create a world generator.

        Args:
            config (WorldConfig): Configuration for the generator

        Returns:
            WorldGenerator: The created generator

        Note:
            Subclasses return specific generator types.
        """
        pass

    @abstractmethod
    def get_factory_type(self) -> str:
        """
        Get the type of factory.

        Returns:
            str: Factory type identifier
        """
        pass


class RandomGeneratorFactory(GeneratorFactory):
    """
    Factory for creating random world generators.

    Creates generators that distribute terrain and resources randomly.
    """

    def create_generator(self, config: WorldConfig) -> WorldGenerator:
        """
        Create a random world generator.

        Args:
            config (WorldConfig): World configuration

        Returns:
            RandomWorldGenerator: Generator with random distribution
        """
        return RandomWorldGenerator(config)

    def get_factory_type(self) -> str:
        """Get factory type."""
        return "random"


class ClusteredGeneratorFactory(GeneratorFactory):
    """
    Factory for creating clustered world generators.

    Creates generators that place resources in clusters for more
    interesting and realistic distributions.

    Attributes:
        default_cluster_size (int): Default cluster radius
    """

    def __init__(self, default_cluster_size: int = 5) -> None:
        """
        Initialize the clustered generator factory.

        Args:
            default_cluster_size (int): Default cluster radius
        """
        self._default_cluster_size: int = default_cluster_size

    def create_generator(self, config: WorldConfig) -> WorldGenerator:
        """
        Create a clustered world generator.

        Args:
            config (WorldConfig): World configuration

        Returns:
            ClusteredWorldGenerator: Generator with clustered distribution
        """
        return ClusteredWorldGenerator(config, self._default_cluster_size)

    def get_factory_type(self) -> str:
        """Get factory type."""
        return "clustered"


class GeneratorFactoryRegistry:
    """
    Registry for managing generator factories.

    This provides centralized access to different generator factories,
    allowing selection by name rather than explicit instantiation.

    Demonstrates Single Responsibility through focused factory management.
    """

    def __init__(self) -> None:
        """Initialize registry with default factories."""
        self._factories: Dict[str, GeneratorFactory] = {
            'random': RandomGeneratorFactory(),
            'clustered': ClusteredGeneratorFactory()
        }

    def register_factory(self, name: str, factory: GeneratorFactory) -> None:
        """
        Register a generator factory.

        Args:
            name (str): Factory identifier
            factory (GeneratorFactory): The factory to register

        Examples:
            >>> registry = GeneratorFactoryRegistry()
            >>> registry.register_factory('custom', CustomGeneratorFactory())
        """
        self._factories[name] = factory

    def get_factory(self, name: str) -> GeneratorFactory:
        """
        Get a factory by name.

        Args:
            name (str): Factory identifier

        Returns:
            GeneratorFactory: The requested factory

        Raises:
            KeyError: If factory name not found
        """
        if name not in self._factories:
            raise KeyError(f"Generator factory '{name}' not found")
        return self._factories[name]

    def create_generator(
        self,
        factory_name: str,
        config: WorldConfig
    ) -> WorldGenerator:
        """
        Create a generator using a named factory.

        Args:
            factory_name (str): Name of the factory to use
            config (WorldConfig): World configuration

        Returns:
            WorldGenerator: The created generator

        Examples:
            >>> registry = GeneratorFactoryRegistry()
            >>> config = create_medium_world_config(seed=42)
            >>> generator = registry.create_generator('clustered', config)
            >>> world = generator.generate()
        """
        factory = self.get_factory(factory_name)
        return factory.create_generator(config)

    def list_factories(self) -> list[str]:
        """
        Get list of registered factory names.

        Returns:
            list[str]: Names of available factories
        """
        return list(self._factories.keys())


def create_default_world(
    size: str = 'medium',
    generator_type: str = 'random',
    seed: int = None
):
    """
    Convenience function to create a world with default settings.

    Args:
        size (str): World size ('small', 'medium', or 'large')
        generator_type (str): Generator type ('random' or 'clustered')
        seed (int): Random seed for reproducibility

    Returns:
        World: The generated world

    Examples:
        >>> world = create_default_world(size='medium', generator_type='clustered', seed=42)
    """
    # Get configuration
    config_factories = {
        'small': create_small_world_config,
        'medium': create_medium_world_config,
        'large': create_large_world_config
    }

    if size not in config_factories:
        raise ValueError(f"Unknown size '{size}'. Use 'small', 'medium', or 'large'")

    config = config_factories[size](seed=seed)

    # Create generator and generate world
    registry = GeneratorFactoryRegistry()
    generator = registry.create_generator(generator_type, config)
    return generator.generate()
