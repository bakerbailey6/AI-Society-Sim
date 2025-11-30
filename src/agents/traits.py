"""
Traits Module - Agent Characteristics

This module defines agent characteristics and attributes that influence
behavior and capabilities, demonstrating the Value Object pattern.

Design Patterns:
    - Value Object: Immutable trait definitions
    - Factory Method: TraitGenerator for creating trait combinations

SOLID Principles:
    - Single Responsibility: Only manages trait data
    - Open/Closed: New trait generators can be added without modification
"""

from dataclasses import dataclass
from typing import Optional
import random

# Import resource types for gather bonus calculations
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from resources.resource import ResourceType


@dataclass(frozen=True)
class AgentTraits:
    """
    Immutable agent characteristics.

    Traits influence agent capabilities and behavior preferences.
    This is a value object - once created, it cannot be modified.

    Using frozen=True makes this a truly immutable dataclass,
    preventing modification after creation and enabling safe sharing
    between components.

    Attributes:
        strength (float): Physical power (0-100), affects combat and gathering
        intelligence (float): Mental capability (0-100), affects learning and efficiency
        sociability (float): Social inclination (0-100), affects group formation
        aggression (float): Hostility tendency (0-100), affects combat decisions
        curiosity (float): Exploration drive (0-100), affects exploration behavior
        vision_radius (int): How far agent can see (minimum 1)
        movement_speed (float): Movement efficiency multiplier (must be positive)

    Examples:
        >>> traits = AgentTraits(strength=75, intelligence=60)
        >>> print(traits.strength)
        75.0
        >>> traits.strength = 80  # Raises FrozenInstanceError
    """

    strength: float = 50.0
    intelligence: float = 50.0
    sociability: float = 50.0
    aggression: float = 50.0
    curiosity: float = 50.0
    vision_radius: int = 5
    movement_speed: float = 1.0

    def __post_init__(self):
        """
        Validate trait values after initialization.

        Raises:
            ValueError: If any trait value is out of valid range
        """
        # Validate stat ranges (0-100)
        for attr in ['strength', 'intelligence', 'sociability',
                     'aggression', 'curiosity']:
            value = getattr(self, attr)
            if not 0 <= value <= 100:
                raise ValueError(f"{attr} must be between 0 and 100, got {value}")

        # Validate vision radius
        if self.vision_radius < 1:
            raise ValueError(f"vision_radius must be at least 1, got {self.vision_radius}")

        # Validate movement speed
        if self.movement_speed <= 0:
            raise ValueError(f"movement_speed must be positive, got {self.movement_speed}")

    def get_gather_bonus(self, resource_type: ResourceType) -> float:
        """
        Calculate gathering efficiency bonus based on traits.

        Different traits affect different resource types:
        - Intelligence helps with all gathering
        - Strength especially helps with material gathering

        Args:
            resource_type (ResourceType): Type of resource being gathered

        Returns:
            float: Multiplier bonus (e.g., 0.2 = 20% bonus)

        Examples:
            >>> traits = AgentTraits(strength=80, intelligence=60)
            >>> bonus = traits.get_gather_bonus(ResourceType.MATERIAL)
            >>> print(f"Bonus: {bonus:.2%}")
            Bonus: 17.50%
        """
        # Intelligence helps with all gathering
        # Normalized to -0.25 to +0.25 range
        bonus = (self.intelligence - 50) / 200

        # Strength especially helps with material gathering
        if resource_type == ResourceType.MATERIAL:
            bonus += (self.strength - 50) / 400

        return bonus

    def get_combat_bonus(self) -> float:
        """
        Calculate combat effectiveness bonus.

        Combat effectiveness is based on both strength and aggression.

        Returns:
            float: Combat multiplier (0-2 range typically)

        Examples:
            >>> traits = AgentTraits(strength=90, aggression=70)
            >>> bonus = traits.get_combat_bonus()
            >>> print(f"Combat multiplier: {bonus:.2f}")
            Combat multiplier: 1.22
        """
        # Base combat from strength (0 to 1)
        base = self.strength / 100

        # Aggression provides additional multiplier (0 to 0.5)
        aggression_mult = self.aggression / 200

        return base * (1 + aggression_mult)

    def get_social_bonus(self) -> float:
        """
        Calculate social interaction bonus.

        Higher sociability makes social actions more effective.

        Returns:
            float: Social effectiveness multiplier (0-1)

        Examples:
            >>> traits = AgentTraits(sociability=80)
            >>> bonus = traits.get_social_bonus()
            >>> print(f"Social bonus: {bonus:.2f}")
            Social bonus: 0.80
        """
        return self.sociability / 100

    def get_learning_rate(self) -> float:
        """
        Calculate learning rate modifier based on intelligence.

        Returns:
            float: Learning rate multiplier (0.5-1.5 range)

        Examples:
            >>> traits = AgentTraits(intelligence=85)
            >>> rate = traits.get_learning_rate()
            >>> print(f"Learning rate: {rate:.2f}")
            Learning rate: 1.35
        """
        # Intelligence maps to 0.5-1.5 learning rate
        return 0.5 + (self.intelligence / 100)


