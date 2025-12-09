"""
Pricing Strategy Module

This module provides pricing strategies for the economy system.
Different strategies calculate prices based on various factors.

Design Patterns:
    - Strategy Pattern: Interchangeable pricing algorithms
    - Decorator Pattern: PriceTracker wraps pricing for history

SOLID Principles:
    - Single Responsibility: Each strategy handles one pricing approach
    - Open/Closed: New strategies can be added without modification
    - Liskov Substitution: All strategies are interchangeable

Integration:
    - Uses inventory/resource_type.py for ResourceType
    - Uses social/relationships.py for relationship-based pricing
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import TYPE_CHECKING, Optional, Dict, List, Any
from collections import deque
import time

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

if TYPE_CHECKING:
    from inventory.resource_type import ResourceType


class PriceVolatility(Enum):
    """Price volatility levels for supply/demand pricing."""
    STABLE = 0.1       # 10% max change
    MODERATE = 0.25    # 25% max change
    VOLATILE = 0.5     # 50% max change
    EXTREME = 1.0      # 100% max change


@dataclass
class PricePoint:
    """
    A single price data point.

    Attributes:
        timestamp: When price was recorded
        price: The price value
        resource_type: Type of resource
        quantity_traded: Optional quantity in transaction
    """
    timestamp: float
    price: float
    resource_type: str
    quantity_traded: Optional[float] = None


@dataclass
class SupplyDemandData:
    """
    Supply and demand information for pricing.

    Attributes:
        total_supply: Total available quantity
        total_demand: Total requested quantity
        recent_trades: Number of recent trades
        average_trade_size: Mean trade quantity
    """
    total_supply: float = 0.0
    total_demand: float = 0.0
    recent_trades: int = 0
    average_trade_size: float = 0.0


class PricingStrategy(ABC):
    """
    Abstract base for pricing strategies.

    Defines interface for calculating resource prices.
    Implementations can use fixed prices, supply/demand,
    relationship modifiers, or custom algorithms.

    Design Pattern: Strategy

    Subclasses:
        - FixedPricing: Constant base prices
        - SupplyDemandPricing: Dynamic market-based prices
        - RelationshipPricing: Modified by social relationships

    Examples:
        >>> strategy = SupplyDemandPricing()
        >>> price = strategy.calculate_price("food", marketplace, 10.0)
    """

    @abstractmethod
    def calculate_price(
        self,
        resource_type: str,
        marketplace: Any,
        base_price: float
    ) -> float:
        """
        Calculate price for a resource.

        Args:
            resource_type: Type of resource (string or ResourceType)
            marketplace: Marketplace instance for context
            base_price: Starting price before modifiers

        Returns:
            float: Calculated price per unit
        """
        pass

    @abstractmethod
    def get_name(self) -> str:
        """
        Get strategy name.

        Returns:
            str: Strategy identifier
        """
        pass


class FixedPricing(PricingStrategy):
    """
    Fixed pricing strategy with constant base prices.

    Returns the base price without modification.
    Useful for stable economies or testing.

    Attributes:
        price_overrides: Optional specific prices per resource

    Examples:
        >>> pricing = FixedPricing({"food": 5.0, "wood": 3.0})
        >>> price = pricing.calculate_price("food", marketplace, 10.0)
        >>> print(price)  # 5.0 (override) or 10.0 (base)
    """

    def __init__(
        self,
        price_overrides: Optional[Dict[str, float]] = None
    ) -> None:
        """
        Initialize FixedPricing.

        Args:
            price_overrides: Specific prices for resources
        """
        self._price_overrides = price_overrides or {}

    def calculate_price(
        self,
        resource_type: str,
        marketplace: Any,
        base_price: float
    ) -> float:
        """
        Return fixed price for resource.

        Args:
            resource_type: Resource type string
            marketplace: Ignored for fixed pricing
            base_price: Default price if no override

        Returns:
            float: Override price or base price
        """
        resource_name = str(resource_type)
        return self._price_overrides.get(resource_name, base_price)

    def set_price(self, resource_type: str, price: float) -> None:
        """
        Set fixed price for a resource.

        Args:
            resource_type: Resource type string
            price: Price to set
        """
        self._price_overrides[str(resource_type)] = price

    def get_name(self) -> str:
        """Return strategy name."""
        return "FixedPricing"


class SupplyDemandPricing(PricingStrategy):
    """
    Dynamic pricing based on supply and demand.

    Prices increase when demand exceeds supply and
    decrease when supply exceeds demand.

    Formula:
        ratio = demand / supply (clamped)
        modifier = 1 + (ratio - 1) * volatility
        price = base_price * modifier

    Attributes:
        volatility: How much prices can change
        min_multiplier: Minimum price multiplier
        max_multiplier: Maximum price multiplier

    Examples:
        >>> pricing = SupplyDemandPricing(volatility=PriceVolatility.MODERATE)
        >>> # High demand, low supply -> higher price
        >>> # Low demand, high supply -> lower price
    """

    DEFAULT_MIN_MULTIPLIER: float = 0.5
    DEFAULT_MAX_MULTIPLIER: float = 2.0

    def __init__(
        self,
        volatility: PriceVolatility = PriceVolatility.MODERATE,
        min_multiplier: float = DEFAULT_MIN_MULTIPLIER,
        max_multiplier: float = DEFAULT_MAX_MULTIPLIER
    ) -> None:
        """
        Initialize SupplyDemandPricing.

        Args:
            volatility: How reactive prices are
            min_multiplier: Minimum price factor
            max_multiplier: Maximum price factor
        """
        self._volatility = volatility
        self._min_multiplier = min_multiplier
        self._max_multiplier = max_multiplier

    def calculate_price(
        self,
        resource_type: str,
        marketplace: Any,
        base_price: float
    ) -> float:
        """
        Calculate price based on supply and demand.

        Args:
            resource_type: Resource type string
            marketplace: Marketplace with supply/demand data
            base_price: Starting price

        Returns:
            float: Adjusted price
        """
        # Get supply/demand data from marketplace
        # Implementation would:
        # supply_demand = marketplace.get_supply_demand(resource_type)
        # supply = supply_demand.total_supply or 1.0
        # demand = supply_demand.total_demand or 1.0
        #
        # ratio = demand / supply
        # modifier = 1 + (ratio - 1) * self._volatility.value
        # modifier = max(self._min_multiplier, min(self._max_multiplier, modifier))
        #
        # return base_price * modifier

        # For now, return base price
        return base_price

    def get_name(self) -> str:
        """Return strategy name."""
        return f"SupplyDemandPricing({self._volatility.name})"


class RelationshipPricing(PricingStrategy):
    """
    Pricing modified by social relationships.

    Allies get discounts, enemies pay premiums.
    Builds on another pricing strategy.

    Modifiers:
        - Ally: -15% discount
        - Neutral: No change
        - Hostile: +25% premium
        - Faction member: -20% discount

    Attributes:
        base_strategy: Underlying pricing strategy
        ally_discount: Discount for allies (0-1)
        enemy_premium: Premium for enemies (0+)

    Examples:
        >>> base = SupplyDemandPricing()
        >>> pricing = RelationshipPricing(base, ally_discount=0.15)
    """

    DEFAULT_ALLY_DISCOUNT: float = 0.15
    DEFAULT_ENEMY_PREMIUM: float = 0.25
    DEFAULT_FACTION_DISCOUNT: float = 0.20

    def __init__(
        self,
        base_strategy: PricingStrategy,
        ally_discount: float = DEFAULT_ALLY_DISCOUNT,
        enemy_premium: float = DEFAULT_ENEMY_PREMIUM,
        faction_discount: float = DEFAULT_FACTION_DISCOUNT
    ) -> None:
        """
        Initialize RelationshipPricing.

        Args:
            base_strategy: Strategy to build on
            ally_discount: Discount for allies (0-1)
            enemy_premium: Premium for enemies (0+)
            faction_discount: Discount for faction members
        """
        self._base_strategy = base_strategy
        self._ally_discount = ally_discount
        self._enemy_premium = enemy_premium
        self._faction_discount = faction_discount

    def calculate_price(
        self,
        resource_type: str,
        marketplace: Any,
        base_price: float
    ) -> float:
        """
        Calculate price with relationship modifiers.

        Note: This method signature doesn't include buyer/seller info.
        In practice, this would be called with additional context.

        Args:
            resource_type: Resource type string
            marketplace: Marketplace instance
            base_price: Starting price

        Returns:
            float: Base strategy price (modifier applied separately)
        """
        return self._base_strategy.calculate_price(
            resource_type, marketplace, base_price
        )

    def calculate_price_for_relationship(
        self,
        resource_type: str,
        marketplace: Any,
        base_price: float,
        relationship_type: str,
        same_faction: bool = False
    ) -> float:
        """
        Calculate price with relationship modifier.

        Args:
            resource_type: Resource type string
            marketplace: Marketplace instance
            base_price: Starting price
            relationship_type: "ally", "neutral", or "hostile"
            same_faction: Whether buyer/seller share faction

        Returns:
            float: Modified price
        """
        price = self._base_strategy.calculate_price(
            resource_type, marketplace, base_price
        )

        # Apply faction discount first
        if same_faction:
            price *= (1 - self._faction_discount)

        # Apply relationship modifier
        if relationship_type == "ally":
            price *= (1 - self._ally_discount)
        elif relationship_type == "hostile":
            price *= (1 + self._enemy_premium)

        return max(0.01, price)  # Minimum price

    def get_name(self) -> str:
        """Return strategy name."""
        return f"RelationshipPricing({self._base_strategy.get_name()})"


class PriceTracker:
    """
    Tracks historical price data.

    Records price points over time for analysis and
    trend detection. Uses a sliding window for memory efficiency.

    Attributes:
        max_history: Maximum price points to retain
        price_history: Dict of resource -> price points

    Design Pattern: Decorator (wraps pricing with history)

    Examples:
        >>> tracker = PriceTracker(max_history=100)
        >>> tracker.record_price("food", 10.0, quantity=5.0)
        >>> avg = tracker.get_average_price("food", window=10)
    """

    DEFAULT_MAX_HISTORY: int = 1000

    def __init__(self, max_history: int = DEFAULT_MAX_HISTORY) -> None:
        """
        Initialize PriceTracker.

        Args:
            max_history: Maximum price points per resource
        """
        self._max_history = max_history
        self._price_history: Dict[str, deque] = {}

    def record_price(
        self,
        resource_type: str,
        price: float,
        quantity: Optional[float] = None,
        timestamp: Optional[float] = None
    ) -> None:
        """
        Record a price point.

        Args:
            resource_type: Resource type string
            price: Price per unit
            quantity: Optional trade quantity
            timestamp: Optional timestamp (uses current time if None)
        """
        resource_name = str(resource_type)

        if resource_name not in self._price_history:
            self._price_history[resource_name] = deque(maxlen=self._max_history)

        point = PricePoint(
            timestamp=timestamp or time.time(),
            price=price,
            resource_type=resource_name,
            quantity_traded=quantity
        )

        self._price_history[resource_name].append(point)

    def get_current_price(self, resource_type: str) -> Optional[float]:
        """
        Get most recent price for resource.

        Args:
            resource_type: Resource type string

        Returns:
            Optional[float]: Latest price or None
        """
        resource_name = str(resource_type)
        history = self._price_history.get(resource_name)

        if history and len(history) > 0:
            return history[-1].price
        return None

    def get_average_price(
        self,
        resource_type: str,
        window: Optional[int] = None
    ) -> Optional[float]:
        """
        Get average price over window.

        Args:
            resource_type: Resource type string
            window: Number of recent points (None = all)

        Returns:
            Optional[float]: Average price or None
        """
        resource_name = str(resource_type)
        history = self._price_history.get(resource_name)

        if not history or len(history) == 0:
            return None

        points = list(history)
        if window is not None:
            points = points[-window:]

        return sum(p.price for p in points) / len(points)

    def get_price_trend(
        self,
        resource_type: str,
        window: int = 10
    ) -> Optional[float]:
        """
        Get price trend (positive = increasing).

        Simple linear regression slope.

        Args:
            resource_type: Resource type string
            window: Points to consider

        Returns:
            Optional[float]: Trend slope or None
        """
        resource_name = str(resource_type)
        history = self._price_history.get(resource_name)

        if not history or len(history) < 2:
            return None

        points = list(history)[-window:]
        if len(points) < 2:
            return None

        # Simple slope calculation
        n = len(points)
        x_mean = (n - 1) / 2
        y_mean = sum(p.price for p in points) / n

        numerator = sum((i - x_mean) * (p.price - y_mean) for i, p in enumerate(points))
        denominator = sum((i - x_mean) ** 2 for i in range(n))

        if denominator == 0:
            return 0.0

        return numerator / denominator

    def get_price_history(
        self,
        resource_type: str,
        limit: Optional[int] = None
    ) -> List[PricePoint]:
        """
        Get price history for resource.

        Args:
            resource_type: Resource type string
            limit: Max points to return (None = all)

        Returns:
            List[PricePoint]: Historical price points
        """
        resource_name = str(resource_type)
        history = self._price_history.get(resource_name)

        if not history:
            return []

        points = list(history)
        if limit is not None:
            points = points[-limit:]

        return points

    def get_volatility(
        self,
        resource_type: str,
        window: int = 10
    ) -> Optional[float]:
        """
        Get price volatility (standard deviation).

        Args:
            resource_type: Resource type string
            window: Points to consider

        Returns:
            Optional[float]: Price standard deviation or None
        """
        resource_name = str(resource_type)
        history = self._price_history.get(resource_name)

        if not history or len(history) < 2:
            return None

        points = list(history)[-window:]
        if len(points) < 2:
            return None

        mean = sum(p.price for p in points) / len(points)
        variance = sum((p.price - mean) ** 2 for p in points) / len(points)

        return variance ** 0.5

    def clear_history(self, resource_type: Optional[str] = None) -> None:
        """
        Clear price history.

        Args:
            resource_type: Specific resource or None for all
        """
        if resource_type is not None:
            resource_name = str(resource_type)
            if resource_name in self._price_history:
                self._price_history[resource_name].clear()
        else:
            self._price_history.clear()

    def __repr__(self) -> str:
        """String representation."""
        tracked = len(self._price_history)
        total_points = sum(len(h) for h in self._price_history.values())
        return f"PriceTracker(resources={tracked}, points={total_points})"
