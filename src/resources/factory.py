"""
Factory Module - Factory Method Pattern for Resources

This module demonstrates the **Factory Method Pattern** by providing
an abstract factory interface for creating resources, with concrete
implementations for different resource creation strategies.

Design Patterns:
    - Factory Method Pattern: Defines interface for creation, lets subclasses decide

SOLID Principles:
    - Single Responsibility: Each factory creates one type of resource
    - Open/Closed: New factories can be added without modifying existing code
    - Dependency Inversion: Clients depend on abstract factory, not concrete creators
    - Liskov Substitution: All factories can be used interchangeably
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
import random

from resource import Resource, Food, Material, Water, ResourceType


class ResourceFactory(ABC):
    """
    Abstract base class for resource factories.

    The Factory Method pattern defines an interface for creating resources
    but lets subclasses decide which concrete resource class to instantiate.

    This promotes loose coupling by eliminating the need for client code
    to know about specific resource classes.
    """

    @abstractmethod
    def create_resource(
        self,
        position: tuple,
        amount: Optional[float] = None,
        **kwargs
    ) -> Resource:
        """
        Factory method for creating a resource.

        Args:
            position (tuple): Grid position for the resource
            amount (Optional[float]): Initial amount (if None, use default)
            **kwargs: Additional factory-specific parameters

        Returns:
            Resource: The created resource instance

        Note:
            Subclasses implement this method to create specific resource types.
        """
        pass

    @abstractmethod
    def get_resource_type(self) -> ResourceType:
        """
        Get the type of resource this factory creates.

        Returns:
            ResourceType: The resource type enum value
        """
        pass

    def can_create_at_position(self, position: tuple) -> bool:
        """
        Check if a resource can be created at the given position.

        Args:
            position (tuple): The grid position to check

        Returns:
            bool: True if resource can be created at position

        Note:
            Default implementation allows creation anywhere.
            Subclasses can override for position-specific constraints.
        """
        return True


class FoodFactory(ResourceFactory):
    """
    Factory for creating Food resources.

    This factory creates food resources with configurable amounts and
    regeneration rates based on the terrain or other environmental factors.

    Demonstrates the Factory Method pattern by providing a concrete
    implementation for food creation.
    """

    def __init__(
        self,
        default_amount: float = 100.0,
        default_max_amount: float = 100.0,
        default_regeneration_rate: float = 0.15
    ) -> None:
        """
        Initialize the food factory with default parameters.

        Args:
            default_amount (float): Default initial food amount
            default_max_amount (float): Default maximum capacity
            default_regeneration_rate (float): Default regeneration rate
        """
        self._default_amount = default_amount
        self._default_max_amount = default_max_amount
        self._default_regeneration_rate = default_regeneration_rate

    def create_resource(
        self,
        position: tuple,
        amount: Optional[float] = None,
        **kwargs
    ) -> Food:
        """
        Create a Food resource.

        Args:
            position (tuple): Grid position
            amount (Optional[float]): Initial amount (uses default if None)
            **kwargs: Optional parameters:
                - max_amount (float): Maximum capacity
                - regeneration_rate (float): Regeneration rate

        Returns:
            Food: A new food resource instance

        Examples:
            >>> factory = FoodFactory()
            >>> food = factory.create_resource((5, 10))
            >>> custom_food = factory.create_resource((3, 7), amount=150.0, regeneration_rate=0.2)
        """
        initial_amount = amount if amount is not None else self._default_amount
        max_amount = kwargs.get('max_amount', self._default_max_amount)
        regen_rate = kwargs.get('regeneration_rate', self._default_regeneration_rate)

        return Food(
            amount=initial_amount,
            max_amount=max_amount,
            position=position,
            regeneration_rate=regen_rate
        )

    def get_resource_type(self) -> ResourceType:
        """Get the resource type created by this factory."""
        return ResourceType.FOOD

    def can_create_at_position(self, position: tuple) -> bool:
        """
        Check if food can be created at position.

        Args:
            position (tuple): Grid position to check

        Returns:
            bool: True (food can be created anywhere)

        Note:
            In a more complex implementation, this might check terrain type.
        """
        return True


class MaterialFactory(ResourceFactory):
    """
    Factory for creating Material resources.

    This factory creates material resources with configurable amounts and
    quality levels. Materials might be more common in certain terrains
    (mountains, forests).

    Demonstrates the Factory Method pattern for material creation.
    """

    def __init__(
        self,
        default_amount: float = 150.0,
        default_max_amount: float = 150.0,
        default_quality: float = 1.0
    ) -> None:
        """
        Initialize the material factory with default parameters.

        Args:
            default_amount (float): Default initial material amount
            default_max_amount (float): Default maximum capacity
            default_quality (float): Default material quality (0.5-2.0)
        """
        self._default_amount = default_amount
        self._default_max_amount = default_max_amount
        self._default_quality = default_quality

    def create_resource(
        self,
        position: tuple,
        amount: Optional[float] = None,
        **kwargs
    ) -> Material:
        """
        Create a Material resource.

        Args:
            position (tuple): Grid position
            amount (Optional[float]): Initial amount (uses default if None)
            **kwargs: Optional parameters:
                - max_amount (float): Maximum capacity
                - material_quality (float): Quality multiplier (0.5-2.0)

        Returns:
            Material: A new material resource instance

        Examples:
            >>> factory = MaterialFactory()
            >>> material = factory.create_resource((8, 12))
            >>> quality_material = factory.create_resource((2, 4), material_quality=1.8)
        """
        initial_amount = amount if amount is not None else self._default_amount
        max_amount = kwargs.get('max_amount', self._default_max_amount)
        quality = kwargs.get('material_quality', self._default_quality)

        return Material(
            amount=initial_amount,
            max_amount=max_amount,
            position=position,
            material_quality=quality
        )

    def get_resource_type(self) -> ResourceType:
        """Get the resource type created by this factory."""
        return ResourceType.MATERIAL


class WaterFactory(ResourceFactory):
    """
    Factory for creating Water resources.

    This factory creates water resources with terrain-dependent regeneration
    rates. Water is more abundant near water terrain.

    Demonstrates the Factory Method pattern for water creation.
    """

    def __init__(
        self,
        default_amount: float = 80.0,
        default_max_amount: float = 80.0,
        default_base_regen: float = 0.2,
        default_terrain_multiplier: float = 1.0
    ) -> None:
        """
        Initialize the water factory with default parameters.

        Args:
            default_amount (float): Default initial water amount
            default_max_amount (float): Default maximum capacity
            default_base_regen (float): Default base regeneration rate
            default_terrain_multiplier (float): Default terrain modifier
        """
        self._default_amount = default_amount
        self._default_max_amount = default_max_amount
        self._default_base_regen = default_base_regen
        self._default_terrain_multiplier = default_terrain_multiplier

    def create_resource(
        self,
        position: tuple,
        amount: Optional[float] = None,
        **kwargs
    ) -> Water:
        """
        Create a Water resource.

        Args:
            position (tuple): Grid position
            amount (Optional[float]): Initial amount (uses default if None)
            **kwargs: Optional parameters:
                - max_amount (float): Maximum capacity
                - base_regeneration_rate (float): Base regeneration
                - terrain_multiplier (float): Terrain modifier

        Returns:
            Water: A new water resource instance

        Examples:
            >>> factory = WaterFactory()
            >>> water = factory.create_resource((15, 20))
            >>> lake_water = factory.create_resource((10, 10), terrain_multiplier=2.5)
        """
        initial_amount = amount if amount is not None else self._default_amount
        max_amount = kwargs.get('max_amount', self._default_max_amount)
        base_regen = kwargs.get('base_regeneration_rate', self._default_base_regen)
        terrain_mult = kwargs.get('terrain_multiplier', self._default_terrain_multiplier)

        return Water(
            amount=initial_amount,
            max_amount=max_amount,
            position=position,
            base_regeneration_rate=base_regen,
            terrain_multiplier=terrain_mult
        )

    def get_resource_type(self) -> ResourceType:
        """Get the resource type created by this factory."""
        return ResourceType.WATER


class RandomResourceFactory(ResourceFactory):
    """
    Factory that randomly creates different resource types.

    This factory demonstrates how the Factory Method pattern can be
    extended to create varied outputs while maintaining the same interface.

    Useful for procedural generation where resource types should be mixed.
    """

    def __init__(
        self,
        food_factory: FoodFactory,
        material_factory: MaterialFactory,
        water_factory: WaterFactory,
        weights: Optional[dict] = None
    ) -> None:
        """
        Initialize random resource factory with component factories.

        Args:
            food_factory (FoodFactory): Factory for creating food
            material_factory (MaterialFactory): Factory for creating materials
            water_factory (WaterFactory): Factory for creating water
            weights (Optional[dict]): Probability weights for each type
                                     e.g., {ResourceType.FOOD: 0.5, ...}

        Examples:
            >>> random_factory = RandomResourceFactory(
            ...     FoodFactory(),
            ...     MaterialFactory(),
            ...     WaterFactory(),
            ...     weights={ResourceType.FOOD: 0.5, ResourceType.MATERIAL: 0.3, ResourceType.WATER: 0.2}
            ... )
        """
        self._food_factory = food_factory
        self._material_factory = material_factory
        self._water_factory = water_factory

        # Default equal weights if not specified
        if weights is None:
            weights = {
                ResourceType.FOOD: 1.0,
                ResourceType.MATERIAL: 1.0,
                ResourceType.WATER: 1.0
            }
        self._weights = weights

    def create_resource(
        self,
        position: tuple,
        amount: Optional[float] = None,
        **kwargs
    ) -> Resource:
        """
        Create a random resource type.

        Args:
            position (tuple): Grid position
            amount (Optional[float]): Initial amount
            **kwargs: Additional parameters passed to specific factory

        Returns:
            Resource: A randomly selected resource type

        Examples:
            >>> factory = RandomResourceFactory(...)
            >>> resource = factory.create_resource((5, 5))  # Random type
        """
        # Choose resource type based on weights
        types = list(self._weights.keys())
        weights = list(self._weights.values())
        chosen_type = random.choices(types, weights=weights)[0]

        # Delegate to appropriate factory
        if chosen_type == ResourceType.FOOD:
            return self._food_factory.create_resource(position, amount, **kwargs)
        elif chosen_type == ResourceType.MATERIAL:
            return self._material_factory.create_resource(position, amount, **kwargs)
        else:  # ResourceType.WATER
            return self._water_factory.create_resource(position, amount, **kwargs)

    def get_resource_type(self) -> ResourceType:
        """
        Get resource type (not applicable for random factory).

        Returns:
            ResourceType: Returns FOOD as placeholder

        Note:
            Random factory creates mixed types, so this is somewhat arbitrary.
        """
        return ResourceType.FOOD  # Arbitrary choice for random factory


class FactoryRegistry:
    """
    Registry for managing resource factories.

    This class provides centralized access to different resource factories,
    demonstrating the Single Responsibility Principle through focused
    factory management.
    """

    def __init__(self) -> None:
        """Initialize the factory registry with default factories."""
        self._factories: dict[ResourceType, ResourceFactory] = {
            ResourceType.FOOD: FoodFactory(),
            ResourceType.MATERIAL: MaterialFactory(),
            ResourceType.WATER: WaterFactory()
        }

    def get_factory(self, resource_type: ResourceType) -> Optional[ResourceFactory]:
        """
        Get a factory for a specific resource type.

        Args:
            resource_type (ResourceType): The type of resource

        Returns:
            Optional[ResourceFactory]: The factory, or None if not found
        """
        return self._factories.get(resource_type)

    def register_factory(self, resource_type: ResourceType, factory: ResourceFactory) -> None:
        """
        Register or replace a factory for a resource type.

        Args:
            resource_type (ResourceType): The resource type
            factory (ResourceFactory): The factory to register
        """
        self._factories[resource_type] = factory

    def create_resource(
        self,
        resource_type: ResourceType,
        position: tuple,
        amount: Optional[float] = None,
        **kwargs
    ) -> Optional[Resource]:
        """
        Create a resource using the appropriate factory.

        Args:
            resource_type (ResourceType): Type of resource to create
            position (tuple): Grid position
            amount (Optional[float]): Initial amount
            **kwargs: Additional parameters

        Returns:
            Optional[Resource]: The created resource, or None if factory not found
        """
        factory = self.get_factory(resource_type)
        if factory:
            return factory.create_resource(position, amount, **kwargs)
        return None
