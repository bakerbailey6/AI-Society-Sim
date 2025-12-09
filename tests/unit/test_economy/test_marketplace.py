"""Tests for economy marketplace.

This module tests the marketplace system including:
- TradeOffer creation and management
- Trade execution
- Marketplace observers
- Supply/demand tracking
"""
import pytest
import sys
import os
import time

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src')
sys.path.insert(0, src_path)

from economy.marketplace import (
    Marketplace,
    MarketplaceConfig,
    TradeOffer,
    TradeRecord,
    OfferStatus,
    MarketplaceObserver,
    MarketEvent,
    MarketEventType,
)
from economy.pricing import FixedPricing


class MockMarketplaceObserver(MarketplaceObserver):
    """Mock observer for testing."""

    def __init__(self):
        self.events = []

    def on_market_event(self, event: MarketEvent) -> None:
        self.events.append(event)


class TestTradeOffer:
    """Tests for TradeOffer dataclass."""

    def test_total_value(self):
        """Test total value calculation."""
        offer = TradeOffer(
            offer_id="test",
            seller_id="seller",
            resource_type="food",
            quantity=10.0,
            price_per_unit=5.0,
            created_at=time.time()
        )
        assert offer.total_value == 50.0

    def test_is_active_pending(self):
        """Test active status for pending offer."""
        offer = TradeOffer(
            offer_id="test",
            seller_id="seller",
            resource_type="food",
            quantity=10.0,
            price_per_unit=5.0,
            created_at=time.time(),
            status=OfferStatus.PENDING
        )
        assert offer.is_active is True

    def test_is_active_expired(self):
        """Test active status for expired offer."""
        offer = TradeOffer(
            offer_id="test",
            seller_id="seller",
            resource_type="food",
            quantity=10.0,
            price_per_unit=5.0,
            created_at=time.time() - 100,
            expires_at=time.time() - 50,  # Already expired
            status=OfferStatus.PENDING
        )
        assert offer.is_active is False

    def test_is_active_cancelled(self):
        """Test active status for cancelled offer."""
        offer = TradeOffer(
            offer_id="test",
            seller_id="seller",
            resource_type="food",
            quantity=10.0,
            price_per_unit=5.0,
            created_at=time.time(),
            status=OfferStatus.CANCELLED
        )
        assert offer.is_active is False


