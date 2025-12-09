"""Tests for AggressivePolicy.

This module tests the aggressive decision policy including:
- Target selection
- Combat readiness
- Territory defense
"""
import pytest
import sys
import os

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src')
sys.path.insert(0, src_path)

from policies.aggressive import (
    AggressivePolicy,
    CombatAssessmentStrategy,
    StandardCombatAssessment,
    AggressionPriority,
    ThreatAssessment,
)
from world.position import Position


class MockAgent:
    """Mock agent for policy testing."""

    def __init__(self, agent_id: str, health: float = 100.0,
                 energy: float = 100.0, strength: int = 50,
                 position: Position = None):
        self.agent_id = agent_id
        self.name = f"Agent_{agent_id}"
        self.health = health
        self.max_health = 100.0
        self.energy = energy
        self.max_energy = 100.0
        self.position = position or Position(0, 0)

        class MockTraits:
            pass
        self.traits = MockTraits()
        self.traits.strength = strength


class TestAggressionPriority:
    """Tests for AggressionPriority enum."""

    def test_priorities_exist(self):
        """Test all priorities exist."""
        assert AggressionPriority.ATTACK_VULNERABLE is not None
        assert AggressionPriority.DEFEND_TERRITORY is not None
        assert AggressionPriority.DENY_RESOURCES is not None
        assert AggressionPriority.EXPAND is not None
        assert AggressionPriority.INTIMIDATE is not None
        assert AggressionPriority.RETREAT is not None


class TestThreatAssessment:
    """Tests for ThreatAssessment dataclass."""

    def test_creation(self):
        """Test ThreatAssessment creation."""
        assessment = ThreatAssessment(
            agent_id="enemy1",
            threat_level=0.7,
            vulnerability=0.3,
            distance=5.0,
            is_enemy=True
        )

        assert assessment.agent_id == "enemy1"
        assert assessment.threat_level == 0.7
        assert assessment.vulnerability == 0.3
        assert assessment.distance == 5.0
        assert assessment.is_enemy is True


class TestStandardCombatAssessment:
    """Tests for StandardCombatAssessment."""

    def test_assess_target(self):
        """Test target assessment."""
        strategy = StandardCombatAssessment()
        attacker = MockAgent("attacker", strength=60)
        target = MockAgent("target", strength=40, health=50.0)

        assessment = strategy.assess_target(attacker, target)

        assert isinstance(assessment, ThreatAssessment)
        assert assessment.agent_id == "target"
        assert assessment.vulnerability > 0  # Low health = vulnerable

    def test_calculate_win_probability_stronger(self):
        """Test win probability when stronger."""
        strategy = StandardCombatAssessment()
        strong = MockAgent("strong", strength=80, health=100.0)
        weak = MockAgent("weak", strength=30, health=100.0)

        win_prob = strategy.calculate_win_probability(strong, weak)

        assert win_prob > 0.5  # Strong should be favored

    def test_calculate_win_probability_equal(self):
        """Test win probability when equal."""
        strategy = StandardCombatAssessment()
        agent1 = MockAgent("agent1", strength=50, health=100.0)
        agent2 = MockAgent("agent2", strength=50, health=100.0)

        win_prob = strategy.calculate_win_probability(agent1, agent2)

        assert win_prob == pytest.approx(0.5)

    def test_calculate_win_probability_health_matters(self):
        """Test health affects win probability."""
        strategy = StandardCombatAssessment()
        healthy = MockAgent("healthy", strength=50, health=100.0)
        injured = MockAgent("injured", strength=50, health=30.0)

        healthy_prob = strategy.calculate_win_probability(healthy, injured)
        injured_prob = strategy.calculate_win_probability(injured, healthy)

        assert healthy_prob > injured_prob


