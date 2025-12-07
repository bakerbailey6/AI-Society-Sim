"""
Social Entity Factory Module - Factory Pattern for Social Structures

This module provides factory classes for creating social entities
following the Factory Method and Abstract Factory patterns.

Design Patterns:
    - Factory Method: Each entity type has its own factory
    - Abstract Factory: SocialEntityFactory defines family interface
    - Registry: Central lookup for factories

SOLID Principles:
    - Single Responsibility: Each factory creates one type
    - Open/Closed: New factories can be added without modification
    - Liskov Substitution: All factories implement same interface
    - Dependency Inversion: Code depends on abstract factory
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Dict, Type, TYPE_CHECKING

from social.social_entity import SocialEntity, SocialEntityType
from social.faction import (
    Faction,
    FactionPolicy,
    GovernanceStrategy,
    GovernanceType,
    AutocracyGovernance,
    OligarchyGovernance,
    DemocracyGovernance,
    MeritocracyGovernance
)
from social.group import Group, GroupPurpose, GroupSettings

if TYPE_CHECKING:
    pass


class SocialEntityFactory(ABC):
    """
    Abstract factory for creating social entities.

    Subclasses implement creation logic for specific entity types.
    Follows the Factory Method pattern.

    Examples:
        >>> factory = FactionFactory()
        >>> faction = factory.create(
        ...     name="Warriors Guild",
        ...     founder_id="agent_001",
        ...     timestamp=100.0
        ... )
    """

    @abstractmethod
    def create(
        self,
        name: str,
        founder_id: str,
        timestamp: float,
        **kwargs
    ) -> SocialEntity:
        """
        Create a new social entity.

        Args:
            name: Entity name
            founder_id: ID of the founding agent
            timestamp: Creation timestamp
            **kwargs: Additional type-specific parameters

        Returns:
            The created SocialEntity
        """
        pass

    @abstractmethod
    def entity_type(self) -> SocialEntityType:
        """Get the type of entity this factory creates."""
        pass


class FactionFactory(SocialEntityFactory):
    """
    Factory for creating Faction entities.

    Supports configuring governance style and policies.

    Examples:
        >>> factory = FactionFactory()
        >>> faction = factory.create(
        ...     name="Iron Brotherhood",
        ...     founder_id="agent_001",
        ...     timestamp=100.0,
        ...     governance_type=GovernanceType.DEMOCRACY
        ... )
    """

    # Governance strategy instances (flyweight pattern)
    _governance_strategies: Dict[GovernanceType, GovernanceStrategy] = {
        GovernanceType.AUTOCRACY: AutocracyGovernance(),
        GovernanceType.OLIGARCHY: OligarchyGovernance(),
        GovernanceType.DEMOCRACY: DemocracyGovernance(),
        GovernanceType.MERITOCRACY: MeritocracyGovernance(),
    }

    def create(
        self,
        name: str,
        founder_id: str,
        timestamp: float,
        **kwargs
    ) -> Faction:
        """
        Create a new Faction.

        Args:
            name: Faction name
            founder_id: Leader's agent ID
            timestamp: Creation time
            **kwargs:
                governance_type (GovernanceType): Governance style
                policies (FactionPolicy): Custom policies
                accept_recruits (bool): Override accept_recruits policy
                require_invitation (bool): Override invitation requirement
                max_members (int): Override member limit

        Returns:
            The created Faction
        """
        # Get governance strategy
        gov_type = kwargs.get('governance_type', GovernanceType.AUTOCRACY)
        governance = self._governance_strategies.get(gov_type, AutocracyGovernance())

        # Build policies
        policies = kwargs.get('policies')
        if policies is None:
            policies = FactionPolicy(
                accept_recruits=kwargs.get('accept_recruits', True),
                require_invitation=kwargs.get('require_invitation', True),
                share_stockpiles=kwargs.get('share_stockpiles', True),
                minimum_reputation=kwargs.get('minimum_reputation', 0.0),
                max_members=kwargs.get('max_members', 0)
            )

        return Faction(
            name=name,
            founder_id=founder_id,
            created_at=timestamp,
            governance=governance,
            policies=policies
        )

    def entity_type(self) -> SocialEntityType:
        return SocialEntityType.FACTION

    @classmethod
    def create_autocracy(
        cls,
        name: str,
        founder_id: str,
        timestamp: float,
        **kwargs
    ) -> Faction:
        """Convenience method for autocratic faction."""
        factory = cls()
        return factory.create(
            name=name,
            founder_id=founder_id,
            timestamp=timestamp,
            governance_type=GovernanceType.AUTOCRACY,
            **kwargs
        )

    @classmethod
    def create_democracy(
        cls,
        name: str,
        founder_id: str,
        timestamp: float,
        **kwargs
    ) -> Faction:
        """Convenience method for democratic faction."""
        factory = cls()
        return factory.create(
            name=name,
            founder_id=founder_id,
            timestamp=timestamp,
            governance_type=GovernanceType.DEMOCRACY,
            **kwargs
        )

    @classmethod
    def create_guild(
        cls,
        name: str,
        founder_id: str,
        timestamp: float,
        **kwargs
    ) -> Faction:
        """
        Create a trade guild faction.

        Guilds use oligarchy governance and open membership.
        """
        factory = cls()
        return factory.create(
            name=name,
            founder_id=founder_id,
            timestamp=timestamp,
            governance_type=GovernanceType.OLIGARCHY,
            require_invitation=False,
            **kwargs
        )


class GroupFactory(SocialEntityFactory):
    """
    Factory for creating Group entities.

    Supports configuring group purpose and settings.

    Examples:
        >>> factory = GroupFactory()
        >>> group = factory.create(
        ...     name="Hunters",
        ...     founder_id="agent_001",
        ...     timestamp=100.0,
        ...     purpose=GroupPurpose.HUNTING
        ... )
    """

    def create(
        self,
        name: str,
        founder_id: str,
        timestamp: float,
        **kwargs
    ) -> Group:
        """
        Create a new Group.

        Args:
            name: Group name
            founder_id: Coordinator's agent ID
            timestamp: Creation time
            **kwargs:
                purpose (GroupPurpose): Group's purpose
                max_size (int): Maximum members
                open_membership (bool): Allow open joining
                shared_vision (bool): Share sensor data

        Returns:
            The created Group
        """
        purpose = kwargs.get('purpose', GroupPurpose.SOCIAL)

        settings = GroupSettings(
            max_size=kwargs.get('max_size', 10),
            open_membership=kwargs.get('open_membership', True),
            shared_vision=kwargs.get('shared_vision', False),
            auto_dissolve_empty=kwargs.get('auto_dissolve_empty', True)
        )

        return Group(
            name=name,
            founder_id=founder_id,
            created_at=timestamp,
            purpose=purpose,
            settings=settings
        )

    def entity_type(self) -> SocialEntityType:
        return SocialEntityType.GROUP

    @classmethod
    def create_hunting_party(
        cls,
        name: str,
        founder_id: str,
        timestamp: float,
        max_size: int = 5
    ) -> Group:
        """Convenience method for hunting group."""
        factory = cls()
        return factory.create(
            name=name,
            founder_id=founder_id,
            timestamp=timestamp,
            purpose=GroupPurpose.HUNTING,
            max_size=max_size,
            shared_vision=True
        )

    @classmethod
    def create_exploration_team(
        cls,
        name: str,
        founder_id: str,
        timestamp: float,
        max_size: int = 4
    ) -> Group:
        """Convenience method for exploration group."""
        factory = cls()
        return factory.create(
            name=name,
            founder_id=founder_id,
            timestamp=timestamp,
            purpose=GroupPurpose.EXPLORATION,
            max_size=max_size,
            shared_vision=True
        )

    @classmethod
    def create_defense_squad(
        cls,
        name: str,
        founder_id: str,
        timestamp: float,
        max_size: int = 8
    ) -> Group:
        """Convenience method for defense group."""
        factory = cls()
        return factory.create(
            name=name,
            founder_id=founder_id,
            timestamp=timestamp,
            purpose=GroupPurpose.DEFENSE,
            max_size=max_size,
            open_membership=False  # Invite only for defense
        )


class SocialEntityFactoryRegistry:
    """
    Registry for social entity factories.

    Provides central lookup for factories by entity type.
    Implements the Registry pattern.

    Examples:
        >>> registry = SocialEntityFactoryRegistry()
        >>> registry.register(SocialEntityType.FACTION, FactionFactory())
        >>> factory = registry.get(SocialEntityType.FACTION)
        >>> faction = factory.create("Warriors", "agent_001", 100.0)
    """

    _instance: Optional[SocialEntityFactoryRegistry] = None

    def __init__(self) -> None:
        """Initialize the registry with default factories."""
        self._factories: Dict[SocialEntityType, SocialEntityFactory] = {}
        self._register_defaults()

    def _register_defaults(self) -> None:
        """Register default factories."""
        self.register(SocialEntityType.FACTION, FactionFactory())
        self.register(SocialEntityType.GROUP, GroupFactory())

    @classmethod
    def get_instance(cls) -> SocialEntityFactoryRegistry:
        """
        Get the singleton registry instance.

        Returns:
            The global registry instance
        """
        if cls._instance is None:
            cls._instance = SocialEntityFactoryRegistry()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset the singleton instance (for testing)."""
        cls._instance = None

    def register(
        self,
        entity_type: SocialEntityType,
        factory: SocialEntityFactory
    ) -> None:
        """
        Register a factory for an entity type.

        Args:
            entity_type: Type of entity
            factory: Factory to register

        Raises:
            ValueError: If factory type doesn't match entity type
        """
        if factory.entity_type() != entity_type:
            raise ValueError(
                f"Factory type {factory.entity_type()} doesn't match "
                f"registered type {entity_type}"
            )
        self._factories[entity_type] = factory

    def get(self, entity_type: SocialEntityType) -> Optional[SocialEntityFactory]:
        """
        Get factory for an entity type.

        Args:
            entity_type: Type of entity

        Returns:
            Factory or None if not registered
        """
        return self._factories.get(entity_type)

    def create(
        self,
        entity_type: SocialEntityType,
        name: str,
        founder_id: str,
        timestamp: float,
        **kwargs
    ) -> Optional[SocialEntity]:
        """
        Create an entity using the registered factory.

        Convenience method that looks up factory and creates entity.

        Args:
            entity_type: Type of entity to create
            name: Entity name
            founder_id: Founder's agent ID
            timestamp: Creation time
            **kwargs: Type-specific parameters

        Returns:
            Created entity or None if no factory registered
        """
        factory = self.get(entity_type)
        if factory is None:
            return None

        return factory.create(name, founder_id, timestamp, **kwargs)

    def get_registered_types(self) -> list:
        """Get list of registered entity types."""
        return list(self._factories.keys())


# Convenience function for quick access
def create_faction(
    name: str,
    founder_id: str,
    timestamp: float,
    governance_type: GovernanceType = GovernanceType.AUTOCRACY,
    **kwargs
) -> Faction:
    """
    Convenience function to create a faction.

    Args:
        name: Faction name
        founder_id: Founder's agent ID
        timestamp: Creation time
        governance_type: Type of governance
        **kwargs: Additional faction options

    Returns:
        Created Faction
    """
    factory = FactionFactory()
    return factory.create(
        name=name,
        founder_id=founder_id,
        timestamp=timestamp,
        governance_type=governance_type,
        **kwargs
    )


def create_group(
    name: str,
    founder_id: str,
    timestamp: float,
    purpose: GroupPurpose = GroupPurpose.SOCIAL,
    **kwargs
) -> Group:
    """
    Convenience function to create a group.

    Args:
        name: Group name
        founder_id: Coordinator's agent ID
        timestamp: Creation time
        purpose: Group's purpose
        **kwargs: Additional group options

    Returns:
        Created Group
    """
    factory = GroupFactory()
    return factory.create(
        name=name,
        founder_id=founder_id,
        timestamp=timestamp,
        purpose=purpose,
        **kwargs
    )
