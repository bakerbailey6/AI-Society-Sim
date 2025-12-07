"""
Group Module - Informal Social Collections

This module provides the Group class for informal collections of agents
with common purpose but without formal hierarchy.

Design Patterns:
    - Template Method: Inherits join/leave flow from SocialEntity

SOLID Principles:
    - Single Responsibility: Manages informal group structure
    - Liskov Substitution: Fully substitutable for SocialEntity
"""

from __future__ import annotations
from typing import Optional, Set
from dataclasses import dataclass
from enum import Enum

from social.social_entity import (
    SocialEntity,
    SocialEntityType,
    MembershipRole
)


class GroupPurpose(Enum):
    """
    Common purposes for informal groups.

    Attributes:
        HUNTING: Cooperative resource gathering
        EXPLORATION: Mapping and discovery
        DEFENSE: Mutual protection
        TRADE: Economic cooperation
        SOCIAL: General socialization
    """
    HUNTING = "hunting"
    EXPLORATION = "exploration"
    DEFENSE = "defense"
    TRADE = "trade"
    SOCIAL = "social"


@dataclass
class GroupSettings:
    """
    Configuration for group behavior.

    Attributes:
        max_size: Maximum members (0 = unlimited)
        open_membership: Whether anyone can join without invitation
        shared_vision: Whether members share sensor information
        auto_dissolve_empty: Dissolve when last member leaves
    """
    max_size: int = 10
    open_membership: bool = True
    shared_vision: bool = False
    auto_dissolve_empty: bool = True