class TestAggressivePolicy:
    """Tests for AggressivePolicy."""

    def test_initialization(self):
        """Test policy initialization."""
        policy = AggressivePolicy()

        assert policy.name == "Aggressive"

    def test_initialization_custom_win_prob(self):
        """Test custom win probability threshold."""
        policy = AggressivePolicy(min_win_probability=0.7)

        assert policy._min_win_probability == 0.7

    def test_is_combat_ready_healthy(self):
        """Test combat ready when healthy."""
        policy = AggressivePolicy()
        agent = MockAgent("self", health=80.0, energy=80.0)

        is_ready = policy._is_combat_ready(agent)

        assert is_ready is True

    def test_is_combat_ready_low_health(self):
        """Test not combat ready with low health."""
        policy = AggressivePolicy()
        agent = MockAgent("self", health=20.0, energy=80.0)

        is_ready = policy._is_combat_ready(agent)

        assert is_ready is False

    def test_is_combat_ready_low_energy(self):
        """Test not combat ready with low energy."""
        policy = AggressivePolicy()
        agent = MockAgent("self", health=80.0, energy=10.0)

        is_ready = policy._is_combat_ready(agent)

        assert is_ready is False

    def test_find_vulnerable_target(self):
        """Test finding vulnerable enemy."""
        policy = AggressivePolicy(min_win_probability=0.6)

        strong_agent = MockAgent("self", strength=80, health=100.0)
        weak_enemy = MockAgent("enemy1", strength=30, health=50.0)
        strong_enemy = MockAgent("enemy2", strength=90, health=100.0)

        sensor_data = {
            'nearby_agents': [
                ("enemy1", weak_enemy, 1.0),
                ("enemy2", strong_enemy, 2.0),
            ],
            'enemies': ["enemy1", "enemy2"]
        }

        target = policy._find_vulnerable_target(sensor_data, strong_agent)

        # Should find weak enemy as target
        assert target is not None
        assert target.agent_id == "enemy1"

    def test_find_vulnerable_target_none_vulnerable(self):
        """Test no target when all enemies are strong."""
        policy = AggressivePolicy(min_win_probability=0.8)

        weak_agent = MockAgent("self", strength=30, health=100.0)
        strong_enemy = MockAgent("enemy1", strength=90, health=100.0)

        sensor_data = {
            'nearby_agents': [("enemy1", strong_enemy, 1.0)],
            'enemies': ["enemy1"]
        }

        target = policy._find_vulnerable_target(sensor_data, weak_agent)

        assert target is None

    def test_find_intruder_in_territory(self):
        """Test finding intruder in territory."""
        policy = AggressivePolicy()

        agent = MockAgent("self", position=Position(5, 5))
        intruder = MockAgent("enemy1", position=Position(5, 5))

        sensor_data = {
            'nearby_agents': [("enemy1", intruder, 0.0)],
            'enemies': ["enemy1"],
            'territory': {Position(5, 5), Position(5, 6)}
        }

        found = policy._find_intruder(sensor_data, agent)

        assert found is not None
        assert found.agent_id == "enemy1"

    def test_find_intruder_no_territory(self):
        """Test no intruder without territory."""
        policy = AggressivePolicy()

        agent = MockAgent("self")
        enemy = MockAgent("enemy1")

        sensor_data = {
            'nearby_agents': [("enemy1", enemy, 1.0)],
            'enemies': ["enemy1"],
            'territory': set()
        }

        found = policy._find_intruder(sensor_data, agent)

        assert found is None

    def test_find_contested_resource(self):
        """Test finding contested resource."""
        policy = AggressivePolicy()

        agent = MockAgent("self", position=Position(0, 0))
        enemy = MockAgent("enemy1", position=Position(2, 0))

        sensor_data = {
            'nearby_resources': [("food", 10, Position(3, 0))],
            'nearby_agents': [("enemy1", enemy, 2.0)],
            'enemies': ["enemy1"]
        }

        contested = policy._find_contested_resource(sensor_data, agent)

        # Enemy is closer to resource
        assert contested is not None

    def test_repr(self):
        """Test string representation."""
        policy = AggressivePolicy()

        repr_str = repr(policy)

        assert "AggressivePolicy" in repr_str
