"""
Social Entity Module - Abstract Base for Social Structures

This module provides abstract base classes for all social structures in the
simulation (factions, groups, alliances, etc.).

Design Patterns:
    - Abstract Base Class: Defines interface for all social entities
    - Template Method: Lifecycle operations (join/leave) have standard flow
    - Observer: Members can observe entity changes

SOLID Principles:
    - Single Responsibility: Manages only social entity structure
    - Open/Closed: New entity types extend without modifying base
    - Liskov Substitution: All subclasses are substitutable
    - Interface Segregation: Separate interfaces for different capabilities
    - Dependency Inversion: Depends on abstractions (Agent via ID)
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Set, List, Dict, Any, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum
import uuid

if TYPE_CHECKING:
    from agents.agent import Agent


class SocialEntityType(Enum):
    """
    Types of social entities in the simulation.

    Attributes:
        FACTION: Formal organization with hierarchy, roles, shared resources
        GROUP: Informal collection of agents with common purpose
        ALLIANCE: Coalition of factions with shared goals
        TRADE_GUILD: Economic cooperation entity
    """
    FACTION = "faction"
    GROUP = "group"
    ALLIANCE = "alliance"
    TRADE_GUILD = "trade_guild"


class MembershipRole(Enum):
    """
    Roles within a social entity.

    Attributes:
        LEADER: Full control, can promote/demote others
        OFFICER: Can invite/expel, manage resources
        MEMBER: Standard membership, can participate
        RECRUIT: Probationary member, limited privileges
    """
    LEADER = "leader"
    OFFICER = "officer"
    MEMBER = "member"
    RECRUIT = "recruit"


@dataclass(frozen=True)
class Membership:
    """
    Immutable record of an agent's membership in a social entity.

    Attributes:
        agent_id: Unique identifier of the member
        entity_id: ID of the social entity
        role: Member's role in the entity
        joined_at: Timestamp when member joined
        invited_by: Agent ID who invited this member (None if founder)

    Note:
        Frozen dataclass ensures membership records cannot be modified,
        supporting the Immutable pattern used throughout the codebase.
    """
    agent_id: str
    entity_id: str
    role: MembershipRole
    joined_at: float
    invited_by: Optional[str] = None


class SocialEntityObserver(ABC):
    """
    Observer interface for social entity changes.

    Implements Observer pattern to notify interested parties
    of membership changes, role updates, and other events.
    """

    @abstractmethod
    def on_member_joined(self, entity_id: str, member_id: str, role: MembershipRole) -> None:
        """Called when a new member joins."""
        pass

    @abstractmethod
    def on_member_left(self, entity_id: str, member_id: str, reason: str) -> None:
        """Called when a member leaves or is expelled."""
        pass

    @abstractmethod
    def on_role_changed(self, entity_id: str, member_id: str, old_role: MembershipRole, new_role: MembershipRole) -> None:
        """Called when a member's role changes."""
        pass