class Group(SocialEntity):
    """
    Informal collection of agents with common purpose.

    Groups are lighter-weight than Factions:
    - Flat hierarchy (coordinator + members)
    - Temporary or purpose-driven
    - Easy to join and leave
    - No territory or formal resources

    Groups are useful for:
    - Hunting parties
    - Exploration teams
    - Temporary alliances
    - Social clusters

    Attributes:
        purpose: What the group is for
        settings: Group configuration

    Examples:
        >>> group = Group(
        ...     name="Northern Hunters",
        ...     founder_id="agent_001",
        ...     created_at=100.0,
        ...     purpose=GroupPurpose.HUNTING
        ... )
        >>> group.join("agent_002", invited_by=None, timestamp=101.0)
        True  # Open membership allows this

    Note:
        Groups use simplified roles - LEADER acts as coordinator,
        everyone else is MEMBER. No officers or recruits.
    """

    def __init__(
        self,
        name: str,
        founder_id: str,
        created_at: float,
        purpose: GroupPurpose = GroupPurpose.SOCIAL,
        settings: GroupSettings = None
    ) -> None:
        """
        Initialize a group.

        Args:
            name: Group name
            founder_id: Agent ID of founder (becomes coordinator)
            created_at: Simulation timestamp
            purpose: Group's purpose
            settings: Group configuration
        """
        super().__init__(
            name=name,
            entity_type=SocialEntityType.GROUP,
            founder_id=founder_id,
            created_at=created_at
        )

        self._purpose = purpose
        self._settings = settings if settings else GroupSettings()

        # Shared goals/objectives for the group
        self._objectives: list = []

    # --- Properties ---

    @property
    def purpose(self) -> GroupPurpose:
        """Get group purpose."""
        return self._purpose

    @property
    def settings(self) -> GroupSettings:
        """Get group settings."""
        return self._settings

    @property
    def coordinator_id(self) -> Optional[str]:
        """Get the coordinator (leader) ID."""
        return self.get_leader_id()

    @property
    def objectives(self) -> list:
        """Get a copy of group objectives."""
        return self._objectives.copy()

    # --- Objective Management ---

    def add_objective(self, objective: str) -> None:
        """Add a group objective."""
        self._objectives.append(objective)

    def complete_objective(self, objective: str) -> bool:
        """Mark an objective as complete (remove it)."""
        if objective in self._objectives:
            self._objectives.remove(objective)
            return True
        return False

    def clear_objectives(self) -> None:
        """Clear all objectives."""
        self._objectives.clear()

    # --- Coordinator Transfer ---

    def transfer_coordinator(self, new_coordinator_id: str) -> bool:
        """
        Transfer coordinator role to another member.

        Args:
            new_coordinator_id: New coordinator's agent ID

        Returns:
            bool: True if transfer succeeded
        """
        if not self.is_member(new_coordinator_id):
            return False

        old_coordinator_id = self.coordinator_id
        if old_coordinator_id is None:
            return False

        # Demote old coordinator to member
        self.change_role(old_coordinator_id, MembershipRole.MEMBER, changed_by=self._entity_id)

        # Promote new coordinator
        self.change_role(new_coordinator_id, MembershipRole.LEADER, changed_by=self._entity_id)

        return True

    # --- SocialEntity Hook Implementations ---

    def can_join(self, agent_id: str, invited_by: Optional[str]) -> bool:
        """
        Validate if agent can join.

        Groups with open membership accept anyone.
        Checks capacity limits.
        """
        # Check capacity
        if self._settings.max_size > 0:
            if self.member_count >= self._settings.max_size:
                return False

        # If not open, require invitation from coordinator
        if not self._settings.open_membership:
            if invited_by != self.coordinator_id:
                return False

        return True

    def get_initial_role(self, agent_id: str, invited_by: Optional[str]) -> MembershipRole:
        """
        Determine starting role.

        Groups use flat structure - everyone is MEMBER except coordinator.
        """
        return MembershipRole.MEMBER

    def can_leave(self, agent_id: str) -> bool:
        """
        Validate if agent can leave.

        Anyone can leave a group at any time.
        If coordinator leaves, leadership transfers.
        """
        return True

    def on_join(self, agent_id: str, role: MembershipRole) -> None:
        """Apply effects when member joins."""
        # Groups are lightweight - no special join effects
        pass

    def on_leave(self, agent_id: str, reason: str) -> None:
        """Apply effects when member leaves."""
        # Groups are lightweight - no special leave effects
        pass

    def handle_leader_departure(self) -> None:
        """
        Handle when coordinator leaves.

        Promote longest-serving member to coordinator.
        If no members remain and auto_dissolve_empty, group dissolves.
        """
        members = list(self.get_members_by_role(MembershipRole.MEMBER))

        if not members:
            # No members left
            if self._settings.auto_dissolve_empty:
                pass  # Group will dissolve naturally
            return

        # Find longest-serving member
        earliest_id = None
        earliest_time = float('inf')
        for member_id in members:
            membership = self.get_membership(member_id)
            if membership and membership.joined_at < earliest_time:
                earliest_time = membership.joined_at
                earliest_id = member_id

        if earliest_id:
            self.change_role(earliest_id, MembershipRole.LEADER, changed_by=self._entity_id)

    def can_expel(self, expelled_by: str, target: str) -> bool:
        """
        Validate if expulsion is allowed.

        Only coordinator can expel members.
        Cannot expel yourself.
        """
        if expelled_by == target:
            return False

        return self.get_role(expelled_by) == MembershipRole.LEADER

    def can_change_role(self, changed_by: str, target: str, new_role: MembershipRole) -> bool:
        """
        Validate if role change is allowed.

        Groups only have LEADER and MEMBER roles.
        Only coordinator (or system) can change roles.
        """
        # Groups only use LEADER and MEMBER
        if new_role not in (MembershipRole.LEADER, MembershipRole.MEMBER):
            return False

        changer_role = self.get_role(changed_by)

        # Coordinator or system (entity_id) can change roles
        return changer_role == MembershipRole.LEADER or changed_by == self._entity_id

    # --- String Representation ---

    def __repr__(self) -> str:
        return (
            f"Group("
            f"id={self._entity_id[:8]}, "
            f"name='{self._name}', "
            f"purpose={self._purpose.value}, "
            f"members={self.member_count})"
        )
