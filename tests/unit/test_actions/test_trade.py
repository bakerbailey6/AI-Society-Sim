"""Tests for TradeAction.

This module tests the trade action including:
- Trade validation
- Pricing strategies
- Trade execution flow
"""
import pytest
import sys
import os

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src')
sys.path.insert(0, src_path)

from actions.trade import (
    TradeAction,
    TradePricingStrategy,
    SimplePricingStrategy,
    TradeOffer,
)


class TestTradeOffer:
    """Tests for TradeOffer dataclass."""

    def test_creation(self):
        """Test TradeOffer creation."""
        offer = TradeOffer(
            initiator_id="agent1",
            target_id="agent2",
            offered={"food": 10.0},
            requested={"wood": 5.0},
            timestamp=100.0
        )

        assert offer.initiator_id == "agent1"
        assert offer.target_id == "agent2"
        assert offer.offered["food"] == 10.0
        assert offer.requested["wood"] == 5.0
        assert offer.timestamp == 100.0


class TestSimplePricingStrategy:
    """Tests for SimplePricingStrategy."""

    def test_default_prices(self):
        """Test default resource prices."""
        strategy = SimplePricingStrategy()

        food_price = strategy.BASE_PRICES.get("food", 10.0)
        water_price = strategy.BASE_PRICES.get("water", 8.0)
        material_price = strategy.BASE_PRICES.get("material", 15.0)

        assert food_price == 10.0
        assert water_price == 8.0
        assert material_price == 15.0

    def test_calculate_value(self):
        """Test value calculation."""
        strategy = SimplePricingStrategy()

        value = strategy.calculate_value({"food": 5.0})

        assert value == 50.0  # 5 * 10.0

    def test_calculate_value_multiple_resources(self):
        """Test value calculation with multiple resources."""
        strategy = SimplePricingStrategy()

        value = strategy.calculate_value({"food": 2.0, "water": 4.0})

        # (2 * 10) + (4 * 8) = 52
        assert value == 52.0

    def test_is_fair_trade_equal(self):
        """Test fair trade detection for equal values."""
        strategy = SimplePricingStrategy()

        # 50 vs 50 - equal values
        is_fair = strategy.is_fair_trade(50.0, 50.0)

        assert is_fair is True

    def test_is_fair_trade_within_tolerance(self):
        """Test fair trade within tolerance."""
        strategy = SimplePricingStrategy()

        # 50 vs 45 - within 30% tolerance
        is_fair = strategy.is_fair_trade(50.0, 45.0)

        assert is_fair is True

    def test_is_fair_trade_unfair(self):
        """Test unfair trade detection."""
        strategy = SimplePricingStrategy()

        # 50 vs 20 - way outside tolerance
        is_fair = strategy.is_fair_trade(50.0, 20.0)

        assert is_fair is False

    def test_is_fair_trade_gift(self):
        """Test gift is always fair."""
        strategy = SimplePricingStrategy()

        # Offering something for nothing
        is_fair = strategy.is_fair_trade(50.0, 0.0)

        assert is_fair is True


class TestTradeAction:
    """Tests for TradeAction."""

    def test_initialization(self):
        """Test TradeAction initialization."""
        action = TradeAction(
            target_agent_id="target1",
            offered_resources={"food": 10.0},
            requested_resources={"wood": 5.0}
        )

        assert action.target_agent_id == "target1"
        assert action.offered["food"] == 10.0
        assert action.requested["wood"] == 5.0

    def test_energy_cost(self):
        """Test trade energy cost."""
        action = TradeAction(
            target_agent_id="target1",
            offered_resources={"food": 10.0},
            requested_resources={}
        )

        assert action.energy_cost == 1.5

    def test_action_name(self):
        """Test action name is Trade."""
        action = TradeAction(
            target_agent_id="target1",
            offered_resources={},
            requested_resources={}
        )

        assert action.name == "Trade"

    def test_calculate_trade_value(self):
        """Test trade value calculation."""
        action = TradeAction(
            target_agent_id="target1",
            offered_resources={"food": 5.0},  # value = 50
            requested_resources={"water": 4.0}  # value = 32
        )

        offered_value, requested_value = action.calculate_trade_value()

        assert offered_value == 50.0
        assert requested_value == 32.0

    def test_is_fair_trade(self):
        """Test fair trade check."""
        action = TradeAction(
            target_agent_id="target1",
            offered_resources={"food": 5.0},  # value = 50
            requested_resources={"food": 5.0}  # value = 50
        )

        assert action.is_fair_trade() is True

    def test_is_unfair_trade(self):
        """Test unfair trade check."""
        action = TradeAction(
            target_agent_id="target1",
            offered_resources={"food": 1.0},  # value = 10
            requested_resources={"food": 10.0}  # value = 100
        )

        assert action.is_fair_trade() is False

    def test_repr(self):
        """Test string representation."""
        action = TradeAction(
            target_agent_id="target1",
            offered_resources={"food": 10.0},
            requested_resources={}
        )

        repr_str = repr(action)

        assert "TradeAction" in repr_str
        assert "target1" in repr_str
