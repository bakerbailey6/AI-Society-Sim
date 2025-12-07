"""
Reputation Module - Agent Standing with Factions

This module provides systems for tracking agent reputation/standing
with factions and the effects of reputation levels.

Design Patterns:
    - Immutable: Reputation records are frozen dataclasses
    - Strategy: Reputation effects can vary by faction
    - Observer: Reputation changes trigger notifications

SOLID Principles:
    - Single Responsibility: Manages only reputation tracking
    - Open/Closed: Reputation tiers and effects are extensible
    - Interface Segregation: Separate interfaces for different queries
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, Dict, List, Tuple, TYPE_CHECKING
from dataclasses import dataclass, field
from enum import Enum

if TYPE_CHECKING:
    from agents.agent import Agent
    from social.faction import Faction


class ReputationTier(Enum):
    """
    Tiers of reputation standing.

    Each tier grants different privileges and restrictions.

    Attributes:
        EXALTED: Highest standing, full privileges
        HONORED: High standing, significant privileges
        FRIENDLY: Positive standing, minor privileges
        NEUTRAL: Default standing, no modifiers
        UNFRIENDLY: Negative standing, minor restrictions
        HOSTILE: Low standing, significant restrictions
        HATED: Lowest standing, severe restrictions
    """
    EXALTED = "exalted"
    HONORED = "honored"
    FRIENDLY = "friendly"
    NEUTRAL = "neutral"
    UNFRIENDLY = "unfriendly"
    HOSTILE = "hostile"
    HATED = "hated"


@dataclass(frozen=True)
class ReputationThresholds:
    """
    Thresholds for reputation tier transitions.

    Defines the reputation values where tier changes occur.
    Frozen to ensure consistency.

    Attributes:
        exalted: Minimum for EXALTED (default: 1000)
        honored: Minimum for HONORED (default: 500)
        friendly: Minimum for FRIENDLY (default: 100)
        neutral_low: Minimum for NEUTRAL (default: -100)
        unfriendly: Minimum for UNFRIENDLY (default: -500)
        hostile: Minimum for HOSTILE (default: -1000)
        # Below hostile threshold is HATED
    """
    exalted: float = 1000.0
    honored: float = 500.0
    friendly: float = 100.0
    neutral_low: float = -100.0
    unfriendly: float = -500.0
    hostile: float = -1000.0

    def get_tier(self, reputation: float) -> ReputationTier:
        """
        Determine tier from reputation value.

        Args:
            reputation: Current reputation value

        Returns:
            ReputationTier corresponding to the value
        """
        if reputation >= self.exalted:
            return ReputationTier.EXALTED
        elif reputation >= self.honored:
            return ReputationTier.HONORED
        elif reputation >= self.friendly:
            return ReputationTier.FRIENDLY
        elif reputation >= self.neutral_low:
            return ReputationTier.NEUTRAL
        elif reputation >= self.unfriendly:
            return ReputationTier.UNFRIENDLY
        elif reputation >= self.hostile:
            return ReputationTier.HOSTILE
        else:
            return ReputationTier.HATED


@dataclass(frozen=True)
class ReputationChange:
    """
    Record of a reputation change event.

    Attributes:
        change_id: Unique identifier
        agent_id: Agent whose reputation changed
        faction_id: Faction with which reputation changed
        old_value: Previous reputation value
        new_value: New reputation value
        old_tier: Previous tier
        new_tier: New tier
        reason: What caused the change
        timestamp: When the change occurred
    """
    change_id: str
    agent_id: str
    faction_id: str
    old_value: float
    new_value: float
    old_tier: ReputationTier
    new_tier: ReputationTier
    reason: str
    timestamp: float


@dataclass
class AgentReputation:
    """
    An agent's reputation with a specific faction.

    Attributes:
        agent_id: The agent
        faction_id: The faction
        value: Current reputation value
        tier: Current reputation tier
        history: Record of changes
        total_gained: Total positive reputation earned
        total_lost: Total reputation lost
    """
    agent_id: str
    faction_id: str
    value: float = 0.0
    tier: ReputationTier = ReputationTier.NEUTRAL
    history: List[ReputationChange] = field(default_factory=list)
    total_gained: float = 0.0
    total_lost: float = 0.0


class ReputationObserver(ABC):
    """
    Observer interface for reputation changes.
    """

    @abstractmethod
    def on_reputation_changed(self, change: ReputationChange) -> None:
        """Called when reputation changes."""
        pass

    @abstractmethod
    def on_tier_changed(
        self,
        agent_id: str,
        faction_id: str,
        old_tier: ReputationTier,
        new_tier: ReputationTier
    ) -> None:
        """Called when reputation tier changes."""
        pass


class ReputationEffects(ABC):
    """
    Abstract strategy for reputation effects.

    Different factions may apply different effects
    based on reputation tier.
    """

    @abstractmethod
    def get_trade_modifier(self, tier: ReputationTier) -> float:
        """
        Get trade price modifier for tier.

        Returns:
            float: Multiplier for trade prices (1.0 = normal)
        """
        pass

    @abstractmethod
    def can_access_services(self, tier: ReputationTier) -> bool:
        """
        Check if tier allows access to faction services.

        Returns:
            bool: True if services are accessible
        """
        pass

    @abstractmethod
    def can_enter_territory(self, tier: ReputationTier) -> bool:
        """
        Check if tier allows entry to faction territory.

        Returns:
            bool: True if territory entry is allowed
        """
        pass

    @abstractmethod
    def is_attack_on_sight(self, tier: ReputationTier) -> bool:
        """
        Check if faction will attack agent on sight.

        Returns:
            bool: True if faction is hostile
        """
        pass


class StandardReputationEffects(ReputationEffects):
    """
    Standard reputation effects used by most factions.

    Trade modifiers:
        - EXALTED: 20% discount
        - HONORED: 10% discount
        - FRIENDLY: 5% discount
        - NEUTRAL: Normal prices
        - UNFRIENDLY: 10% markup
        - HOSTILE: 25% markup (if allowed)
        - HATED: No trade allowed
    """

    def get_trade_modifier(self, tier: ReputationTier) -> float:
        """Get trade price modifier."""
        modifiers = {
            ReputationTier.EXALTED: 0.80,
            ReputationTier.HONORED: 0.90,
            ReputationTier.FRIENDLY: 0.95,
            ReputationTier.NEUTRAL: 1.00,
            ReputationTier.UNFRIENDLY: 1.10,
            ReputationTier.HOSTILE: 1.25,
            ReputationTier.HATED: float('inf'),  # No trade
        }
        return modifiers.get(tier, 1.0)

    def can_access_services(self, tier: ReputationTier) -> bool:
        """Check service access."""
        return tier not in (ReputationTier.HOSTILE, ReputationTier.HATED)

    def can_enter_territory(self, tier: ReputationTier) -> bool:
        """Check territory access."""
        return tier != ReputationTier.HATED

    def is_attack_on_sight(self, tier: ReputationTier) -> bool:
        """Check if attacked on sight."""
        return tier == ReputationTier.HATED


class ReputationManager(ABC):
    """
    Abstract base for managing reputation.

    Provides interface for tracking and querying reputation.
    """

    @abstractmethod
    def get_reputation(self, agent_id: str, faction_id: str) -> AgentReputation:
        """
        Get agent's reputation with a faction.

        Args:
            agent_id: The agent
            faction_id: The faction

        Returns:
            AgentReputation (creates if doesn't exist)
        """
        pass

    @abstractmethod
    def adjust_reputation(
        self,
        agent_id: str,
        faction_id: str,
        delta: float,
        reason: str,
        timestamp: float
    ) -> ReputationChange:
        """
        Adjust reputation value.

        Args:
            agent_id: The agent
            faction_id: The faction
            delta: Amount to adjust (positive or negative)
            reason: Why reputation changed
            timestamp: Current simulation time

        Returns:
            ReputationChange record
        """
        pass

    @abstractmethod
    def set_reputation(
        self,
        agent_id: str,
        faction_id: str,
        value: float,
        reason: str,
        timestamp: float
    ) -> ReputationChange:
        """
        Set reputation to specific value.

        Args:
            agent_id: The agent
            faction_id: The faction
            value: New reputation value
            reason: Why reputation was set
            timestamp: Current simulation time

        Returns:
            ReputationChange record
        """
        pass

    @abstractmethod
    def get_tier(self, agent_id: str, faction_id: str) -> ReputationTier:
        """
        Get agent's reputation tier with faction.

        Args:
            agent_id: The agent
            faction_id: The faction

        Returns:
            ReputationTier
        """
        pass

    @abstractmethod
    def get_all_reputations(self, agent_id: str) -> Dict[str, AgentReputation]:
        """
        Get all reputations for an agent.

        Args:
            agent_id: The agent

        Returns:
            Dict mapping faction_id -> AgentReputation
        """
        pass


class InMemoryReputationManager(ReputationManager):
    """
    In-memory implementation of ReputationManager.
    """

    def __init__(
        self,
        thresholds: ReputationThresholds = None,
        effects: ReputationEffects = None
    ) -> None:
        """
        Initialize the reputation manager.

        Args:
            thresholds: Tier thresholds (default: standard)
            effects: Reputation effects strategy (default: standard)
        """
        self._thresholds = thresholds if thresholds else ReputationThresholds()
        self._effects = effects if effects else StandardReputationEffects()

        # Nested dict: agent_id -> faction_id -> AgentReputation
        self._reputations: Dict[str, Dict[str, AgentReputation]] = {}

        self._observers: List[ReputationObserver] = []
        self._change_counter = 0

    @property
    def thresholds(self) -> ReputationThresholds:
        """Get reputation thresholds."""
        return self._thresholds

    @property
    def effects(self) -> ReputationEffects:
        """Get reputation effects strategy."""
        return self._effects

    def add_observer(self, observer: ReputationObserver) -> None:
        """Register an observer."""
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: ReputationObserver) -> None:
        """Unregister an observer."""
        if observer in self._observers:
            self._observers.remove(observer)

    def get_reputation(self, agent_id: str, faction_id: str) -> AgentReputation:
        """Get or create reputation record."""
        if agent_id not in self._reputations:
            self._reputations[agent_id] = {}

        if faction_id not in self._reputations[agent_id]:
            self._reputations[agent_id][faction_id] = AgentReputation(
                agent_id=agent_id,
                faction_id=faction_id
            )

        return self._reputations[agent_id][faction_id]

    def adjust_reputation(
        self,
        agent_id: str,
        faction_id: str,
        delta: float,
        reason: str,
        timestamp: float
    ) -> ReputationChange:
        """Adjust reputation value."""
        reputation = self.get_reputation(agent_id, faction_id)

        old_value = reputation.value
        old_tier = reputation.tier

        # Apply change
        reputation.value += delta
        if delta > 0:
            reputation.total_gained += delta
        else:
            reputation.total_lost += abs(delta)

        # Update tier
        new_tier = self._thresholds.get_tier(reputation.value)
        reputation.tier = new_tier

        # Create change record
        self._change_counter += 1
        change = ReputationChange(
            change_id=f"rep_{self._change_counter}",
            agent_id=agent_id,
            faction_id=faction_id,
            old_value=old_value,
            new_value=reputation.value,
            old_tier=old_tier,
            new_tier=new_tier,
            reason=reason,
            timestamp=timestamp
        )

        reputation.history.append(change)

        # Notify observers
        for observer in self._observers:
            observer.on_reputation_changed(change)
            if old_tier != new_tier:
                observer.on_tier_changed(agent_id, faction_id, old_tier, new_tier)

        return change

    def set_reputation(
        self,
        agent_id: str,
        faction_id: str,
        value: float,
        reason: str,
        timestamp: float
    ) -> ReputationChange:
        """Set reputation to specific value."""
        reputation = self.get_reputation(agent_id, faction_id)
        delta = value - reputation.value
        return self.adjust_reputation(agent_id, faction_id, delta, reason, timestamp)

    def get_tier(self, agent_id: str, faction_id: str) -> ReputationTier:
        """Get current tier."""
        reputation = self.get_reputation(agent_id, faction_id)
        return reputation.tier

    def get_all_reputations(self, agent_id: str) -> Dict[str, AgentReputation]:
        """Get all reputations for agent."""
        if agent_id not in self._reputations:
            return {}
        return self._reputations[agent_id].copy()

    # --- Convenience methods ---

    def get_trade_modifier(self, agent_id: str, faction_id: str) -> float:
        """Get trade price modifier for agent with faction."""
        tier = self.get_tier(agent_id, faction_id)
        return self._effects.get_trade_modifier(tier)

    def can_access_services(self, agent_id: str, faction_id: str) -> bool:
        """Check if agent can use faction services."""
        tier = self.get_tier(agent_id, faction_id)
        return self._effects.can_access_services(tier)

    def can_enter_territory(self, agent_id: str, faction_id: str) -> bool:
        """Check if agent can enter faction territory."""
        tier = self.get_tier(agent_id, faction_id)
        return self._effects.can_enter_territory(tier)

    def is_hostile(self, agent_id: str, faction_id: str) -> bool:
        """Check if faction is hostile to agent."""
        tier = self.get_tier(agent_id, faction_id)
        return self._effects.is_attack_on_sight(tier)

    def get_factions_by_tier(
        self,
        agent_id: str,
        tier: ReputationTier
    ) -> List[str]:
        """Get all faction IDs where agent has specific tier."""
        if agent_id not in self._reputations:
            return []

        return [
            faction_id for faction_id, rep in self._reputations[agent_id].items()
            if rep.tier == tier
        ]

    def get_friendly_factions(self, agent_id: str) -> List[str]:
        """Get factions where agent has FRIENDLY or better standing."""
        if agent_id not in self._reputations:
            return []

        good_tiers = (
            ReputationTier.FRIENDLY,
            ReputationTier.HONORED,
            ReputationTier.EXALTED
        )
        return [
            faction_id for faction_id, rep in self._reputations[agent_id].items()
            if rep.tier in good_tiers
        ]

    def get_hostile_factions(self, agent_id: str) -> List[str]:
        """Get factions where agent has HOSTILE or worse standing."""
        if agent_id not in self._reputations:
            return []

        bad_tiers = (ReputationTier.HOSTILE, ReputationTier.HATED)
        return [
            faction_id for faction_id, rep in self._reputations[agent_id].items()
            if rep.tier in bad_tiers
        ]