class TestMarketplace:
    """Tests for Marketplace."""

    def test_initialization_default(self):
        """Test default initialization."""
        marketplace = Marketplace()
        assert marketplace.pricing_strategy is not None
        assert "Marketplace" in repr(marketplace)

    def test_initialization_with_config(self):
        """Test initialization with config."""
        config = MarketplaceConfig(
            max_active_offers=5,
            transaction_fee_rate=0.05
        )
        marketplace = Marketplace(config=config)
        assert marketplace.config.max_active_offers == 5

    def test_create_offer(self):
        """Test creating a trade offer."""
        marketplace = Marketplace()
        offer = marketplace.create_offer(
            seller_id="seller1",
            resource_type="food",
            quantity=10.0,
            price_per_unit=5.0
        )

        assert offer is not None
        assert offer.seller_id == "seller1"
        assert offer.resource_type == "food"
        assert offer.quantity == 10.0
        assert offer.price_per_unit == 5.0

    def test_create_offer_auto_price(self):
        """Test creating offer with auto-calculated price."""
        pricing = FixedPricing({"food": 7.5})
        marketplace = Marketplace(pricing_strategy=pricing)

        offer = marketplace.create_offer(
            seller_id="seller1",
            resource_type="food",
            quantity=10.0
        )

        assert offer is not None
        assert offer.price_per_unit == 7.5

    def test_create_offer_min_quantity(self):
        """Test offer rejected below minimum quantity."""
        config = MarketplaceConfig(min_offer_quantity=1.0)
        marketplace = Marketplace(config=config)

        offer = marketplace.create_offer(
            seller_id="seller1",
            resource_type="food",
            quantity=0.5  # Below minimum
        )

        assert offer is None

    def test_create_offer_max_offers(self):
        """Test offer rejected when max offers reached."""
        config = MarketplaceConfig(max_active_offers=2)
        marketplace = Marketplace(config=config)

        # Create max offers
        marketplace.create_offer("seller1", "food", 10.0)
        marketplace.create_offer("seller1", "wood", 10.0)

        # Third should fail
        offer = marketplace.create_offer("seller1", "stone", 10.0)
        assert offer is None

    def test_accept_offer(self):
        """Test accepting a trade offer."""
        marketplace = Marketplace()
        offer = marketplace.create_offer(
            seller_id="seller1",
            resource_type="food",
            quantity=10.0,
            price_per_unit=5.0
        )

        record = marketplace.accept_offer(offer.offer_id, "buyer1")

        assert record is not None
        assert record.seller_id == "seller1"
        assert record.buyer_id == "buyer1"
        assert record.quantity == 10.0
        assert record.total_price == 50.0

    def test_accept_offer_partial(self):
        """Test accepting partial quantity."""
        marketplace = Marketplace()
        offer = marketplace.create_offer(
            seller_id="seller1",
            resource_type="food",
            quantity=10.0,
            price_per_unit=5.0,
            min_quantity=1.0
        )

        record = marketplace.accept_offer(offer.offer_id, "buyer1", quantity=5.0)

        assert record is not None
        assert record.quantity == 5.0
        assert record.total_price == 25.0

        # Check remaining quantity
        updated_offer = marketplace.get_offer(offer.offer_id)
        assert updated_offer.quantity == 5.0
        assert updated_offer.status == OfferStatus.PARTIAL

    def test_accept_offer_self_buy(self):
        """Test that seller cannot buy own offer."""
        marketplace = Marketplace()
        offer = marketplace.create_offer(
            seller_id="seller1",
            resource_type="food",
            quantity=10.0,
            price_per_unit=5.0
        )

        record = marketplace.accept_offer(offer.offer_id, "seller1")
        assert record is None

    def test_accept_offer_below_min(self):
        """Test accepting below minimum quantity."""
        marketplace = Marketplace()
        offer = marketplace.create_offer(
            seller_id="seller1",
            resource_type="food",
            quantity=10.0,
            price_per_unit=5.0,
            min_quantity=5.0
        )

        record = marketplace.accept_offer(offer.offer_id, "buyer1", quantity=2.0)
        assert record is None

    def test_cancel_offer(self):
        """Test cancelling an offer."""
        marketplace = Marketplace()
        offer = marketplace.create_offer(
            seller_id="seller1",
            resource_type="food",
            quantity=10.0
        )

        result = marketplace.cancel_offer(offer.offer_id, "seller1")
        assert result is True

        # Offer should be gone
        assert marketplace.get_offer(offer.offer_id) is None

    def test_cancel_offer_wrong_seller(self):
        """Test that wrong seller cannot cancel."""
        marketplace = Marketplace()
        offer = marketplace.create_offer(
            seller_id="seller1",
            resource_type="food",
            quantity=10.0
        )

        result = marketplace.cancel_offer(offer.offer_id, "other_seller")
        assert result is False

    def test_get_offers_for_resource(self):
        """Test getting offers by resource type."""
        marketplace = Marketplace()
        marketplace.create_offer("seller1", "food", 10.0, price_per_unit=5.0)
        marketplace.create_offer("seller2", "food", 20.0, price_per_unit=4.0)
        marketplace.create_offer("seller3", "wood", 15.0, price_per_unit=3.0)

        food_offers = marketplace.get_offers_for_resource("food")

        assert len(food_offers) == 2
        # Should be sorted by price
        assert food_offers[0].price_per_unit <= food_offers[1].price_per_unit

    def test_get_offers_by_seller(self):
        """Test getting offers by seller."""
        marketplace = Marketplace()
        marketplace.create_offer("seller1", "food", 10.0)
        marketplace.create_offer("seller1", "wood", 15.0)
        marketplace.create_offer("seller2", "stone", 20.0)

        seller1_offers = marketplace.get_offers_by_seller("seller1")

        assert len(seller1_offers) == 2

    def test_get_best_offer(self):
        """Test getting best (lowest price) offer."""
        marketplace = Marketplace()
        marketplace.create_offer("seller1", "food", 10.0, price_per_unit=5.0)
        marketplace.create_offer("seller2", "food", 20.0, price_per_unit=3.0)
        marketplace.create_offer("seller3", "food", 15.0, price_per_unit=7.0)

        best = marketplace.get_best_offer("food")

        assert best is not None
        assert best.price_per_unit == 3.0

    def test_get_trade_history(self):
        """Test retrieving trade history."""
        marketplace = Marketplace()
        offer1 = marketplace.create_offer("seller1", "food", 10.0, price_per_unit=5.0)
        offer2 = marketplace.create_offer("seller2", "wood", 20.0, price_per_unit=3.0)

        marketplace.accept_offer(offer1.offer_id, "buyer1")
        marketplace.accept_offer(offer2.offer_id, "buyer2")

        history = marketplace.get_trade_history()
        assert len(history) == 2

    def test_get_trade_history_filtered(self):
        """Test retrieving filtered trade history."""
        marketplace = Marketplace()
        offer1 = marketplace.create_offer("seller1", "food", 10.0, price_per_unit=5.0)
        offer2 = marketplace.create_offer("seller2", "wood", 20.0, price_per_unit=3.0)

        marketplace.accept_offer(offer1.offer_id, "buyer1")
        marketplace.accept_offer(offer2.offer_id, "buyer2")

        food_history = marketplace.get_trade_history(resource_type="food")
        assert len(food_history) == 1
        assert food_history[0].resource_type == "food"

    def test_observer_notification(self):
        """Test observer receives events."""
        marketplace = Marketplace()
        observer = MockMarketplaceObserver()
        marketplace.add_observer(observer)

        # Create offer - should trigger event
        offer = marketplace.create_offer("seller1", "food", 10.0)
        assert len(observer.events) == 1
        assert observer.events[0].event_type == MarketEventType.OFFER_CREATED

        # Accept offer - should trigger event
        marketplace.accept_offer(offer.offer_id, "buyer1")
        assert len(observer.events) == 2
        assert observer.events[1].event_type == MarketEventType.TRADE_COMPLETED

    def test_remove_observer(self):
        """Test removing observer stops notifications."""
        marketplace = Marketplace()
        observer = MockMarketplaceObserver()
        marketplace.add_observer(observer)

        marketplace.create_offer("seller1", "food", 10.0)
        assert len(observer.events) == 1

        marketplace.remove_observer(observer)
        marketplace.create_offer("seller2", "wood", 15.0)
        assert len(observer.events) == 1  # No new events

    def test_get_supply_demand(self):
        """Test supply/demand tracking."""
        marketplace = Marketplace()
        marketplace.create_offer("seller1", "food", 10.0)
        marketplace.create_offer("seller2", "food", 20.0)

        data = marketplace.get_supply_demand("food")
        assert data["supply"] == 30.0

    def test_record_demand(self):
        """Test recording demand."""
        marketplace = Marketplace()
        marketplace.record_demand("food", 50.0)

        data = marketplace.get_supply_demand("food")
        assert data["demand"] == 50.0

    def test_set_pricing_strategy(self):
        """Test changing pricing strategy."""
        marketplace = Marketplace()
        new_strategy = FixedPricing({"food": 99.0})

        marketplace.set_pricing_strategy(new_strategy)

        assert marketplace.get_market_price("food") == 99.0

    def test_get_statistics(self):
        """Test getting marketplace statistics."""
        marketplace = Marketplace()
        marketplace.create_offer("seller1", "food", 10.0)

        stats = marketplace.get_statistics()

        assert stats["active_offers"] == 1
        assert stats["total_trades"] == 0
        assert "pricing_strategy" in stats

    def test_cleanup_expired_offers(self):
        """Test cleaning up expired offers."""
        config = MarketplaceConfig(default_offer_duration=0.01)  # Expires quickly
        marketplace = Marketplace(config=config)

        marketplace.create_offer("seller1", "food", 10.0, duration=0.01)
        time.sleep(0.02)  # Wait for expiry

        expired_count = marketplace.cleanup_expired_offers()
        assert expired_count == 1
        assert len(marketplace.get_offers_for_resource("food")) == 0
