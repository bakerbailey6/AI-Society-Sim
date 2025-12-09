"""Tests for CooperativePolicy.

This module tests the cooperative decision policy including:
- Ally detection
- Resource sharing logic
- Alliance formation decisions
"""
import pytest
import sys
import os

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src')
sys.path.insert(0, src_path)

from policies.cooperative import (
    CooperativePolicy,
    CooperativeStrategy,
    StandardCooperativeStrategy,
    CooperationPriority,
    AllyNeed,
)


class MockAgent:
    """Mock agent for policy testing."""

    def __init__(self, agent_id: str, health: float = 100.0,
                 energy: float = 100.0, sociability: int = 50):
        self.agent_id = agent_id
        self.name = f"Agent_{agent_id}"
        self.health = health
        self.max_health = 100.0
        self.energy = energy
        self.max_energy = 100.0

        class MockTraits:
            pass
        self.traits = MockTraits()
        self.traits.sociability = sociability


class TestCooperationPriority:
    """Tests for CooperationPriority enum."""

    def test_priorities_exist(self):
        """Test all priorities exist."""
        assert CooperationPriority.HELP_ALLY is not None
        assert CooperationPriority.SHARE_RESOURCES is not None
        assert CooperationPriority.COORDINATE is not None
        assert CooperationPriority.BUILD_ALLIANCE is not None
        assert CooperationPriority.COLLECTIVE_GATHER is not None
        assert CooperationPriority.DEFEND_ALLY is not None


class TestAllyNeed:
    """Tests for AllyNeed dataclass."""

    def test_creation(self):
        """Test AllyNeed creation."""
        need = AllyNeed(
            agent_id="ally1",
            need_type="health",
            severity=0.8,
            resource_type="food"
        )

        assert need.agent_id == "ally1"
        assert need.need_type == "health"
        assert need.severity == 0.8
        assert need.resource_type == "food"

    def test_optional_resource_type(self):
        """Test resource_type is optional."""
        need = AllyNeed(
            agent_id="ally1",
            need_type="energy",
            severity=0.5
        )

        assert need.resource_type is None


class TestStandardCooperativeStrategy:
    """Tests for StandardCooperativeStrategy."""

    def test_evaluate_ally_need_low_health(self):
        """Test detecting low health ally."""
        strategy = StandardCooperativeStrategy()
        ally = MockAgent("ally1", health=20.0)
        agent = MockAgent("self")

        need = strategy.evaluate_ally_need(ally, agent)

        assert need is not None
        assert need.need_type == "health"
        assert need.severity > 0

    def test_evaluate_ally_need_low_energy(self):
        """Test detecting low energy ally."""
        strategy = StandardCooperativeStrategy()
        ally = MockAgent("ally1", health=100.0, energy=15.0)
        agent = MockAgent("self")

        need = strategy.evaluate_ally_need(ally, agent)

        assert need is not None
        assert need.need_type == "energy"

    def test_evaluate_ally_need_healthy(self):
        """Test healthy ally has no need."""
        strategy = StandardCooperativeStrategy()
        ally = MockAgent("ally1", health=80.0, energy=80.0)
        agent = MockAgent("self")

        need = strategy.evaluate_ally_need(ally, agent)

        assert need is None

    def test_should_share_resources(self):
        """Test resource sharing decision."""
        strategy = StandardCooperativeStrategy()
        agent = MockAgent("self")
        ally = MockAgent("ally1")

        should_share = strategy.should_share_resources(agent, ally, "food")

        # Default implementation returns True
        assert should_share is True


class TestCooperativePolicy:
    """Tests for CooperativePolicy."""

    def test_initialization(self):
        """Test policy initialization."""
        policy = CooperativePolicy()

        assert policy.name == "Cooperative"

    def test_initialization_custom_strategy(self):
        """Test initialization with custom strategy."""
        strategy = StandardCooperativeStrategy()
        policy = CooperativePolicy(cooperation_strategy=strategy)

        assert policy._cooperation_strategy is strategy

    def test_find_struggling_ally(self):
        """Test finding struggling ally."""
        policy = CooperativePolicy()

        low_health_ally = MockAgent("ally1", health=20.0)
        healthy_ally = MockAgent("ally2", health=80.0)

        sensor_data = {
            'nearby_agents': [
                ("ally1", low_health_ally, 1.0),
                ("ally2", healthy_ally, 2.0),
            ],
            'allies': ["ally1", "ally2"]
        }

        struggling = policy._find_struggling_ally(sensor_data, MockAgent("self"))

        assert struggling is not None
        assert struggling.agent_id == "ally1"

    def test_find_struggling_ally_none_struggling(self):
        """Test no struggling ally found."""
        policy = CooperativePolicy()

        healthy_ally = MockAgent("ally1", health=80.0)

        sensor_data = {
            'nearby_agents': [("ally1", healthy_ally, 1.0)],
            'allies': ["ally1"]
        }

        struggling = policy._find_struggling_ally(sensor_data, MockAgent("self"))

        assert struggling is None

    def test_should_form_alliance_high_sociability(self):
        """Test alliance formation with high sociability."""
        policy = CooperativePolicy()

        agent = MockAgent("self", sociability=80)

        sensor_data = {
            'nearby_agents': [
                ("other1", MockAgent("other1"), 1.0),
                ("other2", MockAgent("other2"), 2.0),
            ],
            'faction': None
        }

        should_form = policy._should_form_alliance(sensor_data, agent)

        assert should_form is True

    def test_should_not_form_alliance_low_sociability(self):
        """Test no alliance with low sociability."""
        policy = CooperativePolicy()

        agent = MockAgent("self", sociability=20)

        sensor_data = {
            'nearby_agents': [],
            'faction': None
        }

        should_form = policy._should_form_alliance(sensor_data, agent)

        assert should_form is False

    def test_should_not_form_alliance_already_in_faction(self):
        """Test no alliance when already in faction."""
        policy = CooperativePolicy()

        agent = MockAgent("self", sociability=80)

        sensor_data = {
            'nearby_agents': [
                ("other1", MockAgent("other1"), 1.0),
                ("other2", MockAgent("other2"), 2.0),
            ],
            'faction': "existing_faction"  # Already in faction
        }

        should_form = policy._should_form_alliance(sensor_data, agent)

        assert should_form is False

    def test_can_help_ally_enough_energy(self):
        """Test can help when enough energy."""
        policy = CooperativePolicy()

        agent = MockAgent("self", energy=50.0)
        ally = MockAgent("ally1", health=20.0)

        can_help = policy._can_help_ally(agent, ally)

        assert can_help is True

    def test_cannot_help_ally_low_energy(self):
        """Test cannot help when low energy."""
        policy = CooperativePolicy()

        agent = MockAgent("self", energy=1.0)
        ally = MockAgent("ally1", health=20.0)

        can_help = policy._can_help_ally(agent, ally)

        assert can_help is False

    def test_repr(self):
        """Test string representation."""
        policy = CooperativePolicy()

        repr_str = repr(policy)

        assert "CooperativePolicy" in repr_str
