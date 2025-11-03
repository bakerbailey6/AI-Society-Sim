"""
Resource Module - Abstract Resource Hierarchy

This module provides an abstract base class for all resources in the world,
demonstrating inheritance hierarchies and the Open/Closed Principle.

Design Patterns:
    - Template Method (implicit in abstract methods)
    - Marker Interfaces (IHarvestable, IDepletable, etc.)

SOLID Principles:
    - Single Responsibility: Each resource type has one clear purpose
    - Open/Closed: New resource types can be added without modifying existing code
    - Liskov Substitution: All resource subclasses are substitutable for Resource
    - Dependency Inversion: Depends on abstract Resource, not concrete types
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional
from enum import Enum
import uuid

# Import marker interfaces
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from world.markers import IHarvestable, IDepletable, IRegenerative, IObservable, IPoolable


class ResourceType(Enum):
    """
    Enumeration of resource types in the simulation.

    Attributes:
        FOOD: Consumable resource that sustains agents
        MATERIAL: Building and crafting resource
        WATER: Essential resource for agent survival
    """
    FOOD = "food"
    MATERIAL = "material"
    WATER = "water"


class Resource(ABC, IObservable):
    """
    Abstract base class for all resources in the world.

    Resources are objects that agents can interact with, harvest, and consume.
    This abstract class defines the common interface and behavior for all
    resource types while allowing specific implementations to vary.

    All resources are observable (IObservable marker), meaning agents can
    detect them during their sensing phase.

    Attributes:
        resource_id (str): Unique identifier for this resource instance
        resource_type (ResourceType): The type of resource
        amount (float): Current amount/quantity of the resource
        max_amount (float): Maximum capacity of this resource
        position (tuple): Grid position where resource is located

    Note:
        This class demonstrates the Open/Closed Principle - new resource
        types can be added by extending this class without modification.
    """

    def __init__(
        self,
        resource_type: ResourceType,
        amount: float,
        max_amount: float,
        position: tuple
    ) -> None:
        """
        Initialize a resource.

        Args:
            resource_type (ResourceType): The type of resource
            amount (float): Initial amount (must be <= max_amount)
            max_amount (float): Maximum capacity
            position (tuple): Grid position (x, y)

        Raises:
            ValueError: If amount > max_amount or values are negative
        """
        if amount < 0 or max_amount < 0:
            raise ValueError("Resource amounts cannot be negative")
        if amount > max_amount:
            raise ValueError("Initial amount cannot exceed maximum")

        self._resource_id: str = str(uuid.uuid4())
        self._resource_type: ResourceType = resource_type
        self._amount: float = amount
        self._max_amount: float = max_amount
        self._position: tuple = position

    @property
    def resource_id(self) -> str:
        """Get the unique resource identifier."""
        return self._resource_id

    @property
    def resource_type(self) -> ResourceType:
        """Get the resource type."""
        return self._resource_type

    @property
    def amount(self) -> float:
        """Get the current amount of the resource."""
        return self._amount

    @property
    def max_amount(self) -> float:
        """Get the maximum capacity of the resource."""
        return self._max_amount

    @property
    def position(self) -> tuple:
        """Get the grid position of the resource."""
        return self._position

    @abstractmethod
    def get_value(self) -> float:
        """
        Calculate the value/utility of this resource.

        Returns:
            float: The calculated value

        Note:
            Subclasses define their own value calculations based on
            amount, scarcity, or other factors.
        """
        pass

    @abstractmethod
    def can_harvest(self) -> bool:
        """
        Check if this resource can currently be harvested.

        Returns:
            bool: True if harvestable, False otherwise

        Note:
            Conditions for harvesting may vary by resource type.
        """
        pass

    def is_depleted(self) -> bool:
        """
        Check if the resource is completely depleted.

        Returns:
            bool: True if amount is zero or below
        """
        return self._amount <= 0

    def __str__(self) -> str:
        """String representation of the resource."""
        return f"{self.resource_type.value}@{self.position}: {self._amount:.1f}/{self._max_amount:.1f}"

    def __repr__(self) -> str:
        """Developer-friendly representation."""
        return (f"{self.__class__.__name__}(type={self.resource_type.value}, "
                f"amount={self._amount}, position={self.position})")


class Food(Resource, IHarvestable, IDepletable, IRegenerative, IPoolable):
    """
    Food resource that regenerates over time.

    Food is essential for agent survival and regenerates naturally,
    representing renewable resources like fruit, game, or crops.

    This class demonstrates:
    - IHarvestable: Can be collected by agents
    - IDepletable: Has finite amount that decreases when harvested
    - IRegenerative: Automatically regenerates over time
    - IPoolable: Can be returned to resource pool when depleted

    Attributes:
        regeneration_rate (float): Amount regenerated per time step
    """

    def __init__(
        self,
        amount: float,
        max_amount: float,
        position: tuple,
        regeneration_rate: float = 0.1
    ) -> None:
        """
        Initialize a food resource.

        Args:
            amount (float): Initial food amount
            max_amount (float): Maximum food capacity
            position (tuple): Grid position
            regeneration_rate (float): Amount regenerated per time step
        """
        super().__init__(ResourceType.FOOD, amount, max_amount, position)
        self._regeneration_rate: float = regeneration_rate

    @property
    def regeneration_rate(self) -> float:
        """Get the regeneration rate."""
        return self._regeneration_rate

    def get_value(self) -> float:
        """
        Calculate food value based on current amount.

        Returns:
            float: The food value (same as amount for food)
        """
        return self._amount

    def can_harvest(self) -> bool:
        """
        Check if food can be harvested.

        Returns:
            bool: True if amount > 0
        """
        return self._amount > 0

    def deplete(self, amount: float) -> float:
        """
        Remove food from this resource.

        Args:
            amount (float): Amount to remove

        Returns:
            float: Actual amount removed (may be less if insufficient)
        """
        actual_amount = min(amount, self._amount)
        self._amount -= actual_amount
        return actual_amount

    def regenerate(self, time_steps: int = 1) -> None:
        """
        Regenerate food over time.

        Args:
            time_steps (int): Number of time steps to regenerate
        """
        regeneration = self._regeneration_rate * time_steps
        self._amount = min(self._amount + regeneration, self._max_amount)


class Material(Resource, IHarvestable, IDepletable, IPoolable):
    """
    Material resource for building and crafting.

    Materials are finite resources that deplete when harvested but do not
    regenerate naturally. They represent stone, wood, or ore.

    This class demonstrates:
    - IHarvestable: Can be collected by agents
    - IDepletable: Has finite amount with no regeneration
    - IPoolable: Can be returned to resource pool when depleted

    Attributes:
        material_quality (float): Quality multiplier for crafting (0.5-2.0)
    """

    def __init__(
        self,
        amount: float,
        max_amount: float,
        position: tuple,
        material_quality: float = 1.0
    ) -> None:
        """
        Initialize a material resource.

        Args:
            amount (float): Initial material amount
            max_amount (float): Maximum material capacity
            position (tuple): Grid position
            material_quality (float): Quality multiplier (0.5-2.0)

        Raises:
            ValueError: If quality is outside valid range
        """
        super().__init__(ResourceType.MATERIAL, amount, max_amount, position)
        if not 0.5 <= material_quality <= 2.0:
            raise ValueError("Material quality must be between 0.5 and 2.0")
        self._material_quality: float = material_quality

    @property
    def material_quality(self) -> float:
        """Get the material quality multiplier."""
        return self._material_quality

    def get_value(self) -> float:
        """
        Calculate material value based on amount and quality.

        Returns:
            float: The material value (amount * quality)
        """
        return self._amount * self._material_quality

    def can_harvest(self) -> bool:
        """
        Check if material can be harvested.

        Returns:
            bool: True if amount > 0
        """
        return self._amount > 0

    def deplete(self, amount: float) -> float:
        """
        Remove material from this resource.

        Args:
            amount (float): Amount to remove

        Returns:
            float: Actual amount removed
        """
        actual_amount = min(amount, self._amount)
        self._amount -= actual_amount
        return actual_amount


class Water(Resource, IHarvestable, IRegenerative, IPoolable):
    """
    Water resource that regenerates based on terrain.

    Water is essential for agent survival and regenerates at a rate
    dependent on the terrain type (faster near water terrain).

    This class demonstrates:
    - IHarvestable: Can be collected by agents
    - IRegenerative: Regenerates over time
    - IPoolable: Can be returned to resource pool
    - NOT IDepletable: Water is treated as infinite but rate-limited

    Attributes:
        base_regeneration_rate (float): Base regeneration per time step
        terrain_multiplier (float): Terrain-based regeneration modifier
    """

    def __init__(
        self,
        amount: float,
        max_amount: float,
        position: tuple,
        base_regeneration_rate: float = 0.2,
        terrain_multiplier: float = 1.0
    ) -> None:
        """
        Initialize a water resource.

        Args:
            amount (float): Initial water amount
            max_amount (float): Maximum water capacity
            position (tuple): Grid position
            base_regeneration_rate (float): Base regeneration rate
            terrain_multiplier (float): Terrain-based modifier (0.1-3.0)
        """
        super().__init__(ResourceType.WATER, amount, max_amount, position)
        self._base_regeneration_rate: float = base_regeneration_rate
        self._terrain_multiplier: float = terrain_multiplier

    @property
    def effective_regeneration_rate(self) -> float:
        """Get the effective regeneration rate including terrain modifier."""
        return self._base_regeneration_rate * self._terrain_multiplier

    def get_value(self) -> float:
        """
        Calculate water value.

        Returns:
            float: The water value (same as amount)
        """
        return self._amount

    def can_harvest(self) -> bool:
        """
        Check if water can be harvested.

        Returns:
            bool: True if amount > 0
        """
        return self._amount > 0

    def harvest(self, amount: float) -> float:
        """
        Harvest water from this resource.

        Args:
            amount (float): Amount to harvest

        Returns:
            float: Actual amount harvested

        Note:
            Water is not truly depleted but is rate-limited by regeneration.
        """
        actual_amount = min(amount, self._amount)
        self._amount -= actual_amount
        return actual_amount

    def regenerate(self, time_steps: int = 1) -> None:
        """
        Regenerate water over time based on terrain.

        Args:
            time_steps (int): Number of time steps to regenerate
        """
        regeneration = self.effective_regeneration_rate * time_steps
        self._amount = min(self._amount + regeneration, self._max_amount)
