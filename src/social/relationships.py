"""
Relationships Module - Agent and Faction Relationships

This module provides systems for tracking relationships between agents
and between social entities (factions, groups).

Design Patterns:
    - Immutable: Relationship records are frozen dataclasses
    - Observer: Relationship changes can trigger notifications
    - Flyweight: Relationship types are shared instances

SOLID Principles:
    - Single Responsibility: Manages only relationship tracking
    - Open/Closed: New relationship types are extensible
    - Interface Segregation: Separate interfaces for different queries
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Dict, List, Set, Tuple, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum
import uuid

if TYPE_CHECKING:
    from agents.agent import Agent
    from social.social_entity import SocialEntity


class RelationshipType(Enum):
    """
    Types of relationships between entities.

    Agent-Agent relationships:
        STRANGER: No relationship established
        ACQUAINTANCE: Have met/interacted
        FRIEND: Positive relationship
        RIVAL: Competitive relationship
        ENEMY: Hostile relationship
        ALLY: Strong positive bond

    Faction-Faction relationships:
        NEUTRAL: No established relationship
        TRADING_PARTNER: Economic cooperation
        ALLIED: Military/political alliance
        AT_WAR: Active hostility
        VASSAL: Subordinate faction
        OVERLORD: Superior faction
    """
    # Agent-Agent
    STRANGER = "stranger"
    ACQUAINTANCE = "acquaintance"
    FRIEND = "friend"
    RIVAL = "rival"
    ENEMY = "enemy"
    ALLY = "ally"

    # Faction-Faction
    NEUTRAL = "neutral"
    TRADING_PARTNER = "trading_partner"
    ALLIED = "allied"
    AT_WAR = "at_war"
    VASSAL = "vassal"
    OVERLORD = "overlord"


@dataclass(frozen=True)
class RelationshipModifier:
    """
    A modifier affecting a relationship.

    Modifiers are temporary effects that adjust relationship strength.
    They can expire or be permanent.

    Attributes:
        modifier_id: Unique identifier
        source: What caused this modifier (action, event, etc.)
        value: Positive or negative adjustment
        expires_at: When modifier expires (None = permanent)
        description: Human-readable description
    """
    modifier_id: str
    source: str
    value: float
    expires_at: Optional[float]
    description: str


@dataclass
class Relationship:
    """
    A relationship between two entities.

    Tracks the type and strength of relationship, along with
    any temporary modifiers.

    Attributes:
        relationship_id: Unique identifier
        source_id: Entity that "owns" this relationship
        target_id: Entity the relationship is toward
        relationship_type: Current type of relationship
        strength: Numeric strength (-100 to 100)
        modifiers: List of active modifiers
        history: Record of significant events
        created_at: When relationship was established
        last_interaction: Last interaction timestamp

    Note:
        Relationships are directional. Agent A's relationship
        with B may differ from B's relationship with A.
    """
    relationship_id: str
    source_id: str
    target_id: str
    relationship_type: RelationshipType
    strength: float  # -100 (hatred) to 100 (devotion)
    modifiers: List[RelationshipModifier] = field(default_factory=list)
    history: List[str] = field(default_factory=list)
    created_at: float = 0.0
    last_interaction: float = 0.0

    def get_effective_strength(self) -> float:
        """
        Get strength including all active modifiers.

        Returns:
            float: Effective strength (clamped to -100, 100)
        """
        total = self.strength
        for modifier in self.modifiers:
            total += modifier.value
        return max(-100.0, min(100.0, total))

    def add_modifier(self, modifier: RelationshipModifier) -> None:
        """Add a relationship modifier."""
        self.modifiers.append(modifier)

    def remove_expired_modifiers(self, current_time: float) -> int:
        """
        Remove expired modifiers.

        Args:
            current_time: Current simulation time

        Returns:
            int: Number of modifiers removed
        """
        before_count = len(self.modifiers)
        self.modifiers = [
            m for m in self.modifiers
            if m.expires_at is None or m.expires_at > current_time
        ]
        return before_count - len(self.modifiers)

    def add_history_event(self, event: str) -> None:
        """Record a significant event in relationship history."""
        self.history.append(event)


class RelationshipObserver(ABC):
    """
    Observer interface for relationship changes.
    """

    @abstractmethod
    def on_relationship_created(self, relationship: Relationship) -> None:
        """Called when a new relationship is established."""
        pass

    @abstractmethod
    def on_relationship_changed(
        self,
        relationship: Relationship,
        old_type: RelationshipType,
        old_strength: float
    ) -> None:
        """Called when relationship type or strength changes."""
        pass

    @abstractmethod
    def on_relationship_ended(self, relationship: Relationship) -> None:
        """Called when a relationship is terminated."""
        pass


class RelationshipManager(ABC):
    """
    Abstract base for managing relationships.

    Provides interface for tracking and querying relationships.
    Concrete implementations can use different storage strategies.

    This is the main interface for the relationship system.
    """

    @abstractmethod
    def get_relationship(self, source_id: str, target_id: str) -> Optional[Relationship]:
        """
        Get relationship from source to target.

        Args:
            source_id: Entity that has the relationship
            target_id: Entity the relationship is toward

        Returns:
            Relationship or None if no relationship exists
        """
        pass

    @abstractmethod
    def set_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: RelationshipType,
        strength: float,
        timestamp: float
    ) -> Relationship:
        """
        Create or update a relationship.

        Args:
            source_id: Entity that has the relationship
            target_id: Entity the relationship is toward
            relationship_type: Type of relationship
            strength: Relationship strength
            timestamp: Current simulation time

        Returns:
            The created or updated Relationship
        """
        pass

    @abstractmethod
    def adjust_strength(
        self,
        source_id: str,
        target_id: str,
        delta: float,
        reason: str,
        timestamp: float
    ) -> Optional[Relationship]:
        """
        Adjust relationship strength.

        Args:
            source_id: Entity that has the relationship
            target_id: Entity the relationship is toward
            delta: Amount to adjust strength by
            reason: Why the adjustment is happening
            timestamp: Current simulation time

        Returns:
            Updated Relationship or None if no relationship exists
        """
        pass

    @abstractmethod
    def get_all_relationships(self, entity_id: str) -> List[Relationship]:
        """
        Get all relationships where entity is the source.

        Args:
            entity_id: The entity

        Returns:
            List of relationships from this entity
        """
        pass

    @abstractmethod
    def get_relationships_of_type(
        self,
        entity_id: str,
        relationship_type: RelationshipType
    ) -> List[Relationship]:
        """
        Get relationships of a specific type.

        Args:
            entity_id: The entity
            relationship_type: Type to filter by

        Returns:
            List of matching relationships
        """
        pass

    @abstractmethod
    def get_mutual_relationships(
        self,
        entity_a: str,
        entity_b: str
    ) -> Tuple[Optional[Relationship], Optional[Relationship]]:
        """
        Get bidirectional relationship between two entities.

        Args:
            entity_a: First entity
            entity_b: Second entity

        Returns:
            Tuple of (A's relationship with B, B's relationship with A)
        """
        pass


class InMemoryRelationshipManager(RelationshipManager):
    """
    In-memory implementation of RelationshipManager.

    Stores relationships in dictionaries for fast lookup.
    Suitable for simulations with moderate relationship counts.
    """

    def __init__(self) -> None:
        """Initialize the relationship manager."""
        # Nested dict: source_id -> target_id -> Relationship
        self._relationships: Dict[str, Dict[str, Relationship]] = {}
        self._observers: List[RelationshipObserver] = []

    def add_observer(self, observer: RelationshipObserver) -> None:
        """Register an observer."""
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: RelationshipObserver) -> None:
        """Unregister an observer."""
        if observer in self._observers:
            self._observers.remove(observer)

    def get_relationship(self, source_id: str, target_id: str) -> Optional[Relationship]:
        """Get relationship from source to target."""
        source_rels = self._relationships.get(source_id)
        if source_rels is None:
            return None
        return source_rels.get(target_id)

    def set_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: RelationshipType,
        strength: float,
        timestamp: float
    ) -> Relationship:
        """Create or update a relationship."""
        existing = self.get_relationship(source_id, target_id)

        if existing:
            # Update existing
            old_type = existing.relationship_type
            old_strength = existing.strength

            existing.relationship_type = relationship_type
            existing.strength = max(-100.0, min(100.0, strength))
            existing.last_interaction = timestamp

            # Notify observers
            for observer in self._observers:
                observer.on_relationship_changed(existing, old_type, old_strength)

            return existing
        else:
            # Create new
            relationship = Relationship(
                relationship_id=str(uuid.uuid4()),
                source_id=source_id,
                target_id=target_id,
                relationship_type=relationship_type,
                strength=max(-100.0, min(100.0, strength)),
                created_at=timestamp,
                last_interaction=timestamp
            )

            # Store it
            if source_id not in self._relationships:
                self._relationships[source_id] = {}
            self._relationships[source_id][target_id] = relationship

            # Notify observers
            for observer in self._observers:
                observer.on_relationship_created(relationship)

            return relationship

    def adjust_strength(
        self,
        source_id: str,
        target_id: str,
        delta: float,
        reason: str,
        timestamp: float
    ) -> Optional[Relationship]:
        """Adjust relationship strength."""
        relationship = self.get_relationship(source_id, target_id)
        if relationship is None:
            return None

        old_strength = relationship.strength
        relationship.strength = max(-100.0, min(100.0, relationship.strength + delta))
        relationship.last_interaction = timestamp
        relationship.add_history_event(f"{reason}: {delta:+.1f}")

        # Check if type should change based on strength
        new_type = self._determine_type_from_strength(relationship.strength)
        old_type = relationship.relationship_type

        if new_type != old_type:
            relationship.relationship_type = new_type

        # Notify observers
        for observer in self._observers:
            observer.on_relationship_changed(relationship, old_type, old_strength)

        return relationship

    def _determine_type_from_strength(self, strength: float) -> RelationshipType:
        """
        Determine relationship type based on strength.

        This is a helper for automatic type transitions.
        """
        if strength >= 75:
            return RelationshipType.ALLY
        elif strength >= 40:
            return RelationshipType.FRIEND
        elif strength >= 10:
            return RelationshipType.ACQUAINTANCE
        elif strength >= -10:
            return RelationshipType.STRANGER
        elif strength >= -40:
            return RelationshipType.RIVAL
        else:
            return RelationshipType.ENEMY

    def get_all_relationships(self, entity_id: str) -> List[Relationship]:
        """Get all relationships from this entity."""
        source_rels = self._relationships.get(entity_id)
        if source_rels is None:
            return []
        return list(source_rels.values())

    def get_relationships_of_type(
        self,
        entity_id: str,
        relationship_type: RelationshipType
    ) -> List[Relationship]:
        """Get relationships of a specific type."""
        all_rels = self.get_all_relationships(entity_id)
        return [r for r in all_rels if r.relationship_type == relationship_type]

    def get_mutual_relationships(
        self,
        entity_a: str,
        entity_b: str
    ) -> Tuple[Optional[Relationship], Optional[Relationship]]:
        """Get bidirectional relationships."""
        a_to_b = self.get_relationship(entity_a, entity_b)
        b_to_a = self.get_relationship(entity_b, entity_a)
        return (a_to_b, b_to_a)

    def remove_relationship(self, source_id: str, target_id: str) -> bool:
        """
        Remove a relationship.

        Args:
            source_id: Entity that has the relationship
            target_id: Entity the relationship is toward

        Returns:
            bool: True if relationship existed and was removed
        """
        source_rels = self._relationships.get(source_id)
        if source_rels is None:
            return False

        relationship = source_rels.get(target_id)
        if relationship is None:
            return False

        del source_rels[target_id]

        # Notify observers
        for observer in self._observers:
            observer.on_relationship_ended(relationship)

        return True

    def get_friends(self, entity_id: str) -> List[str]:
        """Get IDs of entities this entity considers friends or better."""
        rels = self.get_all_relationships(entity_id)
        return [
            r.target_id for r in rels
            if r.relationship_type in (RelationshipType.FRIEND, RelationshipType.ALLY)
        ]

    def get_enemies(self, entity_id: str) -> List[str]:
        """Get IDs of entities this entity considers enemies."""
        rels = self.get_all_relationships(entity_id)
        return [
            r.target_id for r in rels
            if r.relationship_type in (RelationshipType.ENEMY, RelationshipType.RIVAL)
        ]

    def are_allies(self, entity_a: str, entity_b: str) -> bool:
        """Check if two entities have a mutual alliance."""
        a_to_b, b_to_a = self.get_mutual_relationships(entity_a, entity_b)

        if a_to_b is None or b_to_a is None:
            return False

        ally_types = (RelationshipType.ALLY, RelationshipType.ALLIED, RelationshipType.FRIEND)
        return (
            a_to_b.relationship_type in ally_types and
            b_to_a.relationship_type in ally_types
        )

    def are_enemies(self, entity_a: str, entity_b: str) -> bool:
        """Check if two entities have mutual hostility."""
        a_to_b, b_to_a = self.get_mutual_relationships(entity_a, entity_b)

        if a_to_b is None or b_to_a is None:
            return False

        enemy_types = (RelationshipType.ENEMY, RelationshipType.AT_WAR)
        return (
            a_to_b.relationship_type in enemy_types and
            b_to_a.relationship_type in enemy_types
        )

    def cleanup_expired_modifiers(self, current_time: float) -> int:
        """
        Remove expired modifiers from all relationships.

        Args:
            current_time: Current simulation time

        Returns:
            int: Total number of modifiers removed
        """
        total_removed = 0
        for source_rels in self._relationships.values():
            for relationship in source_rels.values():
                total_removed += relationship.remove_expired_modifiers(current_time)
        return total_removed


class FactionRelationshipManager(RelationshipManager):
    """
    Specialized relationship manager for faction-to-faction relationships.

    Extends base manager with faction-specific concepts like
    treaties, wars, and vassalage.
    """

    def __init__(self) -> None:
        """Initialize the faction relationship manager."""
        self._base_manager = InMemoryRelationshipManager()

        # Track active treaties/wars
        self._active_wars: Set[Tuple[str, str]] = set()  # Frozen sets of faction IDs
        self._trade_agreements: Dict[Tuple[str, str], float] = {}  # Duration

    def get_relationship(self, source_id: str, target_id: str) -> Optional[Relationship]:
        return self._base_manager.get_relationship(source_id, target_id)

    def set_relationship(
        self,
        source_id: str,
        target_id: str,
        relationship_type: RelationshipType,
        strength: float,
        timestamp: float
    ) -> Relationship:
        return self._base_manager.set_relationship(
            source_id, target_id, relationship_type, strength, timestamp
        )

    def adjust_strength(
        self,
        source_id: str,
        target_id: str,
        delta: float,
        reason: str,
        timestamp: float
    ) -> Optional[Relationship]:
        return self._base_manager.adjust_strength(
            source_id, target_id, delta, reason, timestamp
        )

    def get_all_relationships(self, entity_id: str) -> List[Relationship]:
        return self._base_manager.get_all_relationships(entity_id)

    def get_relationships_of_type(
        self,
        entity_id: str,
        relationship_type: RelationshipType
    ) -> List[Relationship]:
        return self._base_manager.get_relationships_of_type(entity_id, relationship_type)

    def get_mutual_relationships(
        self,
        entity_a: str,
        entity_b: str
    ) -> Tuple[Optional[Relationship], Optional[Relationship]]:
        return self._base_manager.get_mutual_relationships(entity_a, entity_b)

    # --- Faction-specific methods ---

    def declare_war(
        self,
        aggressor_id: str,
        defender_id: str,
        timestamp: float
    ) -> bool:
        """
        Declare war between two factions.

        Sets both relationships to AT_WAR.

        Args:
            aggressor_id: Faction declaring war
            defender_id: Faction being attacked
            timestamp: Current time

        Returns:
            bool: True if war declared
        """
        war_key = tuple(sorted([aggressor_id, defender_id]))
        if war_key in self._active_wars:
            return False  # Already at war

        # Set both relationships to AT_WAR
        self.set_relationship(
            aggressor_id, defender_id,
            RelationshipType.AT_WAR, -80.0, timestamp
        )
        self.set_relationship(
            defender_id, aggressor_id,
            RelationshipType.AT_WAR, -80.0, timestamp
        )

        self._active_wars.add(war_key)
        return True

    def make_peace(
        self,
        faction_a: str,
        faction_b: str,
        timestamp: float
    ) -> bool:
        """
        End war between factions.

        Args:
            faction_a: First faction
            faction_b: Second faction
            timestamp: Current time

        Returns:
            bool: True if peace established
        """
        war_key = tuple(sorted([faction_a, faction_b]))
        if war_key not in self._active_wars:
            return False  # Not at war

        # Set to neutral
        self.set_relationship(
            faction_a, faction_b,
            RelationshipType.NEUTRAL, -20.0, timestamp
        )
        self.set_relationship(
            faction_b, faction_a,
            RelationshipType.NEUTRAL, -20.0, timestamp
        )

        self._active_wars.remove(war_key)
        return True

    def form_alliance(
        self,
        faction_a: str,
        faction_b: str,
        timestamp: float
    ) -> bool:
        """
        Form an alliance between factions.

        Args:
            faction_a: First faction
            faction_b: Second faction
            timestamp: Current time

        Returns:
            bool: True if alliance formed
        """
        # Cannot ally if at war
        war_key = tuple(sorted([faction_a, faction_b]))
        if war_key in self._active_wars:
            return False

        # Set both to allied
        self.set_relationship(
            faction_a, faction_b,
            RelationshipType.ALLIED, 60.0, timestamp
        )
        self.set_relationship(
            faction_b, faction_a,
            RelationshipType.ALLIED, 60.0, timestamp
        )

        return True

    def establish_trade_agreement(
        self,
        faction_a: str,
        faction_b: str,
        duration: float,
        timestamp: float
    ) -> bool:
        """
        Establish a trade agreement.

        Args:
            faction_a: First faction
            faction_b: Second faction
            duration: How long agreement lasts
            timestamp: Current time

        Returns:
            bool: True if agreement established
        """
        trade_key = tuple(sorted([faction_a, faction_b]))

        # Set as trading partners
        self.set_relationship(
            faction_a, faction_b,
            RelationshipType.TRADING_PARTNER, 30.0, timestamp
        )
        self.set_relationship(
            faction_b, faction_a,
            RelationshipType.TRADING_PARTNER, 30.0, timestamp
        )

        self._trade_agreements[trade_key] = timestamp + duration
        return True

    def are_at_war(self, faction_a: str, faction_b: str) -> bool:
        """Check if two factions are at war."""
        war_key = tuple(sorted([faction_a, faction_b]))
        return war_key in self._active_wars

    def get_wars(self, faction_id: str) -> List[str]:
        """Get IDs of factions this faction is at war with."""
        wars = []
        for war_key in self._active_wars:
            if faction_id in war_key:
                other = war_key[0] if war_key[1] == faction_id else war_key[1]
                wars.append(other)
        return wars
