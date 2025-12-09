"""
TradeAction Module - Command for Resource Trading Between Agents

This module provides the TradeAction class, demonstrating the Command pattern
for economic interactions between agents.

Design Patterns:
    - Command: TradeAction encapsulates trade as an executable object
    - Mediator: Integrates with TransferManager for atomic trades
    - Observer: Relationship updates notify interested parties

SOLID Principles:
    - Single Responsibility: Only handles resource trading
    - Open/Closed: Designed for extension with pricing strategies
    - Dependency Inversion: Depends on abstractions (Agent, World, managers)

Integration:
    - Uses inventory/transfer.py TransferManager.trade() for atomic exchanges
    - Uses social/relationships.py for relationship updates
    - Uses agents/agent_manager.py for finding target agents
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import TYPE_CHECKING, Dict, Optional, Tuple

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from actions.action import Action
from resources.resource import ResourceType

if TYPE_CHECKING:
    from agents.agent import Agent
    from agents.agent_manager import AgentManager
    from world.world import World
    from social.relationships import RelationshipManager


@dataclass
class TradeOffer:
    """
    Represents a trade offer between agents.

    Immutable record of what each party offers in the trade.

    Attributes:
        initiator_id: ID of agent initiating trade
        target_id: ID of agent receiving offer
        offered: Resources the initiator offers
        requested: Resources the initiator requests
        timestamp: When the offer was created
    """
    initiator_id: str
    target_id: str
    offered: Dict[str, float]
    requested: Dict[str, float]
    timestamp: float


class TradePricingStrategy(ABC):
    """
    Abstract strategy for evaluating trade fairness.

    Allows different pricing models to be plugged in.

    Design Pattern: Strategy
    """

    @abstractmethod
    def calculate_value(
        self,
        resources: Dict[str, float]
    ) -> float:
        """
        Calculate total value of resources.

        Args:
            resources: Dict of resource_type -> quantity

        Returns:
            float: Total value
        """
        pass

    @abstractmethod
    def is_fair_trade(
        self,
        offered_value: float,
        requested_value: float,
        tolerance: float = 0.3
    ) -> bool:
        """
        Check if trade is fair within tolerance.

        Args:
            offered_value: Value of offered resources
            requested_value: Value of requested resources
            tolerance: Acceptable value difference ratio

        Returns:
            bool: True if trade is fair
        """
        pass


class SimplePricingStrategy(TradePricingStrategy):
    """
    Simple fixed-price strategy for trade evaluation.

    Uses predefined base prices for each resource type.
    """

    # Base prices per resource type
    BASE_PRICES = {
        "food": 10.0,
        "water": 8.0,
        "material": 15.0,
        "FOOD": 10.0,
        "WATER": 8.0,
        "MATERIAL": 15.0,
    }

    def calculate_value(self, resources: Dict[str, float]) -> float:
        """Calculate total value using base prices."""
        total = 0.0
        for resource_type, quantity in resources.items():
            price = self.BASE_PRICES.get(resource_type, 10.0)
            total += price * quantity
        return total

    def is_fair_trade(
        self,
        offered_value: float,
        requested_value: float,
        tolerance: float = 0.3
    ) -> bool:
        """Check if values are within tolerance."""
        if requested_value == 0:
            return True  # Gift is always fair
        ratio = offered_value / requested_value
        return (1 - tolerance) <= ratio <= (1 + tolerance)


class TradeAction(Action):
    """
    Command for trading resources with another agent.

    TradeAction demonstrates the Command pattern for economic
    interactions. It encapsulates a trade request that can be:
    - Validated before execution (can_execute)
    - Executed atomically (execute)
    - Logged and tracked (via world events)

    The trade uses TransferManager.trade() for atomic exchange,
    ensuring either both sides complete or neither does.

    Attributes:
        target_agent_id (str): ID of agent to trade with
        offered_resources (Dict[str, float]): Resources to offer
        requested_resources (Dict[str, float]): Resources to request

    Design Patterns:
        - Command: Encapsulates trade as object
        - Strategy: Pluggable pricing evaluation
        - Mediator: Uses TransferManager for coordination

    Examples:
        >>> action = TradeAction(
        ...     target_agent_id="agent-123",
        ...     offered_resources={"food": 5.0},
        ...     requested_resources={"material": 3.0}
        ... )
        >>> if action.can_execute(agent, world):
        ...     success = action.execute(agent, world)
    """

    # Trade range (cells distance)
    TRADE_RANGE: int = 2

    # Minimum relationship strength to trade (-100 to 100 scale)
    MIN_RELATIONSHIP_FOR_TRADE: float = -50.0

    def __init__(
        self,
        target_agent_id: str,
        offered_resources: Dict[str, float],
        requested_resources: Dict[str, float],
        agent_manager: Optional[AgentManager] = None,
        relationship_manager: Optional[RelationshipManager] = None,
        pricing_strategy: Optional[TradePricingStrategy] = None
    ) -> None:
        """
        Initialize a TradeAction.

        Args:
            target_agent_id: ID of agent to trade with
            offered_resources: Resources to offer {type: quantity}
            requested_resources: Resources to request {type: quantity}
            agent_manager: Manager for finding agents (optional, can be
                          retrieved from world)
            relationship_manager: Manager for relationship updates
            pricing_strategy: Strategy for evaluating trade fairness
        """
        super().__init__(
            name="Trade",
            description=f"Trade with agent {target_agent_id}"
        )
        self._target_agent_id: str = target_agent_id
        self._offered: Dict[str, float] = dict(offered_resources)
        self._requested: Dict[str, float] = dict(requested_resources)
        self._agent_manager: Optional[AgentManager] = agent_manager
        self._relationship_manager: Optional[RelationshipManager] = relationship_manager
        self._pricing_strategy: TradePricingStrategy = (
            pricing_strategy or SimplePricingStrategy()
        )

    @property
    def target_agent_id(self) -> str:
        """Get target agent ID."""
        return self._target_agent_id

    @property
    def offered(self) -> Dict[str, float]:
        """Get offered resources (copy)."""
        return dict(self._offered)

    @property
    def requested(self) -> Dict[str, float]:
        """Get requested resources (copy)."""
        return dict(self._requested)

    def execute(self, agent: Agent, world: World) -> bool:
        """
        Execute the trade action.

        Performs atomic resource exchange between agents using
        TransferManager.trade(). Updates relationships on success.

        Implementation Flow:
            1. Validate preconditions (can_execute)
            2. Consume energy from initiating agent
            3. Get target agent from manager
            4. Convert resource types for TransferManager
            5. Execute atomic trade via TransferManager.trade()
            6. Update relationship on success
            7. Log trade event to world

        Args:
            agent: The agent initiating trade
            world: The world context

        Returns:
            bool: True if trade completed successfully

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
        # 4. Convert string types to ResourceType enum:
        #    agent_gives = {ResourceType[k.upper()]: v for k, v in self._offered.items()}
        #    target_gives = {ResourceType[k.upper()]: v for k, v in self._requested.items()}
        #
        # 5. result = TransferManager.trade(agent, target, agent_gives, target_gives)
        #
        # 6. if result.success:
        #        self._update_relationship(agent, target, success=True)
        #        world.event_logger.log(TradeEvent(...))
        #        return True
        #    return False

        raise NotImplementedError(
            "TradeAction.execute() - Interface design complete. "
            "Implementation requires integration with active simulation."
        )

    def can_execute(self, agent: Agent, world: World) -> bool:
        """
        Check if trade can be executed.

        Validates all preconditions for a successful trade:
        - Agent is alive with sufficient energy
        - Target agent exists and is alive
        - Target is within trade range
        - Both agents have required resources
        - Relationship allows trade (not hostile)

        Args:
            agent: The agent initiating trade
            world: The world context

        Returns:
            bool: True if all preconditions met
        """
        # Check agent is alive and has energy
        if not agent.is_alive():
            return False
        if agent.energy < self.energy_cost:
            return False

        # Check target agent exists
        target = self._get_target_agent(world)
        if target is None or not target.is_alive():
            return False

        # Check agents are in range
        if not self._is_in_trade_range(agent, target):
            return False

        # Check both agents have required resources
        if not self._has_required_resources(agent, target):
            return False

        # Check relationship allows trade
        if not self._relationship_allows_trade(agent, target):
            return False

        return True

    @property
    def energy_cost(self) -> float:
        """
        Get the energy cost of trading.

        Trading has a low energy cost (negotiation effort).

        Returns:
            float: Energy cost (1.5)
        """
        return 1.5

    def calculate_trade_value(self) -> Tuple[float, float]:
        """
        Calculate value of offered and requested resources.

        Uses the pricing strategy to evaluate both sides.

        Returns:
            Tuple[float, float]: (offered_value, requested_value)
        """
        offered_value = self._pricing_strategy.calculate_value(self._offered)
        requested_value = self._pricing_strategy.calculate_value(self._requested)
        return offered_value, requested_value

    def is_fair_trade(self, tolerance: float = 0.3) -> bool:
        """
        Check if trade is fair within tolerance.

        Args:
            tolerance: Acceptable value difference ratio

        Returns:
            bool: True if trade is considered fair
        """
        offered_value, requested_value = self.calculate_trade_value()
        return self._pricing_strategy.is_fair_trade(
            offered_value, requested_value, tolerance
        )

    def _get_target_agent(self, world: World) -> Optional[Agent]:
        """
        Get the target agent for this trade.

        Uses agent_manager if provided, otherwise attempts to get from world.

        Args:
            world: World context

        Returns:
            Optional[Agent]: Target agent if found
        """
        if self._agent_manager:
            return self._agent_manager.get_agent(self._target_agent_id)
        # Fallback: try to get agent_manager from world
        if hasattr(world, 'agent_manager'):
            return world.agent_manager.get_agent(self._target_agent_id)
        return None

    def _is_in_trade_range(self, agent: Agent, target: Agent) -> bool:
        """
        Check if agents are within trade range.

        Args:
            agent: Initiating agent
            target: Target agent

        Returns:
            bool: True if within range
        """
        distance = agent.position.distance_to(target.position)
        return distance <= self.TRADE_RANGE

    def _has_required_resources(self, agent: Agent, target: Agent) -> bool:
        """
        Check if both agents have required resources.

        Args:
            agent: Initiating agent (must have offered resources)
            target: Target agent (must have requested resources)

        Returns:
            bool: True if both have required resources
        """
        # Check agent has offered resources
        for resource_type, quantity in self._offered.items():
            try:
                rt = ResourceType[resource_type.upper()]
                if not agent._inventory.has_resource(rt, quantity):
                    return False
            except (KeyError, AttributeError):
                return False

        # Check target has requested resources
        for resource_type, quantity in self._requested.items():
            try:
                rt = ResourceType[resource_type.upper()]
                if not target._inventory.has_resource(rt, quantity):
                    return False
            except (KeyError, AttributeError):
                return False

        return True

    def _relationship_allows_trade(self, agent: Agent, target: Agent) -> bool:
        """
        Check if relationship allows trading.

        Agents with very hostile relationships cannot trade.

        Args:
            agent: Initiating agent
            target: Target agent

        Returns:
            bool: True if relationship allows trade
        """
        if self._relationship_manager is None:
            return True  # No relationship tracking = allow trade

        relationship = self._relationship_manager.get_relationship(
            agent.agent_id, target.agent_id
        )
        if relationship is None:
            return True  # No relationship = neutral = allow trade

        return relationship.strength >= self.MIN_RELATIONSHIP_FOR_TRADE

    def _update_relationship(
        self,
        agent: Agent,
        target: Agent,
        success: bool,
        timestamp: float = 0.0
    ) -> None:
        """
        Update relationship after trade attempt.

        Successful trades improve relationships; failed trades have no effect.

        Args:
            agent: Initiating agent
            target: Target agent
            success: Whether trade succeeded
            timestamp: Current simulation time
        """
        if self._relationship_manager is None:
            return

        if success:
            # Strengthen positive relationship on successful trade
            # Implementation would call relationship_manager.adjust_relationship()
            pass

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"TradeAction(target={self._target_agent_id}, "
            f"offered={self._offered}, requested={self._requested})"
        )
