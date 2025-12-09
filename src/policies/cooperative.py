"""
CooperativePolicy Module - Strategy for Group-Focused Decisions

This module provides the CooperativePolicy class, demonstrating the Strategy
pattern for collaborative decision making.

Design Patterns:
    - Strategy: CooperativePolicy is a concrete decision strategy
    - Observer: Monitors faction/ally status for coordination
    - Facade: Simplifies access to relationship data

SOLID Principles:
    - Single Responsibility: Only implements cooperative decision logic
    - Open/Closed: Extensible with new cooperation behaviors
    - Dependency Inversion: Depends on abstractions

Integration:
    - Uses social/faction.py for faction membership
    - Uses social/relationships.py for ally identification
    - Uses actions/trade.py for resource sharing
    - Uses actions/alliance.py for alliance formation
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum, auto
from typing import TYPE_CHECKING, Optional, Any, Dict, List, Tuple

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from policies.policy import DecisionPolicy

if TYPE_CHECKING:
    from agents.agent import Agent
    from actions.action import Action
    from world.position import Position


class CooperationPriority(Enum):
    """
    Priority levels for cooperative behaviors.

    Determines which cooperative action to take when multiple are available.
    """
    HELP_ALLY = auto()        # Help struggling allies
    SHARE_RESOURCES = auto()   # Trade surplus resources
    COORDINATE = auto()        # Synchronize with faction
    BUILD_ALLIANCE = auto()    # Form new alliances
    COLLECTIVE_GATHER = auto() # Gather for group benefit
    DEFEND_ALLY = auto()       # Protect ally from attack


@dataclass
class AllyNeed:
    """
    Represents an ally's need for resources or assistance.

    Attributes:
        agent_id: ID of ally in need
        need_type: Type of need (health, energy, resource)
        severity: How urgent (0-1, higher = more urgent)
        resource_type: Specific resource needed (if applicable)
    """
    agent_id: str
    need_type: str
    severity: float
    resource_type: Optional[str] = None


class CooperativeStrategy(ABC):
    """
    Abstract strategy for different cooperation approaches.

    Allows customization of how cooperation decisions are made.

    Design Pattern: Strategy
    """

    @abstractmethod
    def evaluate_ally_need(
        self,
        ally: Agent,
        agent: Agent
    ) -> Optional[AllyNeed]:
        """
        Evaluate if an ally needs help.

        Args:
            ally: Potential ally in need
            agent: Agent evaluating

        Returns:
            AllyNeed if ally needs help, None otherwise
        """
        pass

    @abstractmethod
    def should_share_resources(
        self,
        agent: Agent,
        ally: Agent,
        resource_type: str
    ) -> bool:
        """
        Determine if agent should share resources with ally.

        Args:
            agent: Agent with resources
            ally: Potential recipient
            resource_type: Type of resource

        Returns:
            bool: True if should share
        """
        pass


class StandardCooperativeStrategy(CooperativeStrategy):
    """
    Standard cooperative behavior rules.

    Rules:
    - Help allies with health < 30%
    - Share if agent has > 50% surplus
    - Prioritize faction members
    """

    HEALTH_THRESHOLD: float = 30.0
    ENERGY_THRESHOLD: float = 20.0
    SURPLUS_THRESHOLD: float = 50.0

    def evaluate_ally_need(self, ally: Agent, agent: Agent) -> Optional[AllyNeed]:
        """Evaluate ally needs based on health and energy."""
        # Check health need
        health_percent = (ally.health / ally.max_health) * 100 if ally.max_health > 0 else 0
        if health_percent < self.HEALTH_THRESHOLD:
            return AllyNeed(
                agent_id=ally.agent_id,
                need_type="health",
                severity=(self.HEALTH_THRESHOLD - health_percent) / self.HEALTH_THRESHOLD,
                resource_type="food"
            )

        # Check energy need
        energy_percent = (ally.energy / ally.max_energy) * 100 if ally.max_energy > 0 else 0
        if energy_percent < self.ENERGY_THRESHOLD:
            return AllyNeed(
                agent_id=ally.agent_id,
                need_type="energy",
                severity=(self.ENERGY_THRESHOLD - energy_percent) / self.ENERGY_THRESHOLD,
                resource_type="food"
            )

        return None

    def should_share_resources(
        self,
        agent: Agent,
        ally: Agent,
        resource_type: str
    ) -> bool:
        """Check if agent has surplus to share."""
        # Would check agent's inventory for surplus
        # For now, return True if agent has the resource
        return True


class CooperativePolicy(DecisionPolicy):
    """
    Strategy for group-focused, collaborative decisions.

    CooperativePolicy demonstrates the Strategy pattern for decision
    algorithms that prioritize group benefit and collaboration over
    individual gain. Agents using this policy will:

    - Help struggling allies with low health/energy
    - Share surplus resources with faction members
    - Coordinate actions with faction objectives
    - Form and maintain alliances
    - Participate in collective defense

    Decision Priority (highest to lowest):
        1. Help struggling allies (health/energy < threshold)
        2. Trade surplus resources with allies who need them
        3. Coordinate with faction objectives
        4. Build new alliances with friendly agents
        5. Gather resources for group stockpile
        6. Rest/explore as fallback

    Attributes:
        cooperation_strategy: Strategy for evaluating cooperation

    Design Patterns:
        - Strategy: Interchangeable decision algorithm
        - Observer: Monitors ally status
        - Facade: Simplifies relationship queries

    Examples:
        >>> policy = CooperativePolicy()
        >>> action = policy.choose_action(sensor_data, agent)
        >>> # Returns TradeAction if ally needs resources
        >>> # Returns GatherAction if stockpile needs resources
    """

    # Thresholds for cooperation decisions
    HELP_HEALTH_THRESHOLD: float = 30.0
    HELP_ENERGY_THRESHOLD: float = 20.0
    SURPLUS_THRESHOLD: float = 50.0

    def __init__(
        self,
        cooperation_strategy: Optional[CooperativeStrategy] = None
    ) -> None:
        """
        Initialize a CooperativePolicy.

        Args:
            cooperation_strategy: Strategy for cooperation decisions
        """
        super().__init__(
            name="Cooperative",
            description="Prioritize group benefit and collaboration"
        )
        self._cooperation_strategy: CooperativeStrategy = (
            cooperation_strategy or StandardCooperativeStrategy()
        )

    def choose_action(
        self,
        sensor_data: Any,
        agent: Agent
    ) -> Optional[Action]:
        """
        Choose action based on cooperative strategy.

        Analyzes the situation and chooses the most beneficial
        cooperative action according to priority rules.

        Implementation Flow:
            1. Check for struggling allies who need help
            2. Check for trade opportunities with allies
            3. Check for faction coordination needs
            4. Check for alliance formation opportunities
            5. Fallback to gathering for group or resting

        Args:
            sensor_data: Dict containing:
                - world: World instance
                - nearby_agents: List of (agent_id, Agent, distance)
                - nearby_resources: List of resource info
                - faction: Optional Faction membership
                - allies: List of allied agent IDs
                - faction_objective: Optional current objective
            agent: The decision-making agent

        Returns:
            Optional[Action]: The chosen cooperative action

        Raises:
            NotImplementedError: Interface design - implementation pending
        """
        # Design skeleton - shows the implementation flow
        # Full implementation would:
        #
        # 1. Check for struggling allies
        #    struggling = self._find_struggling_ally(sensor_data, agent)
        #    if struggling:
        #        if self._can_help_ally(agent, struggling):
        #            return self._create_help_action(agent, struggling)
        #
        # 2. Check for trade opportunities
        #    ally_needs = self._find_ally_needs(sensor_data)
        #    surplus = self._has_surplus_resources(agent)
        #    if ally_needs and surplus:
        #        return TradeAction(ally_needs[0].agent_id, surplus, {})
        #
        # 3. Check faction objective
        #    objective = self._get_faction_objective(sensor_data)
        #    if objective:
        #        return self._action_for_objective(objective, agent)
        #
        # 4. Check alliance opportunities
        #    if self._should_form_alliance(sensor_data, agent):
        #        targets = self._find_alliance_targets(sensor_data, agent)
        #        return FormAllianceAction(targets, "New Alliance")
        #
        # 5. Fallback: gather for group or rest
        #    return self._fallback_action(sensor_data, agent)

        raise NotImplementedError(
            "CooperativePolicy.choose_action() - Interface design complete. "
            "Implementation requires integration with active simulation."
        )

    def _find_struggling_ally(
        self,
        sensor_data: Any,
        agent: Agent
    ) -> Optional[Agent]:
        """
        Find nearby ally with low health or energy.

        Args:
            sensor_data: Sensor data with nearby agents
            agent: The decision-making agent

        Returns:
            Optional[Agent]: Struggling ally or None
        """
        nearby_agents = sensor_data.get('nearby_agents', [])
        allies = set(sensor_data.get('allies', []))

        for agent_info in nearby_agents:
            # Handle different sensor data formats
            if isinstance(agent_info, tuple):
                agent_id, other_agent, distance = agent_info
            else:
                other_agent = agent_info
                agent_id = other_agent.agent_id

            # Check if ally
            if agent_id not in allies:
                continue

            # Check if struggling
            need = self._cooperation_strategy.evaluate_ally_need(other_agent, agent)
            if need is not None:
                return other_agent

        return None

    def _has_surplus_resources(
        self,
        agent: Agent
    ) -> Dict[str, float]:
        """
        Determine which resources agent has surplus of.

        A surplus is defined as having more than SURPLUS_THRESHOLD
        of a resource's capacity.

        Args:
            agent: Agent to check

        Returns:
            Dict[str, float]: {resource_type: surplus_amount}
        """
        surplus = {}

        # Would check agent's inventory
        # For each resource type, if quantity > threshold, add to surplus
        # Implementation would:
        # for resource_type in ResourceType:
        #     quantity = agent._inventory.get_quantity(resource_type)
        #     if quantity > self.SURPLUS_THRESHOLD:
        #         surplus[resource_type.name] = quantity - self.SURPLUS_THRESHOLD

        return surplus

    def _find_ally_needs(
        self,
        sensor_data: Any
    ) -> Dict[str, Tuple[Agent, str, float]]:
        """
        Find what resources nearby allies need.

        Args:
            sensor_data: Sensor data with nearby agents

        Returns:
            Dict mapping agent_id to (Agent, resource_type, quantity_needed)
        """
        needs = {}
        nearby_agents = sensor_data.get('nearby_agents', [])
        allies = set(sensor_data.get('allies', []))

        for agent_info in nearby_agents:
            if isinstance(agent_info, tuple):
                agent_id, ally, distance = agent_info
            else:
                ally = agent_info
                agent_id = ally.agent_id

            if agent_id not in allies:
                continue

            # Check each resource type for deficiency
            # Would iterate through resources and check inventory levels
            # if level < threshold, add to needs

        return needs

    def _should_form_alliance(
        self,
        sensor_data: Any,
        agent: Agent
    ) -> bool:
        """
        Check if conditions favor alliance formation.

        Considers:
        - Number of nearby friendly agents
        - Agent's sociability trait
        - Existing faction membership
        - Threats in the area

        Args:
            sensor_data: Sensor data
            agent: The decision-making agent

        Returns:
            bool: True if should attempt alliance
        """
        # Check sociability
        sociability = getattr(agent.traits, 'sociability', 50)
        if sociability < 30:
            return False

        # Check if already in faction
        if sensor_data.get('faction') is not None:
            return False  # Already in faction

        # Check for friendly nearby agents
        nearby_agents = sensor_data.get('nearby_agents', [])
        friendly_count = 0
        for agent_info in nearby_agents:
            if isinstance(agent_info, tuple):
                _, other, _ = agent_info
            else:
                other = agent_info

            # Count non-hostile agents
            friendly_count += 1

        return friendly_count >= 2  # Need at least 2 potential members

    def _get_faction_objective(
        self,
        sensor_data: Any
    ) -> Optional[str]:
        """
        Get current faction objective if in faction.

        Args:
            sensor_data: Sensor data with faction info

        Returns:
            Optional[str]: Objective description or None
        """
        faction = sensor_data.get('faction')
        if faction is None:
            return None

        return sensor_data.get('faction_objective')

    def _can_help_ally(
        self,
        agent: Agent,
        ally: Agent
    ) -> bool:
        """
        Check if agent can help the struggling ally.

        Args:
            agent: Helping agent
            ally: Ally in need

        Returns:
            bool: True if can provide help
        """
        # Check if agent has resources to share
        # Check if agent has enough energy for trade action
        return agent.energy >= 1.5  # Trade energy cost

    def _create_help_action(
        self,
        agent: Agent,
        ally: Agent
    ) -> Optional[Action]:
        """
        Create action to help struggling ally.

        Args:
            agent: Helping agent
            ally: Ally to help

        Returns:
            Optional[Action]: Help action (usually TradeAction)
        """
        # Would create TradeAction offering food
        # from actions.trade import TradeAction
        # return TradeAction(ally.agent_id, {"food": 5.0}, {})
        return None

    def _fallback_action(
        self,
        sensor_data: Any,
        agent: Agent
    ) -> Optional[Action]:
        """
        Get fallback action when no cooperative opportunities.

        Args:
            sensor_data: Sensor data
            agent: Agent

        Returns:
            Optional[Action]: Fallback action
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
        return "CooperativePolicy(priority='help_allies,share,coordinate,build_alliances')"