class SocialEntity(ABC):
    """
    Abstract base class for all social structures.

    Social entities are collections of agents with:
    - Membership management (join, leave, invite, expel)
    - Role hierarchy (leader, officers, members, recruits)
    - Shared identity and goals

    This class defines the interface that all social structures must
    implement while providing common functionality.

    Attributes:
        entity_id (str): Unique identifier
        name (str): Human-readable name
        entity_type (SocialEntityType): Type of social entity
        created_at (float): Timestamp of creation

    Subclasses:
        - Faction: Formal organization with territory, resources
        - Group: Informal collection with common purpose
        - Alliance: Coalition of multiple factions

    Note:
        Uses Template Method pattern for join/leave operations,
        with hooks for subclass-specific validation and effects.
    """

    def __init__(
        self,
        name: str,
        entity_type: SocialEntityType,
        founder_id: str,
        created_at: float
    ) -> None:
        """
        Initialize a social entity.

        Args:
            name: Human-readable name
            entity_type: Type of social entity
            founder_id: Agent ID of the founder (becomes leader)
            created_at: Simulation timestamp of creation
        """
        self._entity_id: str = str(uuid.uuid4())
        self._name: str = name
        self._entity_type: SocialEntityType = entity_type
        self._created_at: float = created_at

        # Member tracking: agent_id -> Membership
        self._members: Dict[str, Membership] = {}

        # Observer pattern
        self._observers: List[SocialEntityObserver] = []

        # Add founder as leader
        self._add_member_internal(founder_id, MembershipRole.LEADER, created_at, None)

    # --- Properties ---

    @property
    def entity_id(self) -> str:
        """Get the unique entity identifier."""
        return self._entity_id

    @property
    def name(self) -> str:
        """Get the entity name."""
        return self._name

    @property
    def entity_type(self) -> SocialEntityType:
        """Get the entity type."""
        return self._entity_type

    @property
    def created_at(self) -> float:
        """Get creation timestamp."""
        return self._created_at

    @property
    def member_count(self) -> int:
        """Get the number of members."""
        return len(self._members)

    @property
    def member_ids(self) -> Set[str]:
        """Get a copy of all member IDs."""
        return set(self._members.keys())

    # --- Observer Pattern ---

    def add_observer(self, observer: SocialEntityObserver) -> None:
        """Register an observer for entity changes."""
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: SocialEntityObserver) -> None:
        """Unregister an observer."""
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify_member_joined(self, member_id: str, role: MembershipRole) -> None:
        """Notify observers of new member."""
        for observer in self._observers:
            observer.on_member_joined(self._entity_id, member_id, role)

    def _notify_member_left(self, member_id: str, reason: str) -> None:
        """Notify observers of departing member."""
        for observer in self._observers:
            observer.on_member_left(self._entity_id, member_id, reason)

    def _notify_role_changed(self, member_id: str, old_role: MembershipRole, new_role: MembershipRole) -> None:
        """Notify observers of role change."""
        for observer in self._observers:
            observer.on_role_changed(self._entity_id, member_id, old_role, new_role)

    # --- Membership Queries ---

    def is_member(self, agent_id: str) -> bool:
        """Check if agent is a member."""
        return agent_id in self._members

    def get_membership(self, agent_id: str) -> Optional[Membership]:
        """
        Get membership record for an agent.

        Args:
            agent_id: Agent to look up

        Returns:
            Membership record or None if not a member
        """
        return self._members.get(agent_id)

    def get_role(self, agent_id: str) -> Optional[MembershipRole]:
        """Get an agent's role, or None if not a member."""
        membership = self._members.get(agent_id)
        return membership.role if membership else None

    def get_members_by_role(self, role: MembershipRole) -> Set[str]:
        """Get all member IDs with a specific role."""
        return {
            agent_id for agent_id, membership in self._members.items()
            if membership.role == role
        }

    def get_leader_id(self) -> Optional[str]:
        """Get the leader's agent ID."""
        leaders = self.get_members_by_role(MembershipRole.LEADER)
        return next(iter(leaders), None) if leaders else None

    # --- Template Method: Join ---

    def join(
        self,
        agent_id: str,
        invited_by: Optional[str],
        timestamp: float
    ) -> bool:
        """
        Template method for joining the entity.

        Flow:
        1. Validate join request (can_join hook)
        2. Determine initial role (get_initial_role hook)
        3. Add member
        4. Apply join effects (on_join hook)
        5. Notify observers

        Args:
            agent_id: Agent requesting to join
            invited_by: Agent who invited (None for open join)
            timestamp: Current simulation time

        Returns:
            bool: True if join succeeded
        """
        # Hook: Can this agent join?
        if not self.can_join(agent_id, invited_by):
            return False

        # Already a member?
        if self.is_member(agent_id):
            return False

        # Hook: What role do they start with?
        initial_role = self.get_initial_role(agent_id, invited_by)

        # Add the member
        self._add_member_internal(agent_id, initial_role, timestamp, invited_by)

        # Hook: Apply any join effects
        self.on_join(agent_id, initial_role)

        # Notify observers
        self._notify_member_joined(agent_id, initial_role)

        return True

    def _add_member_internal(
        self,
        agent_id: str,
        role: MembershipRole,
        timestamp: float,
        invited_by: Optional[str]
    ) -> None:
        """Internal method to add a member."""
        membership = Membership(
            agent_id=agent_id,
            entity_id=self._entity_id,
            role=role,
            joined_at=timestamp,
            invited_by=invited_by
        )
        self._members[agent_id] = membership

    # --- Template Method: Leave ---

    def leave(self, agent_id: str, reason: str = "voluntary") -> bool:
        """
        Template method for leaving the entity.

        Flow:
        1. Validate leave request (can_leave hook)
        2. Apply leave effects (on_leave hook)
        3. Remove member
        4. Handle if leader left (handle_leader_departure hook)
        5. Notify observers

        Args:
            agent_id: Agent requesting to leave
            reason: Reason for departure (voluntary, expelled, etc.)

        Returns:
            bool: True if leave succeeded
        """
        if not self.is_member(agent_id):
            return False

        # Hook: Can this agent leave?
        if not self.can_leave(agent_id):
            return False

        membership = self._members[agent_id]
        was_leader = membership.role == MembershipRole.LEADER

        # Hook: Apply leave effects
        self.on_leave(agent_id, reason)

        # Remove member
        del self._members[agent_id]

        # Handle leader departure
        if was_leader and self._members:
            self.handle_leader_departure()

        # Notify observers
        self._notify_member_left(agent_id, reason)

        return True

    def expel(self, agent_id: str, expelled_by: str) -> bool:
        """
        Expel a member from the entity.

        Only officers and leaders can expel members of lower rank.

        Args:
            agent_id: Agent to expel
            expelled_by: Agent performing the expulsion

        Returns:
            bool: True if expulsion succeeded
        """
        if not self.can_expel(expelled_by, agent_id):
            return False

        return self.leave(agent_id, reason=f"expelled by {expelled_by}")

    # --- Role Management ---

    def change_role(
        self,
        agent_id: str,
        new_role: MembershipRole,
        changed_by: str
    ) -> bool:
        """
        Change a member's role.

        Only leaders can promote to officer. Only officers+ can demote.

        Args:
            agent_id: Agent whose role is changing
            new_role: The new role
            changed_by: Agent performing the change

        Returns:
            bool: True if role change succeeded
        """
        if not self.can_change_role(changed_by, agent_id, new_role):
            return False

        if agent_id not in self._members:
            return False

        old_membership = self._members[agent_id]
        old_role = old_membership.role

        if old_role == new_role:
            return False

        # Create new membership with updated role
        new_membership = Membership(
            agent_id=old_membership.agent_id,
            entity_id=old_membership.entity_id,
            role=new_role,
            joined_at=old_membership.joined_at,
            invited_by=old_membership.invited_by
        )
        self._members[agent_id] = new_membership

        # Notify observers
        self._notify_role_changed(agent_id, old_role, new_role)

        return True

    # --- Abstract Hook Methods (subclasses implement) ---

    @abstractmethod
    def can_join(self, agent_id: str, invited_by: Optional[str]) -> bool:
        """
        Hook: Validate if agent can join.

        Subclasses implement join requirements (invitation needed,
        capacity limits, reputation requirements, etc.)

        Args:
            agent_id: Agent requesting to join
            invited_by: Agent who invited (None for open join)

        Returns:
            bool: True if join is allowed
        """
        pass

    @abstractmethod
    def get_initial_role(self, agent_id: str, invited_by: Optional[str]) -> MembershipRole:
        """
        Hook: Determine starting role for new member.

        Args:
            agent_id: New member
            invited_by: Who invited them

        Returns:
            MembershipRole: Starting role
        """
        pass

    @abstractmethod
    def can_leave(self, agent_id: str) -> bool:
        """
        Hook: Validate if agent can leave.

        Subclasses may prevent leaving (e.g., during war,
        if only member, etc.)

        Args:
            agent_id: Agent requesting to leave

        Returns:
            bool: True if leave is allowed
        """
        pass

    @abstractmethod
    def on_join(self, agent_id: str, role: MembershipRole) -> None:
        """
        Hook: Apply effects when member joins.

        Subclasses implement side effects (grant access to
        stockpiles, update reputation, etc.)

        Args:
            agent_id: New member
            role: Their initial role
        """
        pass

    @abstractmethod
    def on_leave(self, agent_id: str, reason: str) -> None:
        """
        Hook: Apply effects when member leaves.

        Subclasses implement cleanup (revoke access,
        update reputation, etc.)

        Args:
            agent_id: Departing member
            reason: Why they left
        """
        pass

    @abstractmethod
    def handle_leader_departure(self) -> None:
        """
        Hook: Handle succession when leader leaves.

        Subclasses implement leader succession rules
        (promote senior officer, election, dissolution, etc.)
        """
        pass

    @abstractmethod
    def can_expel(self, expelled_by: str, target: str) -> bool:
        """
        Hook: Validate if expulsion is allowed.

        Args:
            expelled_by: Agent performing expulsion
            target: Agent being expelled

        Returns:
            bool: True if expulsion is allowed
        """
        pass

    @abstractmethod
    def can_change_role(self, changed_by: str, target: str, new_role: MembershipRole) -> bool:
        """
        Hook: Validate if role change is allowed.

        Args:
            changed_by: Agent performing the change
            target: Agent whose role is changing
            new_role: The proposed new role

        Returns:
            bool: True if change is allowed
        """
        pass

    # --- String Representation ---

    def __repr__(self) -> str:
        return (
            f"{self.__class__.__name__}("
            f"id={self._entity_id[:8]}, "
            f"name='{self._name}', "
            f"members={self.member_count})"
        )

    def __str__(self) -> str:
        return f"{self._name} ({self._entity_type.value})"
