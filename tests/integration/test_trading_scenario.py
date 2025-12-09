"""Integration tests for trading scenarios.

This module tests complete trading workflows involving:
- Marketplace operations
- Multiple agents trading
- Price changes over time
- Supply and demand effects
"""
import pytest
import sys
import os

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src')
sys.path.insert(0, src_path)

from economy.marketplace import (
    Marketplace,
    MarketplaceConfig,
    MarketplaceObserver,
    MarketEvent,
    MarketEventType,
)
from economy.pricing import (
    FixedPricing,
    SupplyDemandPricing,
    PriceTracker,
    PriceVolatility,
)


class TradingAnalytics(MarketplaceObserver):
    """Observer to track trading analytics."""

    def __init__(self):
        self.offers_created = 0
        self.trades_completed = 0
        self.total_volume = 0.0
        self.total_value = 0.0

    def on_market_event(self, event: MarketEvent) -> None:
        if event.event_type == MarketEventType.OFFER_CREATED:
            self.offers_created += 1
        elif event.event_type == MarketEventType.TRADE_COMPLETED:
            self.trades_completed += 1
            self.total_volume += event.data.get("quantity", 0)
            self.total_value += (
                event.data.get("quantity", 0) *
                event.data.get("price", 0)
            )


class TestBasicTradingWorkflow:
    """Tests for basic trading operations."""

    def test_create_offer_and_accept(self):
        """Test complete trade from offer creation to acceptance."""
        marketplace = Marketplace()

        # Seller creates offer
        offer = marketplace.create_offer(
            seller_id="seller1",
            resource_type="food",
            quantity=50.0,
            price_per_unit=5.0
        )

        assert offer is not None

        # Buyer accepts offer
        record = marketplace.accept_offer(offer.offer_id, "buyer1")

        assert record is not None
        assert record.quantity == 50.0
        assert record.total_price == 250.0
        assert record.seller_id == "seller1"
        assert record.buyer_id == "buyer1"

    def test_partial_trade(self):
        """Test partial purchase of an offer."""
        marketplace = Marketplace()

        # Create large offer
        offer = marketplace.create_offer(
            seller_id="seller1",
            resource_type="food",
            quantity=100.0,
            price_per_unit=5.0,
            min_quantity=10.0
        )

        # Buy only part
        record1 = marketplace.accept_offer(offer.offer_id, "buyer1", quantity=30.0)
        assert record1.quantity == 30.0

        # Check remaining
        updated_offer = marketplace.get_offer(offer.offer_id)
        assert updated_offer.quantity == 70.0

        # Another buyer takes the rest
        record2 = marketplace.accept_offer(offer.offer_id, "buyer2", quantity=70.0)
        assert record2.quantity == 70.0

        # Offer should be completed
        final_offer = marketplace.get_offer(offer.offer_id)
        assert final_offer is None  # Removed after completion


class TestMultipleSellerMarket:
    """Tests for market with multiple sellers."""

    def test_price_competition(self):
        """Test buyers get best price from competing sellers."""
        marketplace = Marketplace()

        # Multiple sellers with different prices
        offer1 = marketplace.create_offer("seller1", "food", 50.0, price_per_unit=6.0)
        offer2 = marketplace.create_offer("seller2", "food", 50.0, price_per_unit=5.0)
        offer3 = marketplace.create_offer("seller3", "food", 50.0, price_per_unit=7.0)

        # Get best offer
        best = marketplace.get_best_offer("food")

        assert best is not None
        assert best.price_per_unit == 5.0
        assert best.offer_id == offer2.offer_id

    def test_resource_specific_offers(self):
        """Test offers are filtered by resource type."""
        marketplace = Marketplace()

        marketplace.create_offer("seller1", "food", 50.0, price_per_unit=5.0)
        marketplace.create_offer("seller2", "wood", 100.0, price_per_unit=3.0)
        marketplace.create_offer("seller3", "food", 30.0, price_per_unit=4.0)
        marketplace.create_offer("seller4", "stone", 75.0, price_per_unit=8.0)

        food_offers = marketplace.get_offers_for_resource("food")
        wood_offers = marketplace.get_offers_for_resource("wood")

        assert len(food_offers) == 2
        assert len(wood_offers) == 1