class TraitGenerator:
    """
    Factory for generating agent traits with various presets.

    Provides methods for creating different trait combinations,
    from random to specialized archetypes.

    Design Pattern:
        - Factory Method: Provides different trait generation strategies
        - Static Methods: No instance state needed
    """

    @staticmethod
    def random_traits() -> AgentTraits:
        """
        Generate random traits within reasonable ranges.

        Returns:
            AgentTraits: Randomly generated traits

        Examples:
            >>> traits = TraitGenerator.random_traits()
            >>> assert 20 <= traits.strength <= 80
        """
        return AgentTraits(
            strength=random.uniform(20, 80),
            intelligence=random.uniform(20, 80),
            sociability=random.uniform(20, 80),
            aggression=random.uniform(10, 60),
            curiosity=random.uniform(30, 90),
            vision_radius=random.randint(3, 8),
            movement_speed=random.uniform(0.8, 1.5)
        )

    @staticmethod
    def balanced_traits() -> AgentTraits:
        """
        Generate balanced average traits.

        All stats are at median values, suitable for baseline agents.

        Returns:
            AgentTraits: Balanced traits

        Examples:
            >>> traits = TraitGenerator.balanced_traits()
            >>> assert traits.strength == 50.0
        """
        return AgentTraits(
            strength=50.0,
            intelligence=50.0,
            sociability=50.0,
            aggression=30.0,
            curiosity=50.0,
            vision_radius=5,
            movement_speed=1.0
        )

    @staticmethod
    def warrior_traits() -> AgentTraits:
        """
        Generate warrior-focused traits.

        High strength and aggression, lower intelligence and sociability.
        Suitable for combat-oriented agents.

        Returns:
            AgentTraits: Combat-oriented traits

        Examples:
            >>> traits = TraitGenerator.warrior_traits()
            >>> assert traits.strength > 70
            >>> assert traits.aggression > 60
        """
        return AgentTraits(
            strength=80.0,
            intelligence=40.0,
            sociability=30.0,
            aggression=70.0,
            curiosity=40.0,
            vision_radius=6,
            movement_speed=1.2
        )

    @staticmethod
    def scholar_traits() -> AgentTraits:
        """
        Generate scholar-focused traits.

        High intelligence and curiosity, lower strength and aggression.
        Suitable for learning and innovation-focused agents.

        Returns:
            AgentTraits: Intelligence-oriented traits

        Examples:
            >>> traits = TraitGenerator.scholar_traits()
            >>> assert traits.intelligence > 80
            >>> assert traits.curiosity > 85
        """
        return AgentTraits(
            strength=30.0,
            intelligence=85.0,
            sociability=60.0,
            aggression=20.0,
            curiosity=90.0,
            vision_radius=7,
            movement_speed=0.9
        )

    @staticmethod
    def social_traits() -> AgentTraits:
        """
        Generate socially-focused traits.

        High sociability, moderate intelligence, low aggression.
        Suitable for traders, diplomats, and group-oriented agents.

        Returns:
            AgentTraits: Social-oriented traits

        Examples:
            >>> traits = TraitGenerator.social_traits()
            >>> assert traits.sociability > 85
            >>> assert traits.aggression < 20
        """
        return AgentTraits(
            strength=40.0,
            intelligence=60.0,
            sociability=90.0,
            aggression=15.0,
            curiosity=70.0,
            vision_radius=5,
            movement_speed=1.0
        )

    @staticmethod
    def explorer_traits() -> AgentTraits:
        """
        Generate explorer-focused traits.

        High curiosity and movement speed, balanced other stats.
        Suitable for scouting and exploration-focused agents.

        Returns:
            AgentTraits: Exploration-oriented traits

        Examples:
            >>> traits = TraitGenerator.explorer_traits()
            >>> assert traits.curiosity > 85
            >>> assert traits.movement_speed > 1.2
        """
        return AgentTraits(
            strength=55.0,
            intelligence=65.0,
            sociability=45.0,
            aggression=35.0,
            curiosity=90.0,
            vision_radius=8,
            movement_speed=1.3
        )

    @staticmethod
    def custom_traits(
        strength: float = 50.0,
        intelligence: float = 50.0,
        sociability: float = 50.0,
        aggression: float = 50.0,
        curiosity: float = 50.0,
        vision_radius: int = 5,
        movement_speed: float = 1.0
    ) -> AgentTraits:
        """
        Generate custom traits with specified values.

        Args:
            strength: Physical power (0-100)
            intelligence: Mental capability (0-100)
            sociability: Social inclination (0-100)
            aggression: Hostility tendency (0-100)
            curiosity: Exploration drive (0-100)
            vision_radius: Vision distance (minimum 1)
            movement_speed: Movement multiplier (must be positive)

        Returns:
            AgentTraits: Custom traits

        Raises:
            ValueError: If any trait value is invalid

        Examples:
            >>> traits = TraitGenerator.custom_traits(strength=75, intelligence=65)
            >>> assert traits.strength == 75.0
        """
        return AgentTraits(
            strength=strength,
            intelligence=intelligence,
            sociability=sociability,
            aggression=aggression,
            curiosity=curiosity,
            vision_radius=vision_radius,
            movement_speed=movement_speed
        )
