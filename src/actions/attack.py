"""
AttackAction Module - Command for Agent Combat

This module provides the AttackAction class, demonstrating the Command pattern
for combat interactions between agents.

Design Patterns:
    - Command: AttackAction encapsulates combat as an executable object
    - Strategy: CombatStrategy for different damage calculation methods
    - Observer: Faction conflict notifications

SOLID Principles:
    - Single Responsibility: Only handles combat actions
    - Open/Closed: Extensible with combat strategies
    - Dependency Inversion: Depends on abstractions (Agent, World, managers)

Integration:
    - Uses agents/traits.py for combat bonus calculations
    - Uses social/relationships.py for relationship updates
    - Uses social/faction.py for faction conflict detection
    - Uses agents/agent_manager.py for finding target agents
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Optional

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from actions.action import Action

if TYPE_CHECKING:
    from agents.agent import Agent
    from agents.agent_manager import AgentManager
    from world.world import World
    from social.relationships import RelationshipManager


class CombatResult(Enum):
    """
    Enumeration of combat outcomes.

    Attributes:
        HIT: Attack landed, damage dealt
        MISS: Attack missed, no damage
        BLOCKED: Attack blocked by defender
        CRITICAL: Critical hit, bonus damage
        KILL: Target was killed
    """
    HIT = "hit"
    MISS = "miss"
    BLOCKED = "blocked"
    CRITICAL = "critical"
    KILL = "kill"


@dataclass
class CombatOutcome:
    """
    Result of a combat action.

    Immutable record of combat details.

    Attributes:
        result: The type of outcome
        damage_dealt: Amount of damage dealt
        attacker_id: ID of attacking agent
        defender_id: ID of defending agent
        timestamp: When combat occurred
    """
    result: CombatResult
    damage_dealt: float
    attacker_id: str
    defender_id: str
    timestamp: float


class CombatStrategy(ABC):
    """
    Abstract strategy for combat damage calculation.

    Allows different combat models to be plugged in.

    Design Pattern: Strategy
    """

    @abstractmethod
    def calculate_damage(
        self,
        attacker: Agent,
        defender: Agent
    ) -> float:
        """
        Calculate damage dealt in combat.

        Args:
            attacker: The attacking agent
            defender: The defending agent

        Returns:
            float: Damage to deal
        """
        pass

    @abstractmethod
    def calculate_hit_chance(
        self,
        attacker: Agent,
        defender: Agent
    ) -> float:
        """
        Calculate probability of hitting.

        Args:
            attacker: The attacking agent
            defender: The defending agent

        Returns:
            float: Hit probability (0.0 to 1.0)
        """
        pass


class StandardCombatStrategy(CombatStrategy):
    """
    Standard combat strategy using agent traits.

    Damage Formula:
        base_damage * attacker_bonus * (1 - defender_reduction)

    Where:
        - base_damage = 10.0
        - attacker_bonus = 1.0 + (attacker.traits.strength / 100)
        - defender_reduction = defender.traits.strength / 200 (max 0.5)
    """

    BASE_DAMAGE: float = 10.0
    CRITICAL_MULTIPLIER: float = 2.0
    CRITICAL_CHANCE: float = 0.1  # 10% base critical chance

    def calculate_damage(self, attacker: Agent, defender: Agent) -> float:
        """
        Calculate damage based on traits.

        Uses strength for attack bonus and damage reduction.

        Args:
            attacker: The attacking agent
            defender: The defending agent

        Returns:
            float: Damage amount (minimum 1.0)
        """
        # Get trait-based bonuses
        attacker_strength = getattr(attacker.traits, 'strength', 50)
        defender_strength = getattr(defender.traits, 'strength', 50)

        # Calculate bonuses
        attack_bonus = 1.0 + (attacker_strength / 100.0)
        defense_reduction = min(defender_strength / 200.0, 0.5)

        # Calculate final damage
        damage = self.BASE_DAMAGE * attack_bonus * (1.0 - defense_reduction)

        return max(damage, 1.0)  # Minimum 1 damage

    def calculate_hit_chance(self, attacker: Agent, defender: Agent) -> float:
        """
        Calculate hit probability based on agility.

        Higher attacker agility increases hit chance.
        Higher defender agility decreases hit chance.

        Args:
            attacker: The attacking agent
            defender: The defending agent

        Returns:
            float: Hit probability (0.5 to 0.95)
        """
        attacker_agility = getattr(attacker.traits, 'agility', 50)
        defender_agility = getattr(defender.traits, 'agility', 50)

        # Base 75% hit chance, modified by agility difference
        base_chance = 0.75
        agility_diff = (attacker_agility - defender_agility) / 100.0
        hit_chance = base_chance + (agility_diff * 0.2)

        return max(0.5, min(0.95, hit_chance))  # Clamp to 50%-95%


class AttackAction(Action):
    """
    Command for attacking another agent.

    AttackAction demonstrates the Command pattern for combat
    interactions. It encapsulates an attack that can be:
    - Validated before execution (can_execute)
    - Executed with damage calculation (execute)
    - Logged and tracked (via world events)

    Attributes:
        target_agent_id (str): ID of agent to attack

    Design Patterns:
        - Command: Encapsulates attack as object
        - Strategy: Pluggable combat calculation
        - Observer: Faction conflict notifications

    Examples:
        >>> action = AttackAction(target_agent_id="agent-123")
        >>> if action.can_execute(agent, world):
        ...     success = action.execute(agent, world)
    """

    # Attack range (cells distance)
    ATTACK_RANGE: int = 1

    def __init__(
        self,
        target_agent_id: str,
        agent_manager: Optional[AgentManager] = None,
        relationship_manager: Optional[RelationshipManager] = None,
        combat_strategy: Optional[CombatStrategy] = None
    ) -> None:
        """
        Initialize an AttackAction.

        Args:
            target_agent_id: ID of agent to attack
            agent_manager: Manager for finding agents
            relationship_manager: Manager for relationship updates
            combat_strategy: Strategy for combat calculations
        """
        super().__init__(
            name="Attack",
            description=f"Attack agent {target_agent_id}"
        )
        self._target_agent_id: str = target_agent_id
        self._agent_manager: Optional[AgentManager] = agent_manager
        self._relationship_manager: Optional[RelationshipManager] = relationship_manager
        self._combat_strategy: CombatStrategy = (
            combat_strategy or StandardCombatStrategy()
        )

    @property
    def target_agent_id(self) -> str:
        """Get the target agent ID."""
        return self._target_agent_id

    def execute(self, agent: Agent, world: World) -> bool:
        """
        Execute the attack action.

        Calculates damage based on traits and applies to target.
        Updates relationship to enemy status.

        Implementation Flow:
            1. Validate preconditions (can_execute)
            2. Consume energy from attacker
            3. Get target agent
            4. Calculate hit chance
            5. Calculate damage using combat strategy
            6. Apply damage to target via target.take_damage()
            7. Check if target died
            8. Update relationship to ENEMY
            9. Trigger faction conflict if applicable
            10. Log combat event to world

        Args:
            agent: The attacking agent
            world: The world context

        Returns:
            bool: True if attack executed (regardless of hit/miss)

        Raises:
            NotImplementedError: Interface design - implementation pending
        """
        # Design skeleton - shows the implementation flow
        # Full implementation would:
        #
        # 1. if not self.can_execute(agent, world):
        #        return False
        #
        # 2. agent.consume_energy(self.energy_cost)
        #
        # 3. target = self._get_target_agent(world)
        #
        # 4. hit_chance = self._combat_strategy.calculate_hit_chance(agent, target)
        #    if random.random() > hit_chance:
        #        return True  # Miss, but action was executed
        #
        # 5. damage = self._combat_strategy.calculate_damage(agent, target)
        #
        # 6. target.take_damage(damage)
        #
        # 7. if not target.is_alive():
        #        outcome = CombatOutcome(CombatResult.KILL, damage, ...)
        #    else:
        #        outcome = CombatOutcome(CombatResult.HIT, damage, ...)
        #
        # 8. self._update_relationship_to_enemy(agent, target, world.time)
        #
        # 9. self._trigger_faction_conflict(agent, target, world)
        #
        # 10. world.event_logger.log(CombatEvent(outcome))
        #
        # return True

        raise NotImplementedError(
            "AttackAction.execute() - Interface design complete. "
            "Implementation requires integration with active simulation."
        )

    def can_execute(self, agent: Agent, world: World) -> bool:
        """
        Check if attack can be executed.

        Validates all preconditions for combat:
        - Agent is alive with sufficient energy
        - Target agent exists and is alive
        - Target is within attack range
        - Agents are not in same faction
        - Agents are not allies

        Args:
            agent: The attacking agent
            world: The world context

        Returns:
            bool: True if all preconditions met
        """
        # Check agent is alive and has energy
        if not agent.is_alive():
            return False
        if agent.energy < self.energy_cost:
            return False

        # Check target agent exists and is alive
        target = self._get_target_agent(world)
        if target is None or not target.is_alive():
            return False

        # Check target is in attack range
        if not self._is_in_attack_range(agent, target):
            return False

        # Check not same faction (friendly fire prevention)
        if self._is_same_faction(agent, target, world):
            return False

        # Check not allied
        if self._are_allies(agent, target):
            return False

        return True

    @property
    def energy_cost(self) -> float:
        """
        Get the energy cost of attacking.

        Attacking has a high energy cost (physical exertion).

        Returns:
            float: Energy cost (5.0)
        """
        return 5.0

    def calculate_damage(self, attacker: Agent, defender: Agent) -> float:
        """
        Calculate damage for this attack.

        Delegates to the combat strategy.

        Args:
            attacker: The attacking agent
            defender: The defending agent

        Returns:
            float: Damage amount
        """
        return self._combat_strategy.calculate_damage(attacker, defender)

    def calculate_hit_chance(self, attacker: Agent, defender: Agent) -> float:
        """
        Calculate hit probability for this attack.

        Delegates to the combat strategy.

        Args:
            attacker: The attacking agent
            defender: The defending agent

        Returns:
            float: Hit probability (0.0 to 1.0)
        """
        return self._combat_strategy.calculate_hit_chance(attacker, defender)

    def _get_target_agent(self, world: World) -> Optional[Agent]:
        """
        Get the target agent for this attack.

        Args:
            world: World context

        Returns:
            Optional[Agent]: Target agent if found
        """
        if self._agent_manager:
            return self._agent_manager.get_agent(self._target_agent_id)
        if hasattr(world, 'agent_manager'):
            return world.agent_manager.get_agent(self._target_agent_id)
        return None

    def _is_in_attack_range(self, agent: Agent, target: Agent) -> bool:
        """
        Check if target is within attack range.

        Args:
            agent: Attacking agent
            target: Target agent

        Returns:
            bool: True if within range
        """
        distance = agent.position.distance_to(target.position)
        return distance <= self.ATTACK_RANGE

    def _is_same_faction(self, agent: Agent, target: Agent, world: World) -> bool:
        """
        Check if agents are in the same faction.

        Prevents friendly fire within factions.

        Args:
            agent: Attacking agent
            target: Target agent
            world: World context

        Returns:
            bool: True if same faction
        """
        # Check if both agents have faction_id attribute
        agent_faction = getattr(agent, 'faction_id', None)
        target_faction = getattr(target, 'faction_id', None)

        if agent_faction is None or target_faction is None:
            return False  # No faction = not same faction

        return agent_faction == target_faction

    def _are_allies(self, agent: Agent, target: Agent) -> bool:
        """
        Check if agents are allies.

        Uses relationship manager to check alliance status.

        Args:
            agent: Attacking agent
            target: Target agent

        Returns:
            bool: True if allies
        """
        if self._relationship_manager is None:
            return False

        # Check if relationship manager has alliance checking method
        if hasattr(self._relationship_manager, 'are_allies'):
            return self._relationship_manager.are_allies(
                agent.agent_id, target.agent_id
            )

        # Fallback: check if relationship type is ALLY or FRIEND
        relationship = self._relationship_manager.get_relationship(
            agent.agent_id, target.agent_id
        )
        if relationship is None:
            return False

        # Check for ally relationship type
        rel_type = getattr(relationship, 'relationship_type', None)
        if rel_type is not None:
            type_name = getattr(rel_type, 'name', str(rel_type))
            return type_name in ('ALLY', 'FRIEND')

        return False

    def _update_relationship_to_enemy(
        self,
        agent: Agent,
        target: Agent,
        timestamp: float
    ) -> None:
        """
        Update relationship to enemy status after attack.

        Args:
            agent: Attacking agent
            target: Target agent
            timestamp: Current simulation time
        """
        if self._relationship_manager is None:
            return

        # Implementation would call:
        # self._relationship_manager.set_relationship(
        #     agent.agent_id, target.agent_id,
        #     RelationshipType.ENEMY, strength=-50.0, timestamp=timestamp
        # )
        pass

    def _trigger_faction_conflict(
        self,
        agent: Agent,
        target: Agent,
        world: World
    ) -> None:
        """
        Trigger faction-level conflict if applicable.

        When agents from different factions fight, it may
        escalate to faction war.

        Args:
            agent: Attacking agent
            target: Target agent
            world: World context
        """
        # Get faction IDs
        agent_faction = getattr(agent, 'faction_id', None)
        target_faction = getattr(target, 'faction_id', None)

        if agent_faction is None or target_faction is None:
            return  # No factions involved

        if agent_faction == target_faction:
            return  # Same faction, no inter-faction conflict

        # Implementation would:
        # 1. Get FactionRelationshipManager
        # 2. Decrease faction relationship
        # 3. Potentially declare war if relationship drops too low
        pass

    def __repr__(self) -> str:
        """String representation."""
        return f"AttackAction(target={self._target_agent_id}, cost={self.energy_cost})"
