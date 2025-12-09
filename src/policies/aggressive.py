"""
AggressivePolicy Module - Strategy for Competitive Behavior

This module provides the AggressivePolicy class, demonstrating the Strategy
pattern for conflict-oriented decision making.

Design Patterns:
    - Strategy: AggressivePolicy is a concrete decision strategy
    - Command: Uses AttackAction and territorial control actions

SOLID Principles:
    - Single Responsibility: Only implements aggressive decision logic
    - Open/Closed: Extensible with new combat behaviors
    - Dependency Inversion: Depends on abstractions

Integration:
    - Uses actions/attack.py for combat
    - Uses social/relationships.py for enemy identification
    - Uses agents/traits.py for combat calculations
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, Optional, Any, List, Set

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from policies.policy import DecisionPolicy

if TYPE_CHECKING:
    from agents.agent import Agent
    from actions.action import Action
    from world.position import Position


class AggressionPriority(Enum):
    """
    Priority levels for aggressive behaviors.

    Determines which aggressive action to take when multiple are available.
    """
    ATTACK_VULNERABLE = auto()  # Attack weak enemies
    DEFEND_TERRITORY = auto()   # Attack intruders
    DENY_RESOURCES = auto()     # Take contested resources
    EXPAND = auto()             # Move to strategic positions
    INTIMIDATE = auto()         # Show force
    RETREAT = auto()            # Strategic withdrawal


@dataclass
class ThreatAssessment:
    """
    Assessment of a potential target or threat.

    Attributes:
        agent_id: ID of the assessed agent
        threat_level: How threatening (0-1, higher = more dangerous)
        vulnerability: How vulnerable to attack (0-1, higher = easier target)
        distance: Distance from assessing agent
        is_enemy: Whether known enemy
    """
    agent_id: str
    threat_level: float
    vulnerability: float
    distance: float
    is_enemy: bool


class CombatAssessmentStrategy(ABC):
    """
    Abstract strategy for combat assessment.

    Allows different approaches to evaluating combat situations.

    Design Pattern: Strategy
    """

    @abstractmethod
    def assess_target(
        self,
        attacker: Agent,
        target: Agent
    ) -> ThreatAssessment:
        """
        Assess a potential combat target.

        Args:
            attacker: Agent considering attack
            target: Potential target

        Returns:
            ThreatAssessment with combat odds
        """
        pass

    @abstractmethod
    def calculate_win_probability(
        self,
        attacker: Agent,
        defender: Agent
    ) -> float:
        """
        Calculate probability of winning combat.

        Args:
            attacker: Attacking agent
            defender: Defending agent

        Returns:
            float: Win probability (0-1)
        """
        pass


class StandardCombatAssessment(CombatAssessmentStrategy):
    """
    Standard combat assessment based on traits.

    Considers strength, health, and energy for combat evaluation.
    """

    def assess_target(self, attacker: Agent, target: Agent) -> ThreatAssessment:
        """Assess target based on relative strength."""
        # Calculate threat level based on target's strength
        target_strength = getattr(target.traits, 'strength', 50)
        attacker_strength = getattr(attacker.traits, 'strength', 50)

        threat_level = target_strength / 100.0
        vulnerability = 1.0 - (target.health / target.max_health) if target.max_health > 0 else 1.0

        return ThreatAssessment(
            agent_id=target.agent_id,
            threat_level=threat_level,
            vulnerability=vulnerability,
            distance=attacker.position.distance_to(target.position),
            is_enemy=False  # Would check relationship
        )

    def calculate_win_probability(self, attacker: Agent, defender: Agent) -> float:
        """Calculate win probability based on traits."""
        attacker_power = self._calculate_combat_power(attacker)
        defender_power = self._calculate_combat_power(defender)

        total_power = attacker_power + defender_power
        if total_power == 0:
            return 0.5

        return attacker_power / total_power

    def _calculate_combat_power(self, agent: Agent) -> float:
        """Calculate overall combat power."""
        strength = getattr(agent.traits, 'strength', 50)
        health_ratio = agent.health / agent.max_health if agent.max_health > 0 else 0
        energy_ratio = agent.energy / agent.max_energy if agent.max_energy > 0 else 0

        return strength * health_ratio * (0.5 + 0.5 * energy_ratio)


class AggressivePolicy(DecisionPolicy):
    """
    Strategy for aggressive, competitive decisions.

    AggressivePolicy demonstrates the Strategy pattern for decision
    algorithms that prioritize competition, conflict, and territorial
    expansion over cooperation. Agents using this policy will:

    - Attack vulnerable enemies when advantageous
    - Defend territory from intruders
    - Deny resources to competitors
    - Expand territorial influence
    - Establish dominance through intimidation

    Decision Priority (highest to lowest):
        1. Attack vulnerable enemies (high win probability)
        2. Defend territory (attack intruders)
        3. Deny resources (gather contested resources first)
        4. Expand territory (move to strategic positions)
        5. Build strength (gather/rest when no opportunities)

    Attributes:
        combat_strategy: Strategy for combat assessment
        min_win_probability: Minimum win chance to attack

    Design Patterns:
        - Strategy: Interchangeable decision algorithm
        - Command: Uses AttackAction for combat

    Examples:
        >>> policy = AggressivePolicy()
        >>> action = policy.choose_action(sensor_data, agent)
        >>> # Returns AttackAction if vulnerable enemy nearby
        >>> # Returns MoveAction to strategic position otherwise
    """

    # Combat thresholds
    MIN_WIN_PROBABILITY: float = 0.6
    MIN_HEALTH_FOR_COMBAT: float = 30.0
    MIN_ENERGY_FOR_COMBAT: float = 20.0

    # Territorial range
    TERRITORY_RADIUS: int = 3

    def __init__(
        self,
        combat_strategy: Optional[CombatAssessmentStrategy] = None,
        min_win_probability: float = 0.6
    ) -> None:
        """
        Initialize an AggressivePolicy.

        Args:
            combat_strategy: Strategy for combat assessment
            min_win_probability: Minimum win chance to attack
        """
        super().__init__(
            name="Aggressive",
            description="Prioritize competition, conflict, and territory control"
        )
        self._combat_strategy: CombatAssessmentStrategy = (
            combat_strategy or StandardCombatAssessment()
        )
        self._min_win_probability: float = min_win_probability

    def choose_action(
        self,
        sensor_data: Any,
        agent: Agent
    ) -> Optional[Action]:
        """
        Choose action based on aggressive strategy.

        Analyzes the situation and chooses the most advantageous
        aggressive action according to priority rules.

        Implementation Flow:
            1. Check agent combat readiness (health/energy)
            2. Find vulnerable enemies
            3. Check for territorial intruders
            4. Check for contested resources
            5. Find strategic expansion opportunities
            6. Fallback to building strength

        Args:
            sensor_data: Dict containing:
                - world: World instance
                - nearby_agents: List of (agent_id, Agent, distance)
                - enemies: List of enemy agent IDs
                - territory: Set of controlled positions
                - nearby_resources: List of resource info
            agent: The decision-making agent

        Returns:
            Optional[Action]: The chosen aggressive action

        Raises:
            NotImplementedError: Interface design - implementation pending
        """
        # Design skeleton - shows the implementation flow
        # Full implementation would:
        #
        # 1. Check combat readiness
        #    if not self._is_combat_ready(agent):
        #        return self._build_strength_action(sensor_data, agent)
        #
        # 2. Find vulnerable targets
        #    target = self._find_vulnerable_target(sensor_data, agent)
        #    if target:
        #        return AttackAction(target.agent_id)
        #
        # 3. Check for intruders
        #    intruder = self._find_intruder(sensor_data, agent)
        #    if intruder:
        #        return AttackAction(intruder.agent_id)
        #
        # 4. Check contested resources
        #    contested = self._find_contested_resource(sensor_data, agent)
        #    if contested:
        #        return MoveAction(contested) or GatherAction()
        #
        # 5. Find expansion opportunity
        #    expansion = self._get_expansion_target(sensor_data, agent)
        #    if expansion:
        #        return MoveAction(expansion)
        #
        # 6. Build strength
        #    return self._build_strength_action(sensor_data, agent)

        raise NotImplementedError(
            "AggressivePolicy.choose_action() - Interface design complete. "
            "Implementation requires integration with active simulation."
        )

    def _is_combat_ready(self, agent: Agent) -> bool:
        """
        Check if agent is ready for combat.

        Args:
            agent: Agent to check

        Returns:
            bool: True if combat ready
        """
        health_percent = (agent.health / agent.max_health) * 100 if agent.max_health > 0 else 0
        energy_percent = (agent.energy / agent.max_energy) * 100 if agent.max_energy > 0 else 0

        return (
            health_percent >= self.MIN_HEALTH_FOR_COMBAT and
            energy_percent >= self.MIN_ENERGY_FOR_COMBAT
        )

    def _find_vulnerable_target(
        self,
        sensor_data: Any,
        agent: Agent
    ) -> Optional[Agent]:
        """
        Find nearby enemy that agent could defeat.

        Evaluates all nearby enemies and returns the most vulnerable
        one that agent has good odds against.

        Args:
            sensor_data: Sensor data with nearby agents
            agent: The decision-making agent

        Returns:
            Optional[Agent]: Most vulnerable target or None
        """
        nearby_agents = sensor_data.get('nearby_agents', [])
        enemies = set(sensor_data.get('enemies', []))

        best_target = None
        best_vulnerability = 0.0

        for agent_info in nearby_agents:
            if isinstance(agent_info, tuple):
                agent_id, target, distance = agent_info
            else:
                target = agent_info
                agent_id = target.agent_id

            # Skip if not enemy
            if agent_id not in enemies:
                continue

            # Assess target
            assessment = self._combat_strategy.assess_target(agent, target)

            # Check win probability
            win_prob = self._combat_strategy.calculate_win_probability(agent, target)
            if win_prob < self._min_win_probability:
                continue

            # Track most vulnerable
            if assessment.vulnerability > best_vulnerability:
                best_vulnerability = assessment.vulnerability
                best_target = target

        return best_target

    def _assess_combat_odds(
        self,
        attacker: Agent,
        defender: Agent
    ) -> float:
        """
        Calculate probability of winning combat.

        Args:
            attacker: Attacking agent
            defender: Defending agent

        Returns:
            float: Win probability (0-1)
        """
        return self._combat_strategy.calculate_win_probability(attacker, defender)

    def _find_intruder(
        self,
        sensor_data: Any,
        agent: Agent
    ) -> Optional[Agent]:
        """
        Find agent intruding in our territory.

        Args:
            sensor_data: Sensor data with territory info
            agent: Agent defending territory

        Returns:
            Optional[Agent]: Intruding agent or None
        """
        territory = sensor_data.get('territory', set())
        if not territory:
            return None

        nearby_agents = sensor_data.get('nearby_agents', [])
        enemies = set(sensor_data.get('enemies', []))

        for agent_info in nearby_agents:
            if isinstance(agent_info, tuple):
                agent_id, intruder, distance = agent_info
            else:
                intruder = agent_info
                agent_id = intruder.agent_id

            # Skip allies
            if agent_id not in enemies:
                continue

            # Check if in territory
            if intruder.position in territory:
                return intruder

        return None

    def _find_contested_resource(
        self,
        sensor_data: Any,
        agent: Agent
    ) -> Optional[Position]:
        """
        Find resource that enemy is approaching.

        Args:
            sensor_data: Sensor data
            agent: Agent

        Returns:
            Optional[Position]: Position of contested resource
        """
        nearby_resources = sensor_data.get('nearby_resources', [])
        nearby_agents = sensor_data.get('nearby_agents', [])
        enemies = set(sensor_data.get('enemies', []))

        # Find resources with enemies nearby
        for resource_info in nearby_resources:
            if isinstance(resource_info, tuple):
                resource_type, quantity, position = resource_info
            else:
                continue

            # Check if any enemy is closer to this resource
            for agent_info in nearby_agents:
                if isinstance(agent_info, tuple):
                    agent_id, enemy, distance = agent_info
                else:
                    continue

                if agent_id in enemies:
                    # Calculate distances
                    agent_dist = agent.position.distance_to(position)
                    enemy_dist = enemy.position.distance_to(position)

                    # Contested if enemy is closer or similar distance
                    if enemy_dist <= agent_dist + 2:
                        return position

        return None

    def _get_expansion_target(
        self,
        sensor_data: Any,
        agent: Agent
    ) -> Optional[Position]:
        """
        Find strategic position to expand territory.

        Args:
            sensor_data: Sensor data
            agent: Agent

        Returns:
            Optional[Position]: Strategic position or None
        """
        # Would analyze map for strategic chokepoints,
        # resource-rich areas, or defensive positions
        # For now, return None (no expansion opportunity)
        return None

    def _build_strength_action(
        self,
        sensor_data: Any,
        agent: Agent
    ) -> Optional[Action]:
        """
        Get action to build strength when no combat opportunities.

        Args:
            sensor_data: Sensor data
            agent: Agent

        Returns:
            Optional[Action]: Gather or Rest action
        """
        # Would return GatherAction or RestAction
        # from actions.gather import GatherAction
        # from actions.rest import RestAction
        #
        # if nearby_resources:
        #     return GatherAction()
        # return RestAction()
        return None

    def __repr__(self) -> str:
        """String representation."""
        return f"AggressivePolicy(priority='attack,defend,deny,expand')"
