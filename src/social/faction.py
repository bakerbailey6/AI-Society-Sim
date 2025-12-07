"""
Faction Module - Formal Social Organizations

This module provides the Faction class for formal organizations with
hierarchy, shared resources, territory, and governance.

Design Patterns:
    - Template Method: Inherits join/leave flow from SocialEntity
    - Observer: Inherits observer pattern from SocialEntity
    - Strategy: Governance style can be swapped

SOLID Principles:
    - Single Responsibility: Manages formal organization structure
    - Liskov Substitution: Fully substitutable for SocialEntity
    - Open/Closed: Governance strategies are extensible
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Set, List, Dict, TYPE_CHECKING
from dataclasses import dataclass
from enum import Enum

from social.social_entity import (
    SocialEntity,
    SocialEntityType,
    MembershipRole,
    Membership
)

if TYPE_CHECKING:
    from world.position import Position
    from inventory.stockpile import Stockpile


class GovernanceType(Enum):
    """
    Types of faction governance.

    Affects decision-making, succession, and member rights.

    Attributes:
        AUTOCRACY: Leader has absolute power
        OLIGARCHY: Council of officers makes decisions
        DEMOCRACY: Members vote on decisions
        MERITOCRACY: Decisions based on contribution
    """
    AUTOCRACY = "autocracy"
    OLIGARCHY = "oligarchy"
    DEMOCRACY = "democracy"
    MERITOCRACY = "meritocracy"


class GovernanceStrategy(ABC):
    """
    Abstract strategy for faction governance.

    Determines how decisions are made and who has authority.
    Implements Strategy pattern for interchangeable governance styles.
    """

    @abstractmethod
    def can_make_decision(self, faction: Faction, agent_id: str, decision_type: str) -> bool:
        """
        Check if agent can make a specific type of decision.

        Args:
            faction: The faction
            agent_id: Agent attempting decision
            decision_type: Type of decision (invite, expel, war, trade, etc.)

        Returns:
            bool: True if agent has authority
        """
        pass

    @abstractmethod
    def handle_succession(self, faction: Faction) -> Optional[str]:
        """
        Determine new leader when current leader departs.

        Args:
            faction: The faction needing new leader

        Returns:
            Optional[str]: New leader's agent ID, or None to dissolve
        """
        pass

    @abstractmethod
    def governance_type(self) -> GovernanceType:
        """Get the governance type."""
        pass


class AutocracyGovernance(GovernanceStrategy):
    """
    Autocratic governance - leader has absolute power.

    Only the leader can make major decisions.
    Succession goes to longest-serving officer.
    """

    def can_make_decision(self, faction: Faction, agent_id: str, decision_type: str) -> bool:
        """Only leader can make decisions."""
        role = faction.get_role(agent_id)
        if role == MembershipRole.LEADER:
            return True
        # Officers can only invite/expel
        if role == MembershipRole.OFFICER and decision_type in ("invite", "expel_member"):
            return True
        return False

    def handle_succession(self, faction: Faction) -> Optional[str]:
        """Promote longest-serving officer."""
        officers = faction.get_members_by_role(MembershipRole.OFFICER)
        if not officers:
            # Promote longest-serving member
            members = faction.get_members_by_role(MembershipRole.MEMBER)
            if not members:
                return None  # Faction dissolves
            # Find earliest joiner
            earliest_id = None
            earliest_time = float('inf')
            for member_id in members:
                membership = faction.get_membership(member_id)
                if membership and membership.joined_at < earliest_time:
                    earliest_time = membership.joined_at
                    earliest_id = member_id
            return earliest_id

        # Find earliest joining officer
        earliest_id = None
        earliest_time = float('inf')
        for officer_id in officers:
            membership = faction.get_membership(officer_id)
            if membership and membership.joined_at < earliest_time:
                earliest_time = membership.joined_at
                earliest_id = officer_id
        return earliest_id

    def governance_type(self) -> GovernanceType:
        return GovernanceType.AUTOCRACY


class OligarchyGovernance(GovernanceStrategy):
    """
    Oligarchic governance - council of officers rule.

    Officers collectively make decisions.
    Succession promotes from officer pool.
    """

    def can_make_decision(self, faction: Faction, agent_id: str, decision_type: str) -> bool:
        """Officers and leader can make decisions."""
        role = faction.get_role(agent_id)
        return role in (MembershipRole.LEADER, MembershipRole.OFFICER)

    def handle_succession(self, faction: Faction) -> Optional[str]:
        """Rotate to next officer."""
        officers = list(faction.get_members_by_role(MembershipRole.OFFICER))
        if officers:
            # Just pick first officer (could implement voting)
            return officers[0]
        return None

    def governance_type(self) -> GovernanceType:
        return GovernanceType.OLIGARCHY


class DemocracyGovernance(GovernanceStrategy):
    """
    Democratic governance - members vote on decisions.

    Major decisions require member approval.
    Succession determined by election.
    """

    def can_make_decision(self, faction: Faction, agent_id: str, decision_type: str) -> bool:
        """
        All members can propose, but major decisions need votes.

        For now, returns True for members and above.
        Actual voting logic would be implemented in Faction.
        """
        role = faction.get_role(agent_id)
        return role in (MembershipRole.LEADER, MembershipRole.OFFICER, MembershipRole.MEMBER)

    def handle_succession(self, faction: Faction) -> Optional[str]:
        """
        Would trigger election - for now promotes random member.

        Full implementation would track votes.
        """
        members = list(faction.get_members_by_role(MembershipRole.MEMBER))
        officers = list(faction.get_members_by_role(MembershipRole.OFFICER))
        candidates = officers + members
        if candidates:
            return candidates[0]  # Placeholder for election
        return None

    def governance_type(self) -> GovernanceType:
        return GovernanceType.DEMOCRACY


class MeritocracyGovernance(GovernanceStrategy):
    """
    Meritocratic governance - authority based on contribution.

    Decision power scales with faction contribution.
    Succession goes to highest contributor.
    """

    def can_make_decision(self, faction: Faction, agent_id: str, decision_type: str) -> bool:
        """
        Decision power based on contribution.

        For now, uses role as proxy. Full implementation would
        check contribution scores.
        """
        role = faction.get_role(agent_id)
        if role == MembershipRole.LEADER:
            return True
        if role == MembershipRole.OFFICER:
            return True
        # Members could make minor decisions based on contribution
        return False

    def handle_succession(self, faction: Faction) -> Optional[str]:
        """
        Promote highest contributor.

        Would use contribution tracking. For now, uses officer.
        """
        officers = list(faction.get_members_by_role(MembershipRole.OFFICER))
        if officers:
            return officers[0]
        return None

    def governance_type(self) -> GovernanceType:
        return GovernanceType.MERITOCRACY


@dataclass
class FactionPolicy:
    """
    Faction policies that govern behavior.

    Attributes:
        accept_recruits: Whether faction accepts new members
        require_invitation: Whether invitation is required to join
        share_stockpiles: Whether members share access to stockpiles
        minimum_reputation: Minimum reputation to join
        max_members: Maximum number of members (0 = unlimited)
    """
    accept_recruits: bool = True
    require_invitation: bool = True
    share_stockpiles: bool = True
    minimum_reputation: float = 0.0
    max_members: int = 0  # 0 = unlimited


class Faction(SocialEntity):
    """
    Formal organization with hierarchy, resources, and territory.

    Factions are the primary social structure for agent cooperation.
    They provide:
    - Hierarchical membership (leader, officers, members, recruits)
    - Shared resource stockpiles
    - Territory control
    - Governance structure
    - Inter-faction relationships

    Attributes:
        governance: Strategy determining how decisions are made
        policies: Rules governing faction behavior
        territory: Set of positions the faction controls
        stockpile_ids: IDs of stockpiles owned by faction

    Examples:
        >>> governance = AutocracyGovernance()
        >>> faction = Faction(
        ...     name="Iron Brotherhood",
        ...     founder_id="agent_001",
        ...     created_at=100.0,
        ...     governance=governance
        ... )
        >>> faction.join("agent_002", invited_by="agent_001", timestamp=101.0)
        True

    Note:
        Integrates with existing FactionAccess strategy in stockpile.py.
        The faction tracks members, and FactionAccess uses that for
        access control.
    """

    def __init__(
        self,
        name: str,
        founder_id: str,
        created_at: float,
        governance: GovernanceStrategy = None,
        policies: FactionPolicy = None
    ) -> None:
        """
        Initialize a faction.

        Args:
            name: Faction name
            founder_id: Agent ID of founder (becomes leader)
            created_at: Simulation timestamp
            governance: Governance strategy (default: Autocracy)
            policies: Faction policies (default: standard policies)
        """
        super().__init__(
            name=name,
            entity_type=SocialEntityType.FACTION,
            founder_id=founder_id,
            created_at=created_at
        )

        self._governance = governance if governance else AutocracyGovernance()
        self._policies = policies if policies else FactionPolicy()

        # Territory tracking
        self._territory: Set[tuple] = set()  # Set of (x, y) tuples

        # Stockpile references
        self._stockpile_ids: Set[str] = set()

        # Pending invitations: invited_agent_id -> inviter_agent_id
        self._pending_invitations: Dict[str, str] = {}

    # --- Properties ---

    @property
    def governance(self) -> GovernanceStrategy:
        """Get governance strategy."""
        return self._governance

    @property
    def governance_type(self) -> GovernanceType:
        """Get governance type."""
        return self._governance.governance_type()

    @property
    def policies(self) -> FactionPolicy:
        """Get faction policies."""
        return self._policies

    @property
    def territory(self) -> Set[tuple]:
        """Get a copy of territory positions."""
        return self._territory.copy()

    @property
    def territory_size(self) -> int:
        """Get number of controlled positions."""
        return len(self._territory)

    @property
    def stockpile_ids(self) -> Set[str]:
        """Get a copy of stockpile IDs."""
        return self._stockpile_ids.copy()

    # --- Territory Management ---

    def claim_territory(self, x: int, y: int) -> bool:
        """
        Claim a position as faction territory.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            bool: True if claimed (always succeeds currently)
        """
        self._territory.add((x, y))
        return True

    def release_territory(self, x: int, y: int) -> bool:
        """
        Release a position from faction territory.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            bool: True if was in territory
        """
        if (x, y) in self._territory:
            self._territory.discard((x, y))
            return True
        return False

    def is_in_territory(self, x: int, y: int) -> bool:
        """Check if position is in faction territory."""
        return (x, y) in self._territory

    # --- Stockpile Management ---

    def add_stockpile(self, stockpile_id: str) -> None:
        """Associate a stockpile with this faction."""
        self._stockpile_ids.add(stockpile_id)

    def remove_stockpile(self, stockpile_id: str) -> None:
        """Disassociate a stockpile from this faction."""
        self._stockpile_ids.discard(stockpile_id)

    # --- Invitation System ---

    def invite(self, inviter_id: str, invited_id: str) -> bool:
        """
        Invite an agent to join the faction.

        Args:
            inviter_id: Agent sending invitation
            invited_id: Agent being invited

        Returns:
            bool: True if invitation sent
        """
        # Check inviter has authority
        if not self._governance.can_make_decision(self, inviter_id, "invite"):
            return False

        # Check if already member
        if self.is_member(invited_id):
            return False

        # Check if already invited
        if invited_id in self._pending_invitations:
            return False

        self._pending_invitations[invited_id] = inviter_id
        return True

    def has_invitation(self, agent_id: str) -> bool:
        """Check if agent has a pending invitation."""
        return agent_id in self._pending_invitations

    def cancel_invitation(self, agent_id: str) -> bool:
        """Cancel a pending invitation."""
        if agent_id in self._pending_invitations:
            del self._pending_invitations[agent_id]
            return True
        return False

    # --- Governance Delegation ---

    def can_make_decision(self, agent_id: str, decision_type: str) -> bool:
        """
        Check if agent can make a specific decision.

        Delegates to governance strategy.

        Args:
            agent_id: Agent attempting decision
            decision_type: Type of decision

        Returns:
            bool: True if authorized
        """
        return self._governance.can_make_decision(self, agent_id, decision_type)

    # --- SocialEntity Hook Implementations ---

    def can_join(self, agent_id: str, invited_by: Optional[str]) -> bool:
        """
        Validate if agent can join.

        Checks:
        - Faction is accepting recruits
        - Invitation requirement is met
        - Member capacity not exceeded
        """
        # Check if accepting recruits
        if not self._policies.accept_recruits:
            return False

        # Check capacity
        if self._policies.max_members > 0:
            if self.member_count >= self._policies.max_members:
                return False

        # Check invitation requirement
        if self._policies.require_invitation:
            # Must have pending invitation
            if agent_id not in self._pending_invitations:
                return False

        return True

    def get_initial_role(self, agent_id: str, invited_by: Optional[str]) -> MembershipRole:
        """
        Determine starting role.

        New members start as RECRUIT. After probation they
        become MEMBER.
        """
        return MembershipRole.RECRUIT

    def can_leave(self, agent_id: str) -> bool:
        """
        Validate if agent can leave.

        Leaders cannot leave unless they transfer leadership first,
        or they are the last member.
        """
        if self.member_count == 1:
            return True  # Last member can always leave (dissolves faction)

        role = self.get_role(agent_id)
        if role == MembershipRole.LEADER:
            # Leader must transfer leadership first
            return False

        return True

    def on_join(self, agent_id: str, role: MembershipRole) -> None:
        """
        Apply effects when member joins.

        - Clear pending invitation
        - Grant stockpile access (via FactionAccess integration)
        """
        # Clear invitation if exists
        if agent_id in self._pending_invitations:
            del self._pending_invitations[agent_id]

        # Note: Stockpile access is managed by FactionAccess strategy
        # which queries faction membership directly

    def on_leave(self, agent_id: str, reason: str) -> None:
        """
        Apply effects when member leaves.

        - Revoke stockpile access (automatic via FactionAccess)
        """
        # FactionAccess will automatically deny access since
        # agent is no longer in faction's member list
        pass

    def handle_leader_departure(self) -> None:
        """
        Handle succession when leader leaves.

        Delegates to governance strategy.
        """
        new_leader_id = self._governance.handle_succession(self)

        if new_leader_id is None:
            # Faction dissolves - would need to handle this
            pass
        else:
            # Promote new leader
            self.change_role(new_leader_id, MembershipRole.LEADER, changed_by=self._entity_id)

    def can_expel(self, expelled_by: str, target: str) -> bool:
        """
        Validate if expulsion is allowed.

        Rules:
        - Cannot expel yourself
        - Cannot expel leader
        - Must have higher role than target
        - Must have expel authority
        """
        if expelled_by == target:
            return False

        if not self._governance.can_make_decision(self, expelled_by, "expel_member"):
            return False

        expeller_role = self.get_role(expelled_by)
        target_role = self.get_role(target)

        if target_role is None:
            return False

        if target_role == MembershipRole.LEADER:
            return False

        # Role hierarchy: LEADER > OFFICER > MEMBER > RECRUIT
        role_order = {
            MembershipRole.LEADER: 4,
            MembershipRole.OFFICER: 3,
            MembershipRole.MEMBER: 2,
            MembershipRole.RECRUIT: 1
        }

        return role_order.get(expeller_role, 0) > role_order.get(target_role, 0)

    def can_change_role(self, changed_by: str, target: str, new_role: MembershipRole) -> bool:
        """
        Validate if role change is allowed.

        Rules:
        - Only leader can promote to OFFICER
        - Only leader can transfer leadership
        - Officers can promote RECRUIT to MEMBER
        - Cannot change own role
        """
        if changed_by == target and new_role != MembershipRole.LEADER:
            return False  # Can't change own role (except resign leadership)

        changer_role = self.get_role(changed_by)
        target_role = self.get_role(target)

        if changer_role is None or target_role is None:
            return False

        # Only leader can make someone else leader
        if new_role == MembershipRole.LEADER:
            return changer_role == MembershipRole.LEADER

        # Only leader can promote to officer
        if new_role == MembershipRole.OFFICER:
            return changer_role == MembershipRole.LEADER

        # Officers can promote recruits to members
        if new_role == MembershipRole.MEMBER and target_role == MembershipRole.RECRUIT:
            return changer_role in (MembershipRole.LEADER, MembershipRole.OFFICER)

        return changer_role == MembershipRole.LEADER

    # --- String Representation ---

    def __repr__(self) -> str:
        return (
            f"Faction("
            f"id={self._entity_id[:8]}, "
            f"name='{self._name}', "
            f"gov={self.governance_type.value}, "
            f"members={self.member_count}, "
            f"territory={self.territory_size})"
        )
