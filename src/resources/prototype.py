"""
Prototype Module - Prototype Pattern for Resources

This module demonstrates the **Prototype Pattern** by allowing resource
objects to be cloned from template instances rather than created from scratch.

Design Patterns:
    - Prototype Pattern: Cloning objects from prototypes

SOLID Principles:
    - Single Responsibility: Focuses solely on resource cloning
    - Open/Closed: New prototype types can be added without modification
    - Dependency Inversion: Depends on abstract Resource, not concrete types
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Dict, Optional
import copy

from resources.resource import Resource, Food, Material, Water, ResourceType


class IPrototype(ABC):
    """
    Interface for objects that can be cloned.

    The Prototype pattern allows objects to be copied without depending
    on their concrete classes, promoting loose coupling.

    This interface defines the contract for cloneable objects.
    """

    @abstractmethod
    def clone(self) -> IPrototype:
        """
        Create a deep copy of this object.

        Returns:
            IPrototype: A new instance with copied state

        Note:
            Cloned objects should be independent - modifying the clone
            should not affect the original.
        """
        pass


class ResourcePrototype(IPrototype):
    """
    Prototype wrapper for Resource objects.

    This class wraps a Resource and provides cloning functionality,
    allowing resource templates to be defined once and cloned many times.

    This is particularly useful for:
    - Creating multiple similar resources efficiently
    - Defining resource templates in configuration
    - Avoiding repeated initialization logic

    Attributes:
        _template (Resource): The template resource to clone from
        _name (str): Identifier for this prototype template
    """

    def __init__(self, name: str, template: Resource) -> None:
        """
        Initialize a resource prototype.

        Args:
            name (str): Identifier for this prototype
            template (Resource): The resource to use as a template

        Examples:
            >>> food_template = Food(100.0, 100.0, (0, 0), regeneration_rate=0.2)
            >>> food_proto = ResourcePrototype("standard_food", food_template)
        """
        self._name: str = name
        self._template: Resource = template

    @property
    def name(self) -> str:
        """Get the prototype name."""
        return self._name

    @property
    def template(self) -> Resource:
        """Get the template resource (read-only)."""
        return self._template

    def clone(self) -> Resource:
        """
        Create a deep copy of the template resource.

        Returns:
            Resource: A new resource instance cloned from the template

        Note:
            Uses Python's copy.deepcopy to ensure complete independence
            between the clone and the original.

        Examples:
            >>> proto = ResourcePrototype("food", food_template)
            >>> resource1 = proto.clone()
            >>> resource2 = proto.clone()
            >>> # resource1 and resource2 are independent instances
        """
        return copy.deepcopy(self._template)

    def clone_at_position(self, position: tuple) -> Resource:
        """
        Create a clone with a different position.

        Args:
            position (tuple): The (x, y) position for the cloned resource

        Returns:
            Resource: A new resource at the specified position

        Note:
            This is a convenience method that clones the resource and
            updates its position in one operation.

        Examples:
            >>> proto = ResourcePrototype("water", water_template)
            >>> resource = proto.clone_at_position((5, 10))
        """
        cloned = self.clone()
        # Update the position (accessing private attribute for cloning)
        cloned._position = position
        return cloned

    def clone_with_amount(self, amount: float, position: tuple) -> Resource:
        """
        Create a clone with specified amount and position.

        Args:
            amount (float): Initial amount for the cloned resource
            position (tuple): Grid position for the cloned resource

        Returns:
            Resource: A new resource with custom amount and position

        Raises:
            ValueError: If amount exceeds the template's max_amount

        Examples:
            >>> proto = ResourcePrototype("material", material_template)
            >>> resource = proto.clone_with_amount(50.0, (3, 7))
        """
        cloned = self.clone()
        if amount > cloned.max_amount:
            raise ValueError(f"Amount {amount} exceeds max {cloned.max_amount}")
        cloned._amount = amount
        cloned._position = position
        return cloned


class PrototypeRegistry:
    """
    Registry for managing resource prototypes.

    This class maintains a collection of named prototypes and provides
    methods for registering, retrieving, and cloning from them.

    The registry pattern combined with prototype pattern allows:
    - Centralized management of resource templates
    - Easy lookup by name
    - Consistent resource creation across the application

    This demonstrates the Single Responsibility Principle by focusing
    solely on prototype management.
    """

    def __init__(self) -> None:
        """Initialize an empty prototype registry."""
        self._prototypes: Dict[str, ResourcePrototype] = {}

    def register_prototype(self, prototype: ResourcePrototype) -> None:
        """
        Register a prototype in the registry.

        Args:
            prototype (ResourcePrototype): The prototype to register

        Raises:
            ValueError: If a prototype with the same name already exists

        Examples:
            >>> registry = PrototypeRegistry()
            >>> food_proto = ResourcePrototype("berry_bush", berry_template)
            >>> registry.register_prototype(food_proto)
        """
        if prototype.name in self._prototypes:
            raise ValueError(f"Prototype '{prototype.name}' already registered")
        self._prototypes[prototype.name] = prototype

    def get_prototype(self, name: str) -> Optional[ResourcePrototype]:
        """
        Retrieve a prototype by name.

        Args:
            name (str): The prototype name

        Returns:
            Optional[ResourcePrototype]: The prototype, or None if not found

        Examples:
            >>> proto = registry.get_prototype("berry_bush")
            >>> if proto:
            ...     resource = proto.clone()
        """
        return self._prototypes.get(name)

    def create_resource(self, prototype_name: str, position: tuple) -> Optional[Resource]:
        """
        Create a resource from a registered prototype.

        Args:
            prototype_name (str): Name of the prototype to clone
            position (tuple): Position for the new resource

        Returns:
            Optional[Resource]: The cloned resource, or None if prototype not found

        Examples:
            >>> resource = registry.create_resource("berry_bush", (10, 15))
        """
        prototype = self.get_prototype(prototype_name)
        if prototype:
            return prototype.clone_at_position(position)
        return None

    def has_prototype(self, name: str) -> bool:
        """
        Check if a prototype is registered.

        Args:
            name (str): The prototype name to check

        Returns:
            bool: True if registered, False otherwise
        """
        return name in self._prototypes

    def list_prototypes(self) -> list[str]:
        """
        Get a list of all registered prototype names.

        Returns:
            list[str]: List of prototype names

        Examples:
            >>> names = registry.list_prototypes()
            >>> print(f"Available prototypes: {', '.join(names)}")
        """
        return list(self._prototypes.keys())

    def unregister_prototype(self, name: str) -> bool:
        """
        Remove a prototype from the registry.

        Args:
            name (str): The prototype name to remove

        Returns:
            bool: True if removed, False if not found

        Examples:
            >>> registry.unregister_prototype("old_template")
        """
        if name in self._prototypes:
            del self._prototypes[name]
            return True
        return False

    def clear(self) -> None:
        """Remove all prototypes from the registry."""
        self._prototypes.clear()


def create_default_prototypes() -> PrototypeRegistry:
    """
    Factory function to create a registry with default resource prototypes.

    This function demonstrates how prototypes can be pre-configured with
    standard templates for common resource types.

    Returns:
        PrototypeRegistry: Registry with standard resource prototypes

    Examples:
        >>> registry = create_default_prototypes()
        >>> food = registry.create_resource("standard_food", (5, 5))
        >>> material = registry.create_resource("standard_material", (10, 10))
    """
    registry = PrototypeRegistry()

    # Standard food prototype (fast regeneration)
    food_template = Food(
        amount=100.0,
        max_amount=100.0,
        position=(0, 0),  # Position will be overridden on clone
        regeneration_rate=0.15
    )
    registry.register_prototype(ResourcePrototype("standard_food", food_template))

    # Rich food prototype (high capacity, slow regeneration)
    rich_food_template = Food(
        amount=200.0,
        max_amount=200.0,
        position=(0, 0),
        regeneration_rate=0.05
    )
    registry.register_prototype(ResourcePrototype("rich_food", rich_food_template))

    # Standard material prototype
    material_template = Material(
        amount=150.0,
        max_amount=150.0,
        position=(0, 0),
        material_quality=1.0
    )
    registry.register_prototype(ResourcePrototype("standard_material", material_template))

    # High quality material prototype
    quality_material_template = Material(
        amount=100.0,
        max_amount=100.0,
        position=(0, 0),
        material_quality=1.5
    )
    registry.register_prototype(ResourcePrototype("quality_material", quality_material_template))

    # Standard water prototype
    water_template = Water(
        amount=80.0,
        max_amount=80.0,
        position=(0, 0),
        base_regeneration_rate=0.2,
        terrain_multiplier=1.0
    )
    registry.register_prototype(ResourcePrototype("standard_water", water_template))

    # Abundant water prototype (near water terrain)
    abundant_water_template = Water(
        amount=120.0,
        max_amount=120.0,
        position=(0, 0),
        base_regeneration_rate=0.2,
        terrain_multiplier=2.5
    )
    registry.register_prototype(ResourcePrototype("abundant_water", abundant_water_template))

    return registry
