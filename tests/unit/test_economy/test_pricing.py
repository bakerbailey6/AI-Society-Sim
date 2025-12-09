"""Tests for economy pricing strategies.

This module tests the pricing system including:
- FixedPricing strategy
- SupplyDemandPricing strategy
- RelationshipPricing strategy
- PriceTracker history management
"""
import pytest
import sys
import os

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src')
sys.path.insert(0, src_path)

from economy.pricing import (
    PricingStrategy,
    FixedPricing,
    SupplyDemandPricing,
    RelationshipPricing,
    PriceTracker,
    PriceVolatility,
    PricePoint,
)


class TestFixedPricing:
    """Tests for FixedPricing strategy."""

    def test_initialization_with_overrides(self):
        """Test initialization with price overrides."""
        overrides = {"food": 5.0, "wood": 3.0}
        pricing = FixedPricing(price_overrides=overrides)
        assert pricing.get_name() == "FixedPricing"

    def test_initialization_without_overrides(self):
        """Test initialization without overrides."""
        pricing = FixedPricing()
        assert pricing.get_name() == "FixedPricing"

    def test_calculate_price_with_override(self):
        """Test price calculation returns override when available."""
        pricing = FixedPricing({"food": 5.0})
        price = pricing.calculate_price("food", None, 10.0)
        assert price == 5.0

    def test_calculate_price_without_override(self):
        """Test price calculation returns base price when no override."""
        pricing = FixedPricing({"food": 5.0})
        price = pricing.calculate_price("wood", None, 10.0)
        assert price == 10.0

    def test_set_price(self):
        """Test setting price for a resource."""
        pricing = FixedPricing()
        pricing.set_price("gold", 50.0)
        price = pricing.calculate_price("gold", None, 10.0)
        assert price == 50.0


class TestSupplyDemandPricing:
    """Tests for SupplyDemandPricing strategy."""

    def test_initialization_default(self):
        """Test default initialization."""
        pricing = SupplyDemandPricing()
        assert "SupplyDemandPricing" in pricing.get_name()

    def test_initialization_with_volatility(self):
        """Test initialization with specific volatility."""
        pricing = SupplyDemandPricing(volatility=PriceVolatility.EXTREME)
        assert "EXTREME" in pricing.get_name()

    def test_calculate_price_returns_base_without_marketplace(self):
        """Test that price returns base when marketplace has no data."""
        pricing = SupplyDemandPricing()
        price = pricing.calculate_price("food", None, 10.0)
        assert price == 10.0

    def test_volatility_levels(self):
        """Test different volatility levels."""
        for volatility in PriceVolatility:
            pricing = SupplyDemandPricing(volatility=volatility)
            assert volatility.name in pricing.get_name()


class TestRelationshipPricing:
    """Tests for RelationshipPricing strategy."""

    def test_initialization(self):
        """Test initialization wraps base strategy."""
        base = FixedPricing({"food": 10.0})
        pricing = RelationshipPricing(base)
        assert "RelationshipPricing" in pricing.get_name()
        assert "FixedPricing" in pricing.get_name()

    def test_ally_discount(self):
        """Test ally discount is applied."""
        base = FixedPricing({"food": 10.0})
        pricing = RelationshipPricing(base, ally_discount=0.15)

        price = pricing.calculate_price_for_relationship(
            "food", None, 10.0, "ally", same_faction=False
        )
        assert price < 10.0
        assert price == pytest.approx(8.5)  # 10 * (1 - 0.15)

    def test_enemy_premium(self):
        """Test enemy premium is applied."""
        base = FixedPricing({"food": 10.0})
        pricing = RelationshipPricing(base, enemy_premium=0.25)

        price = pricing.calculate_price_for_relationship(
            "food", None, 10.0, "hostile", same_faction=False
        )
        assert price > 10.0
        assert price == pytest.approx(12.5)  # 10 * (1 + 0.25)

    def test_faction_discount(self):
        """Test faction discount is applied."""
        base = FixedPricing({"food": 10.0})
        pricing = RelationshipPricing(base, faction_discount=0.20)

        price = pricing.calculate_price_for_relationship(
            "food", None, 10.0, "neutral", same_faction=True
        )
        assert price == pytest.approx(8.0)  # 10 * (1 - 0.20)

    def test_combined_discounts(self):
        """Test ally and faction discounts stack."""
        base = FixedPricing({"food": 10.0})
        pricing = RelationshipPricing(
            base, ally_discount=0.15, faction_discount=0.20
        )

        price = pricing.calculate_price_for_relationship(
            "food", None, 10.0, "ally", same_faction=True
        )
        # 10 * (1 - 0.20) * (1 - 0.15) = 8.0 * 0.85 = 6.8
        assert price == pytest.approx(6.8)

    def test_minimum_price(self):
        """Test minimum price of 0.01 is enforced."""
        base = FixedPricing({"food": 0.01})
        pricing = RelationshipPricing(
            base, ally_discount=0.99, faction_discount=0.99
        )

        price = pricing.calculate_price_for_relationship(
            "food", None, 0.01, "ally", same_faction=True
        )
        assert price >= 0.01


