"""
Marketplace Module

This module provides a centralized marketplace for trading resources.
The marketplace coordinates trades between agents and tracks market data.

Design Patterns:
    - Mediator Pattern: Marketplace coordinates trades between agents
    - Observer Pattern: Notifies observers of market events
    - Factory Pattern: Creates trade offers and records

SOLID Principles:
    - Single Responsibility: Marketplace manages trade coordination
    - Open/Closed: Observers can be added without modification
    - Dependency Inversion: Depends on abstract PricingStrategy

Integration:
    - Uses economy/pricing.py for price calculations
    - Uses inventory/transfer.py for resource transfers
    - Uses social/relationships.py for relationship-based trades
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import TYPE_CHECKING, Optional, Dict, List, Set, Any, Callable
from collections import defaultdict
import time
import uuid

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from economy.pricing import PricingStrategy, FixedPricing, PriceTracker

if TYPE_CHECKING:
    from agents.agent import Agent


class OfferStatus(Enum):
    """Status of a trade offer."""
    PENDING = auto()      # Awaiting buyer
    ACCEPTED = auto()     # Trade completed
    CANCELLED = auto()    # Seller cancelled
    EXPIRED = auto()      # Offer timed out
    PARTIAL = auto()      # Partially filled


class MarketEventType(Enum):
    """Types of marketplace events."""
    OFFER_CREATED = auto()
    OFFER_CANCELLED = auto()
    OFFER_EXPIRED = auto()
    TRADE_COMPLETED = auto()
    PRICE_CHANGED = auto()


@dataclass
class MarketEvent:
    """
    An event that occurred in the marketplace.

    Attributes:
        event_type: Type of event
        timestamp: When event occurred
        data: Event-specific data
    """
    event_type: MarketEventType
    timestamp: float
    data: Dict[str, Any]


@dataclass
class TradeOffer:
    """
    A trade offer in the marketplace.

    Represents a seller's offer to sell resources at a price.
    Buyers can accept offers to complete trades.

    Attributes:
        offer_id: Unique identifier
        seller_id: Agent selling resources
        resource_type: Type of resource
        quantity: Amount available
        price_per_unit: Price for each unit
        created_at: Creation timestamp
        expires_at: Expiration timestamp (None = no expiry)
        status: Current offer status
        min_quantity: Minimum purchase amount
    """
    offer_id: str
    seller_id: str
    resource_type: str
    quantity: float
    price_per_unit: float
    created_at: float
    expires_at: Optional[float] = None
    status: OfferStatus = OfferStatus.PENDING
    min_quantity: float = 1.0

    @property
    def total_value(self) -> float:
        """Total value of the offer."""
        return self.quantity * self.price_per_unit

    @property
    def is_active(self) -> bool:
        """Whether offer can still be accepted."""
        if self.status not in (OfferStatus.PENDING, OfferStatus.PARTIAL):
            return False
        if self.expires_at is not None and time.time() > self.expires_at:
            return False
        return True


@dataclass
class TradeRecord:
    """
    Record of a completed trade.

    Immutable record of a transaction for history and analytics.

    Attributes:
        trade_id: Unique identifier
        offer_id: Original offer ID
        seller_id: Seller agent ID
        buyer_id: Buyer agent ID
        resource_type: Resource traded
        quantity: Amount traded
        price_per_unit: Unit price
        total_price: Total transaction value
        timestamp: When trade occurred
    """
    trade_id: str
    offer_id: str
    seller_id: str
    buyer_id: str
    resource_type: str
    quantity: float
    price_per_unit: float
    total_price: float
    timestamp: float


@dataclass
class MarketplaceConfig:
    """
    Configuration for marketplace behavior.

    Attributes:
        default_offer_duration: Default offer expiry (seconds)
        min_offer_quantity: Minimum quantity for offers
        max_active_offers: Max offers per seller
        enable_price_tracking: Whether to track prices
        transaction_fee_rate: Fee as fraction of trade (0-1)
    """
    default_offer_duration: Optional[float] = None  # None = no expiry
    min_offer_quantity: float = 0.1
    max_active_offers: int = 10
    enable_price_tracking: bool = True
    transaction_fee_rate: float = 0.0


class MarketplaceObserver(ABC):
    """
    Abstract observer for marketplace events.

    Implementations can react to market events for analytics,
    logging, AI decision making, etc.

    Design Pattern: Observer

    Examples:
        >>> class PriceLogger(MarketplaceObserver):
        ...     def on_market_event(self, event):
        ...         if event.event_type == MarketEventType.TRADE_COMPLETED:
        ...             print(f"Trade: {event.data}")
    """

    @abstractmethod
    def on_market_event(self, event: MarketEvent) -> None:
        """
        Handle a marketplace event.

        Args:
            event: The market event that occurred
        """
        pass


class Marketplace:
    """
    Central marketplace for resource trading.

    Coordinates trades between agents, maintains offers,
    and tracks market data. Uses pricing strategies for
    price calculation.

    Design Patterns:
        - Mediator: Coordinates agent trades
        - Observer: Notifies observers of events
        - Strategy: Pluggable pricing strategies

    Attributes:
        pricing_strategy: Strategy for price calculations
        config: Marketplace configuration
        offers: Active trade offers
        trade_history: Completed trades
        observers: Event observers

    Examples:
        >>> marketplace = Marketplace(SupplyDemandPricing())
        >>> offer = marketplace.create_offer("agent1", "food", 10.0)
        >>> record = marketplace.accept_offer(offer.offer_id, "agent2")
    """

    # Default base prices for resources
    DEFAULT_BASE_PRICES: Dict[str, float] = {
        "food": 10.0,
        "wood": 8.0,
        "stone": 12.0,
        "metal": 20.0,
        "gold": 50.0,
    }

    def __init__(
        self,
        pricing_strategy: Optional[PricingStrategy] = None,
        config: Optional[MarketplaceConfig] = None
    ) -> None:
        """
        Initialize Marketplace.

        Args:
            pricing_strategy: Strategy for pricing (default: FixedPricing)
            config: Marketplace configuration
        """
        self._pricing_strategy = pricing_strategy or FixedPricing()
        self._config = config or MarketplaceConfig()

        # Active offers by offer_id
        self._offers: Dict[str, TradeOffer] = {}

        # Offers indexed by resource type
        self._offers_by_resource: Dict[str, Set[str]] = defaultdict(set)

        # Offers indexed by seller
        self._offers_by_seller: Dict[str, Set[str]] = defaultdict(set)

        # Trade history
        self._trade_history: List[TradeRecord] = []

        # Price tracker
        self._price_tracker: Optional[PriceTracker] = None
        if self._config.enable_price_tracking:
            self._price_tracker = PriceTracker()

        # Observers
        self._observers: List[MarketplaceObserver] = []

        # Supply and demand tracking
        self._supply: Dict[str, float] = defaultdict(float)
        self._demand: Dict[str, float] = defaultdict(float)

    @property
    def pricing_strategy(self) -> PricingStrategy:
        """Current pricing strategy."""
        return self._pricing_strategy

    @property
    def config(self) -> MarketplaceConfig:
        """Marketplace configuration."""
        return self._config

    def create_offer(
        self,
        seller_id: str,
        resource_type: str,
        quantity: float,
        price_per_unit: Optional[float] = None,
        duration: Optional[float] = None,
        min_quantity: float = 1.0
    ) -> Optional[TradeOffer]:
        """
        Create a new trade offer.

        Creates an offer for selling resources. If no price is
        specified, uses the pricing strategy to calculate one.

        Args:
            seller_id: ID of selling agent
            resource_type: Type of resource to sell
            quantity: Amount to sell
            price_per_unit: Price per unit (None = auto-calculate)
            duration: Offer duration in seconds (None = config default)
            min_quantity: Minimum purchase amount

        Returns:
            Optional[TradeOffer]: Created offer or None if invalid

        Raises:
            ValueError: If quantity < min_offer_quantity

        Note:
            Implementation would verify seller has resources.
        """
        # Validate quantity
        if quantity < self._config.min_offer_quantity:
            return None

        # Check seller offer limit
        if len(self._offers_by_seller[seller_id]) >= self._config.max_active_offers:
            return None

        # Calculate price if not provided
        if price_per_unit is None:
            base_price = self.DEFAULT_BASE_PRICES.get(resource_type, 10.0)
            price_per_unit = self._pricing_strategy.calculate_price(
                resource_type, self, base_price
            )

        # Calculate expiry
        expires_at = None
        effective_duration = duration or self._config.default_offer_duration
        if effective_duration is not None:
            expires_at = time.time() + effective_duration

        # Create offer
        offer = TradeOffer(
            offer_id=str(uuid.uuid4()),
            seller_id=seller_id,
            resource_type=resource_type,
            quantity=quantity,
            price_per_unit=price_per_unit,
            created_at=time.time(),
            expires_at=expires_at,
            status=OfferStatus.PENDING,
            min_quantity=min_quantity
        )

        # Register offer
        self._offers[offer.offer_id] = offer
        self._offers_by_resource[resource_type].add(offer.offer_id)
        self._offers_by_seller[seller_id].add(offer.offer_id)

        # Update supply tracking
        self._supply[resource_type] += quantity

        # Notify observers
        self._notify_observers(MarketEvent(
            event_type=MarketEventType.OFFER_CREATED,
            timestamp=time.time(),
            data={"offer_id": offer.offer_id, "resource": resource_type, "quantity": quantity}
        ))

        return offer

    def accept_offer(
        self,
        offer_id: str,
        buyer_id: str,
        quantity: Optional[float] = None
    ) -> Optional[TradeRecord]:
        """
        Accept a trade offer.

        Buyer accepts an offer, completing the trade.
        Can accept partial quantity if offer allows.

        Args:
            offer_id: ID of offer to accept
            buyer_id: ID of buying agent
            quantity: Amount to buy (None = full offer)

        Returns:
            Optional[TradeRecord]: Trade record or None if failed

        Note:
            Implementation would:
            1. Verify buyer has funds
            2. Verify seller still has resources
            3. Execute transfer
            4. Record trade
        """
        offer = self._offers.get(offer_id)
        if offer is None or not offer.is_active:
            return None

        # Cannot buy from self
        if buyer_id == offer.seller_id:
            return None

        # Determine quantity
        trade_quantity = quantity if quantity is not None else offer.quantity

        # Validate quantity
        if trade_quantity < offer.min_quantity:
            return None
        if trade_quantity > offer.quantity:
            trade_quantity = offer.quantity

        # Calculate total price
        total_price = trade_quantity * offer.price_per_unit

        # Apply transaction fee (if any)
        fee = total_price * self._config.transaction_fee_rate

        # Create trade record
        record = TradeRecord(
            trade_id=str(uuid.uuid4()),
            offer_id=offer_id,
            seller_id=offer.seller_id,
            buyer_id=buyer_id,
            resource_type=offer.resource_type,
            quantity=trade_quantity,
            price_per_unit=offer.price_per_unit,
            total_price=total_price,
            timestamp=time.time()
        )

        # Update offer
        offer.quantity -= trade_quantity
        if offer.quantity <= 0:
            offer.status = OfferStatus.ACCEPTED
            self._remove_offer(offer_id)
        else:
            offer.status = OfferStatus.PARTIAL

        # Update supply tracking
        self._supply[offer.resource_type] -= trade_quantity

        # Record trade
        self._trade_history.append(record)

        # Track price
        if self._price_tracker is not None:
            self._price_tracker.record_price(
                offer.resource_type,
                offer.price_per_unit,
                quantity=trade_quantity
            )

        # Notify observers
        self._notify_observers(MarketEvent(
            event_type=MarketEventType.TRADE_COMPLETED,
            timestamp=time.time(),
            data={
                "trade_id": record.trade_id,
                "seller": offer.seller_id,
                "buyer": buyer_id,
                "resource": offer.resource_type,
                "quantity": trade_quantity,
                "price": offer.price_per_unit
            }
        ))

        return record

    def cancel_offer(self, offer_id: str, seller_id: str) -> bool:
        """
        Cancel a trade offer.

        Only the seller can cancel their own offer.

        Args:
            offer_id: ID of offer to cancel
            seller_id: ID of seller (for verification)

        Returns:
            bool: True if cancelled, False if not found/unauthorized
        """
        offer = self._offers.get(offer_id)
        if offer is None:
            return False

        if offer.seller_id != seller_id:
            return False

        offer.status = OfferStatus.CANCELLED
        self._supply[offer.resource_type] -= offer.quantity
        self._remove_offer(offer_id)

        self._notify_observers(MarketEvent(
            event_type=MarketEventType.OFFER_CANCELLED,
            timestamp=time.time(),
            data={"offer_id": offer_id}
        ))

        return True

    def get_offer(self, offer_id: str) -> Optional[TradeOffer]:
        """
        Get offer by ID.

        Args:
            offer_id: Offer ID

        Returns:
            Optional[TradeOffer]: Offer or None
        """
        return self._offers.get(offer_id)

    def get_offers_for_resource(
        self,
        resource_type: str,
        active_only: bool = True
    ) -> List[TradeOffer]:
        """
        Get all offers for a resource type.

        Args:
            resource_type: Resource type to find
            active_only: Only return active offers

        Returns:
            List[TradeOffer]: Matching offers
        """
        offer_ids = self._offers_by_resource.get(resource_type, set())
        offers = [self._offers[oid] for oid in offer_ids if oid in self._offers]

        if active_only:
            offers = [o for o in offers if o.is_active]

        return sorted(offers, key=lambda o: o.price_per_unit)

    def get_offers_by_seller(self, seller_id: str) -> List[TradeOffer]:
        """
        Get all offers by a seller.

        Args:
            seller_id: Seller agent ID

        Returns:
            List[TradeOffer]: Seller's offers
        """
        offer_ids = self._offers_by_seller.get(seller_id, set())
        return [self._offers[oid] for oid in offer_ids if oid in self._offers]

    def get_market_price(self, resource_type: str) -> float:
        """
        Get current market price for resource.

        Uses pricing strategy with current market state.

        Args:
            resource_type: Resource type

        Returns:
            float: Current market price
        """
        base_price = self.DEFAULT_BASE_PRICES.get(resource_type, 10.0)
        return self._pricing_strategy.calculate_price(resource_type, self, base_price)

    def get_best_offer(self, resource_type: str) -> Optional[TradeOffer]:
        """
        Get best (lowest price) active offer for resource.

        Args:
            resource_type: Resource type

        Returns:
            Optional[TradeOffer]: Best offer or None
        """
        offers = self.get_offers_for_resource(resource_type, active_only=True)
        return offers[0] if offers else None

    def get_trade_history(
        self,
        resource_type: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[TradeRecord]:
        """
        Get trade history.

        Args:
            resource_type: Filter by resource (None = all)
            limit: Max records to return

        Returns:
            List[TradeRecord]: Trade records
        """
        records = self._trade_history

        if resource_type is not None:
            records = [r for r in records if r.resource_type == resource_type]

        if limit is not None:
            records = records[-limit:]

        return records

    def get_supply_demand(self, resource_type: str) -> Dict[str, float]:
        """
        Get supply and demand data for resource.

        Args:
            resource_type: Resource type

        Returns:
            Dict with 'supply' and 'demand' keys
        """
        return {
            "supply": self._supply.get(resource_type, 0.0),
            "demand": self._demand.get(resource_type, 0.0)
        }

    def record_demand(self, resource_type: str, quantity: float) -> None:
        """
        Record demand for a resource.

        Used for supply/demand pricing calculations.

        Args:
            resource_type: Resource type
            quantity: Amount demanded
        """
        self._demand[resource_type] += quantity

    def add_observer(self, observer: MarketplaceObserver) -> None:
        """
        Add marketplace observer.

        Args:
            observer: Observer to add
        """
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: MarketplaceObserver) -> None:
        """
        Remove marketplace observer.

        Args:
            observer: Observer to remove
        """
        if observer in self._observers:
            self._observers.remove(observer)

    def set_pricing_strategy(self, strategy: PricingStrategy) -> None:
        """
        Change pricing strategy.

        Args:
            strategy: New pricing strategy
        """
        old_strategy = self._pricing_strategy
        self._pricing_strategy = strategy

        self._notify_observers(MarketEvent(
            event_type=MarketEventType.PRICE_CHANGED,
            timestamp=time.time(),
            data={
                "old_strategy": old_strategy.get_name(),
                "new_strategy": strategy.get_name()
            }
        ))

    def cleanup_expired_offers(self) -> int:
        """
        Remove expired offers.

        Should be called periodically.

        Returns:
            int: Number of offers expired
        """
        current_time = time.time()
        expired = []

        for offer_id, offer in self._offers.items():
            if offer.expires_at is not None and current_time > offer.expires_at:
                offer.status = OfferStatus.EXPIRED
                expired.append(offer_id)

        for offer_id in expired:
            offer = self._offers[offer_id]
            self._supply[offer.resource_type] -= offer.quantity
            self._remove_offer(offer_id)

            self._notify_observers(MarketEvent(
                event_type=MarketEventType.OFFER_EXPIRED,
                timestamp=current_time,
                data={"offer_id": offer_id}
            ))

        return len(expired)

    def get_statistics(self) -> Dict[str, Any]:
        """
        Get marketplace statistics.

        Returns:
            Dict with various market statistics
        """
        return {
            "active_offers": len(self._offers),
            "total_trades": len(self._trade_history),
            "tracked_resources": list(self._supply.keys()),
            "pricing_strategy": self._pricing_strategy.get_name(),
            "observers": len(self._observers)
        }

    def _remove_offer(self, offer_id: str) -> None:
        """Remove offer from all indices."""
        offer = self._offers.pop(offer_id, None)
        if offer is not None:
            self._offers_by_resource[offer.resource_type].discard(offer_id)
            self._offers_by_seller[offer.seller_id].discard(offer_id)

    def _notify_observers(self, event: MarketEvent) -> None:
        """Notify all observers of an event."""
        for observer in self._observers:
            try:
                observer.on_market_event(event)
            except Exception:
                pass  # Don't let observer errors break marketplace

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Marketplace("
            f"offers={len(self._offers)}, "
            f"trades={len(self._trade_history)}, "
            f"strategy={self._pricing_strategy.get_name()})"
        )
