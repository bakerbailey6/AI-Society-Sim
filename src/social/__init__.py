"""
Social Package - Social Systems for AI Agents

This package provides the social and faction systems for the AI Society
Simulation, enabling agents to form groups, factions, and maintain
relationships with other agents and organizations.

Design Patterns Used:
    - Abstract Base Class: SocialEntity defines interface for all social structures
    - Template Method: Join/leave operations have standard flow with hooks
    - Strategy: Governance strategies, reputation effects
    - Observer: Membership and relationship change notifications
    - Factory Method: Entity creation via factories
    - Registry: Central factory lookup
    - Immutable: Membership and reputation records
    - Flyweight: Governance strategy instances are shared

Modules:
    social_entity: Abstract base for social structures
    faction: Formal organizations with hierarchy and resources
    group: Informal collections with common purpose
    relationships: Agent and faction relationship tracking
    reputation: Agent standing with factions
    factory: Factory patterns for entity creation

Integration Points:
    - Agents (agents/agent.py): Agents can join/leave social entities
    - Stockpiles (inventory/stockpile.py): FactionAccess uses faction membership
    - Policies (policies/): CooperativePolicy can consider faction membership
    - Actions (actions/): Alliance and trade actions use social systems

Examples:
    Create a faction:
        >>> from social import create_faction, GovernanceType
        >>> faction = create_faction(
        ...     name="Iron Brotherhood",
        ...     founder_id="agent_001",
        ...     timestamp=100.0,
        ...     governance_type=GovernanceType.DEMOCRACY
        ... )

    Create a hunting group:
        >>> from social import GroupFactory
        >>> group = GroupFactory.create_hunting_party(
        ...     name="Northern Hunters",
        ...     founder_id="agent_002",
        ...     timestamp=101.0
        ... )

    Track relationships:
        >>> from social import InMemoryRelationshipManager, RelationshipType
        >>> manager = InMemoryRelationshipManager()
        >>> manager.set_relationship(
        ...     "agent_001", "agent_002",
        ...     RelationshipType.FRIEND, 50.0, 100.0
        ... )

    Track reputation:
        >>> from social import InMemoryReputationManager
        >>> rep_manager = InMemoryReputationManager()
        >>> rep_manager.adjust_reputation(
        ...     "agent_001", "faction_001",
        ...     delta=100.0, reason="Completed quest", timestamp=100.0
        ... )
"""

# Social Entity base
from social.social_entity import (
    SocialEntity,
    SocialEntityType,
    SocialEntityObserver,
    MembershipRole,
    Membership,
)

# Faction
from social.faction import (
    Faction,
    FactionPolicy,
    GovernanceType,
    GovernanceStrategy,
    AutocracyGovernance,
    OligarchyGovernance,
    DemocracyGovernance,
    MeritocracyGovernance,
)

# Group
from social.group import (
    Group,
    GroupPurpose,
    GroupSettings,
)

# Relationships
from social.relationships import (
    RelationshipType,
    Relationship,
    RelationshipModifier,
    RelationshipObserver,
    RelationshipManager,
    InMemoryRelationshipManager,
    FactionRelationshipManager,
)

# Reputation
from social.reputation import (
    ReputationTier,
    ReputationThresholds,
    ReputationChange,
    AgentReputation,
    ReputationObserver,
    ReputationEffects,
    StandardReputationEffects,
    ReputationManager,
    InMemoryReputationManager,
)

# Factories
from social.factory import (
    SocialEntityFactory,
    FactionFactory,
    GroupFactory,
    SocialEntityFactoryRegistry,
    create_faction,
    create_group,
)

__all__ = [
    # Social Entity base
    "SocialEntity",
    "SocialEntityType",
    "SocialEntityObserver",
    "MembershipRole",
    "Membership",

    # Faction
    "Faction",
    "FactionPolicy",
    "GovernanceType",
    "GovernanceStrategy",
    "AutocracyGovernance",
    "OligarchyGovernance",
    "DemocracyGovernance",
    "MeritocracyGovernance",

    # Group
    "Group",
    "GroupPurpose",
    "GroupSettings",

    # Relationships
    "RelationshipType",
    "Relationship",
    "RelationshipModifier",
    "RelationshipObserver",
    "RelationshipManager",
    "InMemoryRelationshipManager",
    "FactionRelationshipManager",

    # Reputation
    "ReputationTier",
    "ReputationThresholds",
    "ReputationChange",
    "AgentReputation",
    "ReputationObserver",
    "ReputationEffects",
    "StandardReputationEffects",
    "ReputationManager",
    "InMemoryReputationManager",

    # Factories
    "SocialEntityFactory",
    "FactionFactory",
    "GroupFactory",
    "SocialEntityFactoryRegistry",
    "create_faction",
    "create_group",
]