class TestMarketplaceWithAnalytics:
    """Tests for marketplace with analytics observer."""

    def test_analytics_tracking(self):
        """Test analytics observer receives events."""
        marketplace = Marketplace()
        analytics = TradingAnalytics()
        marketplace.add_observer(analytics)

        # Create several offers
        for i in range(3):
            offer = marketplace.create_offer(
                f"seller{i}",
                "food",
                50.0,
                price_per_unit=5.0
            )
            marketplace.accept_offer(offer.offer_id, f"buyer{i}")

        assert analytics.offers_created == 3
        assert analytics.trades_completed == 3
        assert analytics.total_volume == 150.0
        assert analytics.total_value == 750.0


class TestPriceTracking:
    """Tests for price tracking integration."""

    def test_price_history_builds(self):
        """Test marketplace builds price history."""
        config = MarketplaceConfig(enable_price_tracking=True)
        marketplace = Marketplace(config=config)

        # Execute several trades at different prices
        prices = [5.0, 6.0, 7.0, 5.5, 6.5]
        for i, price in enumerate(prices):
            offer = marketplace.create_offer(
                f"seller{i}",
                "food",
                10.0,
                price_per_unit=price
            )
            marketplace.accept_offer(offer.offer_id, f"buyer{i}")

        # Check that price tracker has data
        tracker = marketplace._price_tracker
        assert tracker is not None

        current_price = tracker.get_current_price("food")
        assert current_price == 6.5  # Last trade price

        avg_price = tracker.get_average_price("food")
        assert avg_price == pytest.approx(6.0)  # Mean of all prices


class TestSupplyDemandPricing:
    """Tests for supply/demand based pricing."""

    def test_supply_tracking(self):
        """Test marketplace tracks supply."""
        marketplace = Marketplace()

        # Create offers to build supply
        marketplace.create_offer("seller1", "food", 100.0)
        marketplace.create_offer("seller2", "food", 50.0)

        supply_demand = marketplace.get_supply_demand("food")
        assert supply_demand["supply"] == 150.0

    def test_demand_recording(self):
        """Test marketplace tracks demand."""
        marketplace = Marketplace()

        # Record demand
        marketplace.record_demand("food", 75.0)
        marketplace.record_demand("food", 25.0)

        supply_demand = marketplace.get_supply_demand("food")
        assert supply_demand["demand"] == 100.0


class TestMarketplaceStatistics:
    """Tests for marketplace statistics."""

    def test_statistics_comprehensive(self):
        """Test comprehensive statistics."""
        marketplace = Marketplace()

        # Build up some activity
        for i in range(5):
            offer = marketplace.create_offer(f"seller{i}", "food", 20.0, price_per_unit=5.0)
            if i % 2 == 0:  # Accept every other offer
                marketplace.accept_offer(offer.offer_id, f"buyer{i}")

        stats = marketplace.get_statistics()

        # Should have 2 active offers (indices 1 and 3)
        assert stats["active_offers"] == 2
        # Should have 3 completed trades (indices 0, 2, 4)
        assert stats["total_trades"] == 3


class TestEdgeCases:
    """Tests for edge cases and error handling."""

    def test_accept_nonexistent_offer(self):
        """Test accepting nonexistent offer fails gracefully."""
        marketplace = Marketplace()

        record = marketplace.accept_offer("fake-offer-id", "buyer1")
        assert record is None

    def test_cancel_offer(self):
        """Test cancelling an offer."""
        marketplace = Marketplace()

        offer = marketplace.create_offer("seller1", "food", 50.0)

        result = marketplace.cancel_offer(offer.offer_id, "seller1")
        assert result is True

        # Offer should be gone
        assert marketplace.get_offer(offer.offer_id) is None

    def test_cannot_cancel_others_offer(self):
        """Test cannot cancel another seller's offer."""
        marketplace = Marketplace()

        offer = marketplace.create_offer("seller1", "food", 50.0)

        result = marketplace.cancel_offer(offer.offer_id, "seller2")
        assert result is False

        # Offer should still exist
        assert marketplace.get_offer(offer.offer_id) is not None
