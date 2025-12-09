"""Tests for AttackAction.

This module tests the attack action including:
- Combat calculations
- Damage formulas
- Combat outcomes
"""
import pytest
import sys
import os

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src')
sys.path.insert(0, src_path)

from actions.attack import (
    AttackAction,
    CombatStrategy,
    StandardCombatStrategy,
    CombatResult,
    CombatOutcome,
)


class MockAgent:
    """Mock agent for combat testing."""

    def __init__(self, agent_id: str, strength: int = 50, health: float = 100.0):
        self.agent_id = agent_id
        self.health = health
        self.max_health = 100.0

        class MockTraits:
            pass
        self.traits = MockTraits()
        self.traits.strength = strength


class TestStandardCombatStrategy:
    """Tests for StandardCombatStrategy."""

    def test_calculate_damage(self):
        """Test damage calculation."""
        strategy = StandardCombatStrategy()
        attacker = MockAgent("attacker", strength=60)
        defender = MockAgent("defender", strength=40)

        damage = strategy.calculate_damage(attacker, defender)

        assert damage > 0
        assert isinstance(damage, float)

    def test_stronger_attacker_more_damage(self):
        """Test stronger attacker does more damage."""
        strategy = StandardCombatStrategy()
        defender = MockAgent("defender", strength=50)

        strong_attacker = MockAgent("strong", strength=80)
        weak_attacker = MockAgent("weak", strength=30)

        strong_damage = strategy.calculate_damage(strong_attacker, defender)
        weak_damage = strategy.calculate_damage(weak_attacker, defender)

        assert strong_damage > weak_damage

    def test_defense_reduces_damage(self):
        """Test higher defense reduces damage taken."""
        strategy = StandardCombatStrategy()
        attacker = MockAgent("attacker", strength=50)

        low_def = MockAgent("low_def", strength=20)
        high_def = MockAgent("high_def", strength=80)

        damage_to_low = strategy.calculate_damage(attacker, low_def)
        damage_to_high = strategy.calculate_damage(attacker, high_def)

        assert damage_to_low > damage_to_high

    def test_calculate_hit_chance(self):
        """Test hit chance calculation."""
        strategy = StandardCombatStrategy()
        attacker = MockAgent("attacker", strength=50)
        defender = MockAgent("defender", strength=50)

        hit_chance = strategy.calculate_hit_chance(attacker, defender)

        assert 0 <= hit_chance <= 1

    def test_minimum_damage(self):
        """Test minimum damage is enforced."""
        strategy = StandardCombatStrategy()
        weak_attacker = MockAgent("weak", strength=1)
        strong_defender = MockAgent("strong", strength=100)

        damage = strategy.calculate_damage(weak_attacker, strong_defender)

        assert damage >= 1.0  # Minimum damage


class TestCombatOutcome:
    """Tests for CombatOutcome dataclass."""

    def test_creation(self):
        """Test CombatOutcome creation."""
        outcome = CombatOutcome(
            result=CombatResult.HIT,
            damage_dealt=25.0,
            attacker_id="attacker1",
            defender_id="defender1",
            timestamp=100.0
        )

        assert outcome.attacker_id == "attacker1"
        assert outcome.defender_id == "defender1"
        assert outcome.damage_dealt == 25.0
        assert outcome.result == CombatResult.HIT
        assert outcome.timestamp == 100.0


class TestCombatResult:
    """Tests for CombatResult enum."""

    def test_result_values(self):
        """Test combat result enum values exist."""
        assert CombatResult.HIT is not None
        assert CombatResult.MISS is not None
        assert CombatResult.CRITICAL is not None
        assert CombatResult.BLOCKED is not None
        assert CombatResult.KILL is not None


class TestAttackAction:
    """Tests for AttackAction."""

    def test_initialization(self):
        """Test AttackAction initialization."""
        action = AttackAction(target_agent_id="target1")

        assert action.target_agent_id == "target1"

    def test_energy_cost(self):
        """Test attack energy cost."""
        action = AttackAction(target_agent_id="target1")

        assert action.energy_cost == 5.0

    def test_action_name(self):
        """Test action name is Attack."""
        action = AttackAction(target_agent_id="target1")

        assert action.name == "Attack"

    def test_calculate_damage_method(self):
        """Test action delegates to strategy."""
        action = AttackAction(target_agent_id="target1")
        attacker = MockAgent("attacker", strength=60)
        defender = MockAgent("defender", strength=40)

        damage = action.calculate_damage(attacker, defender)

        assert damage > 0

    def test_calculate_hit_chance_method(self):
        """Test action delegates hit chance to strategy."""
        action = AttackAction(target_agent_id="target1")
        attacker = MockAgent("attacker", strength=60)
        defender = MockAgent("defender", strength=40)

        hit_chance = action.calculate_hit_chance(attacker, defender)

        assert 0 <= hit_chance <= 1

    def test_repr(self):
        """Test string representation."""
        action = AttackAction(target_agent_id="target1")

        repr_str = repr(action)

        assert "AttackAction" in repr_str
        assert "target1" in repr_str

    def test_custom_combat_strategy(self):
        """Test using custom combat strategy."""
        strategy = StandardCombatStrategy()
        action = AttackAction(
            target_agent_id="target1",
            combat_strategy=strategy
        )

        assert action._combat_strategy is strategy
