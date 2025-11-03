"""
Config Module - Immutable World Configuration

This module provides immutable configuration objects for world generation,
demonstrating the Immutable Pattern.

Design Patterns:
    - Immutable Pattern: Configuration cannot be modified after creation

SOLID Principles:
    - Single Responsibility: Manages only configuration data
    - Open/Closed: New configuration fields can be added via subclassing
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass(frozen=True)
class WorldConfig:
    """
    Immutable configuration for world generation.

    The frozen=True parameter ensures this configuration cannot be
    modified after creation, preventing accidental changes that could
    lead to inconsistent world generation.

    Attributes:
        width (int): World grid width
        height (int): World grid height
        resource_density (float): Resource generation density (0.0-1.0)
        seed (Optional[int]): Random seed for reproducible generation
        terrain_distribution (Dict[str, float]): Terrain type probabilities
    """

    width: int
    height: int
    resource_density: float = 0.3
    seed: Optional[int] = None
    terrain_distribution: Optional[Dict[str, float]] = None

    def __post_init__(self) -> None:
        """
        Validate configuration after initialization.

        Raises:
            ValueError: If configuration values are invalid
        """
        if self.width <= 0 or self.height <= 0:
            raise ValueError("World dimensions must be positive")

        if not 0.0 <= self.resource_density <= 1.0:
            raise ValueError("Resource density must be between 0.0 and 1.0")

        # Set default terrain distribution if not provided
        if self.terrain_distribution is None:
            object.__setattr__(self, 'terrain_distribution', {
                'plains': 0.4,
                'forest': 0.3,
                'mountain': 0.2,
                'water': 0.1
            })

    def with_width(self, width: int) -> WorldConfig:
        """
        Create a new config with different width.

        Args:
            width (int): New width

        Returns:
            WorldConfig: New configuration instance

        Note:
            Since config is immutable, this creates a new instance.

        Examples:
            >>> config = WorldConfig(100, 100)
            >>> new_config = config.with_width(200)
        """
        return WorldConfig(
            width=width,
            height=self.height,
            resource_density=self.resource_density,
            seed=self.seed,
            terrain_distribution=self.terrain_distribution
        )

    def with_height(self, height: int) -> WorldConfig:
        """Create a new config with different height."""
        return WorldConfig(
            width=self.width,
            height=height,
            resource_density=self.resource_density,
            seed=self.seed,
            terrain_distribution=self.terrain_distribution
        )

    def with_resource_density(self, density: float) -> WorldConfig:
        """Create a new config with different resource density."""
        return WorldConfig(
            width=self.width,
            height=self.height,
            resource_density=density,
            seed=self.seed,
            terrain_distribution=self.terrain_distribution
        )

    def with_seed(self, seed: int) -> WorldConfig:
        """Create a new config with different random seed."""
        return WorldConfig(
            width=self.width,
            height=self.height,
            resource_density=self.resource_density,
            seed=seed,
            terrain_distribution=self.terrain_distribution
        )


def create_small_world_config(seed: Optional[int] = None) -> WorldConfig:
    """
    Factory function for small world configuration.

    Args:
        seed (Optional[int]): Random seed

    Returns:
        WorldConfig: Configuration for a small world (50x50)

    Examples:
        >>> config = create_small_world_config(seed=42)
    """
    return WorldConfig(
        width=50,
        height=50,
        resource_density=0.4,
        seed=seed
    )


def create_medium_world_config(seed: Optional[int] = None) -> WorldConfig:
    """
    Factory function for medium world configuration.

    Args:
        seed (Optional[int]): Random seed

    Returns:
        WorldConfig: Configuration for a medium world (100x100)
    """
    return WorldConfig(
        width=100,
        height=100,
        resource_density=0.3,
        seed=seed
    )


def create_large_world_config(seed: Optional[int] = None) -> WorldConfig:
    """
    Factory function for large world configuration.

    Args:
        seed (Optional[int]): Random seed

    Returns:
        WorldConfig: Configuration for a large world (200x200)
    """
    return WorldConfig(
        width=200,
        height=200,
        resource_density=0.2,
        seed=seed
    )