class TestPriceTracker:
    """Tests for PriceTracker."""

    def test_initialization(self):
        """Test initialization."""
        tracker = PriceTracker(max_history=100)
        assert "PriceTracker" in repr(tracker)

    def test_record_price(self):
        """Test recording price points."""
        tracker = PriceTracker()
        tracker.record_price("food", 10.0)

        price = tracker.get_current_price("food")
        assert price == 10.0

    def test_record_multiple_prices(self):
        """Test recording multiple prices for same resource."""
        tracker = PriceTracker()
        tracker.record_price("food", 10.0)
        tracker.record_price("food", 12.0)
        tracker.record_price("food", 11.0)

        price = tracker.get_current_price("food")
        assert price == 11.0  # Most recent

    def test_get_average_price(self):
        """Test average price calculation."""
        tracker = PriceTracker()
        tracker.record_price("food", 10.0)
        tracker.record_price("food", 12.0)
        tracker.record_price("food", 14.0)

        avg = tracker.get_average_price("food")
        assert avg == pytest.approx(12.0)

    def test_get_average_price_with_window(self):
        """Test average price with window limit."""
        tracker = PriceTracker()
        for i in range(10):
            tracker.record_price("food", float(i))

        avg = tracker.get_average_price("food", window=3)
        # Last 3: 7, 8, 9 -> avg = 8
        assert avg == pytest.approx(8.0)

    def test_get_price_trend_increasing(self):
        """Test price trend detection for increasing prices."""
        tracker = PriceTracker()
        for i in range(5):
            tracker.record_price("food", float(i * 2))  # 0, 2, 4, 6, 8

        trend = tracker.get_price_trend("food")
        assert trend is not None
        assert trend > 0  # Positive slope = increasing

    def test_get_price_trend_decreasing(self):
        """Test price trend detection for decreasing prices."""
        tracker = PriceTracker()
        for i in range(5):
            tracker.record_price("food", float(10 - i * 2))  # 10, 8, 6, 4, 2

        trend = tracker.get_price_trend("food")
        assert trend is not None
        assert trend < 0  # Negative slope = decreasing

    def test_get_price_history(self):
        """Test retrieving price history."""
        tracker = PriceTracker()
        for i in range(5):
            tracker.record_price("food", float(i))

        history = tracker.get_price_history("food")
        assert len(history) == 5
        assert all(isinstance(p, PricePoint) for p in history)

    def test_get_price_history_with_limit(self):
        """Test retrieving limited price history."""
        tracker = PriceTracker()
        for i in range(10):
            tracker.record_price("food", float(i))

        history = tracker.get_price_history("food", limit=3)
        assert len(history) == 3

    def test_get_volatility(self):
        """Test volatility calculation."""
        tracker = PriceTracker()
        # Prices: 10, 20, 10, 20, 10 -> high volatility
        for price in [10, 20, 10, 20, 10]:
            tracker.record_price("food", float(price))

        volatility = tracker.get_volatility("food")
        assert volatility is not None
        assert volatility > 0

    def test_clear_history_specific(self):
        """Test clearing specific resource history."""
        tracker = PriceTracker()
        tracker.record_price("food", 10.0)
        tracker.record_price("wood", 5.0)

        tracker.clear_history("food")

        assert tracker.get_current_price("food") is None
        assert tracker.get_current_price("wood") == 5.0

    def test_clear_history_all(self):
        """Test clearing all history."""
        tracker = PriceTracker()
        tracker.record_price("food", 10.0)
        tracker.record_price("wood", 5.0)

        tracker.clear_history()

        assert tracker.get_current_price("food") is None
        assert tracker.get_current_price("wood") is None

    def test_history_limit(self):
        """Test that history respects max limit."""
        tracker = PriceTracker(max_history=5)

        for i in range(10):
            tracker.record_price("food", float(i))

        history = tracker.get_price_history("food")
        assert len(history) == 5
        # Should keep most recent
        assert history[-1].price == 9.0
