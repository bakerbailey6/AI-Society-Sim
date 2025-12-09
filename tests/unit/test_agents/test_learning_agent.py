"""Tests for LearningAgent.

This module tests the Q-learning agent including:
- Q-table management
- State encoding
- Reward calculation
- Learning parameter validation
"""
import pytest
import sys
import os

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src')
sys.path.insert(0, src_path)

from world.position import Position
from agents.traits import AgentTraits
from agents.learning_agent import (
    LearningAgent,
    StateEncoder,
    RewardCalculator,
    EncodedState,
    StateLevel,
)


@pytest.fixture
def default_traits():
    """Provide default agent traits."""
    return AgentTraits(
        strength=50,
        intelligence=50,
        sociability=50,
        aggression=50,
        curiosity=50
    )


@pytest.fixture
def learning_agent(default_traits):
    """Provide a learning agent."""
    return LearningAgent(
        name="Learner",
        position=Position(0, 0),
        traits=default_traits,
        learning_rate=0.1,
        discount_factor=0.95,
        epsilon=0.2
    )


class TestLearningAgentInitialization:
    """Tests for LearningAgent initialization."""

    def test_default_initialization(self, default_traits):
        """Test default initialization."""
        agent = LearningAgent(
            name="Test",
            position=Position(0, 0),
            traits=default_traits
        )

        assert agent.name == "Test"
        assert agent.learning_rate == 0.1
        assert agent.discount_factor == 0.95
        assert agent.epsilon == 0.1

    def test_custom_parameters(self, default_traits):
        """Test custom learning parameters."""
        agent = LearningAgent(
            name="Test",
            position=Position(0, 0),
            traits=default_traits,
            learning_rate=0.2,
            discount_factor=0.9,
            epsilon=0.3
        )

        assert agent.learning_rate == 0.2
        assert agent.discount_factor == 0.9
        assert agent.epsilon == 0.3

    def test_invalid_learning_rate(self, default_traits):
        """Test invalid learning rate raises error."""
        with pytest.raises(ValueError):
            LearningAgent(
                name="Test",
                position=Position(0, 0),
                traits=default_traits,
                learning_rate=1.5  # Invalid: > 1
            )

    def test_invalid_discount_factor(self, default_traits):
        """Test invalid discount factor raises error."""
        with pytest.raises(ValueError):
            LearningAgent(
                name="Test",
                position=Position(0, 0),
                traits=default_traits,
                discount_factor=-0.1  # Invalid: < 0
            )

    def test_invalid_epsilon(self, default_traits):
        """Test invalid epsilon raises error."""
        with pytest.raises(ValueError):
            LearningAgent(
                name="Test",
                position=Position(0, 0),
                traits=default_traits,
                epsilon=2.0  # Invalid: > 1
            )


class TestQTableManagement:
    """Tests for Q-table operations."""

    def test_empty_q_table(self, learning_agent):
        """Test Q-table starts empty."""
        assert learning_agent.get_q_table_size() == 0

    def test_get_q_value_default(self, learning_agent):
        """Test get_q_value returns 0 for unknown state-action."""
        value = learning_agent.get_q_value("unknown_state", "unknown_action")
        assert value == 0.0

    def test_set_and_get_q_value(self, learning_agent):
        """Test setting and getting Q-value."""
        learning_agent.set_q_value("state1", "action1", 0.5)

        value = learning_agent.get_q_value("state1", "action1")
        assert value == 0.5

    def test_q_table_size(self, learning_agent):
        """Test Q-table size increases."""
        learning_agent.set_q_value("s1", "a1", 0.5)
        learning_agent.set_q_value("s1", "a2", 0.3)
        learning_agent.set_q_value("s2", "a1", 0.7)

        assert learning_agent.get_q_table_size() == 3

    def test_clear_q_table(self, learning_agent):
        """Test clearing Q-table."""
        learning_agent.set_q_value("s1", "a1", 0.5)
        learning_agent.set_q_value("s2", "a2", 0.3)

        learning_agent.clear_q_table()

        assert learning_agent.get_q_table_size() == 0

    def test_update_existing_q_value(self, learning_agent):
        """Test updating existing Q-value."""
        learning_agent.set_q_value("s1", "a1", 0.5)
        learning_agent.set_q_value("s1", "a1", 0.8)

        value = learning_agent.get_q_value("s1", "a1")
        assert value == 0.8
        assert learning_agent.get_q_table_size() == 1


class TestEpsilonDecay:
    """Tests for epsilon decay functionality."""

    def test_decay_epsilon(self, learning_agent):
        """Test epsilon decay."""
        learning_agent.epsilon = 0.5

        learning_agent.decay_epsilon(0.9)

        assert learning_agent.epsilon == pytest.approx(0.45)

    def test_epsilon_minimum(self, learning_agent):
        """Test epsilon doesn't go below minimum."""
        learning_agent.epsilon = 0.02

        learning_agent.decay_epsilon(0.1)

        assert learning_agent.epsilon == 0.01  # Minimum

    def test_multiple_decays(self, learning_agent):
        """Test multiple decay operations."""
        learning_agent.epsilon = 1.0

        for _ in range(10):
            learning_agent.decay_epsilon(0.9)

        # Should be around 0.35 (1.0 * 0.9^10)
        assert learning_agent.epsilon < 0.4
        assert learning_agent.epsilon > 0.3


class TestStateEncoder:
    """Tests for StateEncoder."""

    def test_discretize_critical(self):
        """Test critical level discretization."""
        level = StateEncoder._discretize_level(10.0)
        assert level == StateLevel.CRITICAL

    def test_discretize_low(self):
        """Test low level discretization."""
        level = StateEncoder._discretize_level(25.0)
        assert level == StateLevel.LOW

    def test_discretize_medium(self):
        """Test medium level discretization."""
        level = StateEncoder._discretize_level(50.0)
        assert level == StateLevel.MEDIUM

    def test_discretize_high(self):
        """Test high level discretization."""
        level = StateEncoder._discretize_level(80.0)
        assert level == StateLevel.HIGH

    def test_get_available_actions_basic(self):
        """Test basic available actions."""
        sensor_data = {
            'nearby_resources': [],
            'nearby_agents': [],
            'allies': [],
            'enemies': []
        }

        actions = StateEncoder.get_available_actions(sensor_data, None)

        assert "rest" in actions
        assert "move_north" in actions
        assert "move_south" in actions

    def test_get_available_actions_with_resources(self):
        """Test actions include gather when resources nearby."""
        sensor_data = {
            'nearby_resources': [("food", 10, (1, 0))],
            'nearby_agents': [],
            'allies': [],
            'enemies': []
        }

        actions = StateEncoder.get_available_actions(sensor_data, None)

        assert "gather" in actions

    def test_get_available_actions_with_allies(self):
        """Test actions include trade when allies nearby."""
        sensor_data = {
            'nearby_resources': [],
            'nearby_agents': [("ally1", None, 1.0)],
            'allies': ["ally1"],
            'enemies': []
        }

        actions = StateEncoder.get_available_actions(sensor_data, None)

        assert "trade" in actions

    def test_get_available_actions_with_enemies(self):
        """Test actions include attack when enemies nearby."""
        sensor_data = {
            'nearby_resources': [],
            'nearby_agents': [("enemy1", None, 1.0)],
            'allies': [],
            'enemies': ["enemy1"]
        }

        actions = StateEncoder.get_available_actions(sensor_data, None)

        assert "attack" in actions


class TestEncodedState:
    """Tests for EncodedState."""

    def test_hashable(self):
        """Test EncodedState is hashable."""
        state = EncodedState(
            energy_level=StateLevel.HIGH,
            health_level=StateLevel.HIGH,
            has_resources_nearby=True,
            has_enemies_nearby=False,
            has_allies_nearby=True,
            terrain_type="plains"
        )

        # Should not raise
        hash_value = hash(state)
        assert isinstance(hash_value, int)

    def test_equal_states_same_hash(self):
        """Test equal states have same hash."""
        state1 = EncodedState(
            energy_level=StateLevel.HIGH,
            health_level=StateLevel.HIGH,
            has_resources_nearby=True,
            has_enemies_nearby=False,
            has_allies_nearby=True,
            terrain_type="plains"
        )

        state2 = EncodedState(
            energy_level=StateLevel.HIGH,
            health_level=StateLevel.HIGH,
            has_resources_nearby=True,
            has_enemies_nearby=False,
            has_allies_nearby=True,
            terrain_type="plains"
        )

        assert hash(state1) == hash(state2)

    def test_different_states_different_hash(self):
        """Test different states have different hashes."""
        state1 = EncodedState(
            energy_level=StateLevel.HIGH,
            health_level=StateLevel.HIGH,
            has_resources_nearby=True,
            has_enemies_nearby=False,
            has_allies_nearby=True,
            terrain_type="plains"
        )

        state2 = EncodedState(
            energy_level=StateLevel.LOW,  # Different
            health_level=StateLevel.HIGH,
            has_resources_nearby=True,
            has_enemies_nearby=False,
            has_allies_nearby=True,
            terrain_type="plains"
        )

        assert hash(state1) != hash(state2)


class TestRewardCalculator:
    """Tests for RewardCalculator."""

    def test_death_penalty(self):
        """Test death penalty is applied."""
        pre = {"health": 50, "energy": 50, "resources": 0}
        post = {"health": 0, "energy": 50, "resources": 0}

        reward = RewardCalculator.calculate_reward(pre, post, "move")

        assert reward == RewardCalculator.DEATH_PENALTY

    def test_health_increase_reward(self):
        """Test health increase gives reward."""
        pre = {"health": 50, "energy": 50, "resources": 0}
        post = {"health": 60, "energy": 50, "resources": 0}

        reward = RewardCalculator.calculate_reward(pre, post, "rest")

        assert reward == RewardCalculator.HEALTH_INCREASE_REWARD

    def test_damage_penalty(self):
        """Test damage gives penalty."""
        pre = {"health": 50, "energy": 50, "resources": 0}
        post = {"health": 40, "energy": 50, "resources": 0}

        reward = RewardCalculator.calculate_reward(pre, post, "attack")

        assert reward == RewardCalculator.DAMAGE_PENALTY

    def test_energy_increase_reward(self):
        """Test energy increase gives reward."""
        pre = {"health": 100, "energy": 50, "resources": 0}
        post = {"health": 100, "energy": 60, "resources": 0}

        reward = RewardCalculator.calculate_reward(pre, post, "gather")

        assert reward == RewardCalculator.ENERGY_INCREASE_REWARD

    def test_gather_reward(self):
        """Test gathering gives reward."""
        pre = {"health": 100, "energy": 100, "resources": 0}
        post = {"health": 100, "energy": 100, "resources": 10}

        reward = RewardCalculator.calculate_reward(pre, post, "gather")

        assert reward == RewardCalculator.GATHER_REWARD

    def test_move_cost(self):
        """Test moving has cost."""
        pre = {"health": 100, "energy": 100, "resources": 0}
        post = {"health": 100, "energy": 100, "resources": 0}

        reward = RewardCalculator.calculate_reward(pre, post, "move")

        assert reward == RewardCalculator.MOVE_COST


class TestLearningAgentRepr:
    """Tests for string representation."""

    def test_repr(self, learning_agent):
        """Test repr includes key information."""
        repr_str = repr(learning_agent)

        assert "LearningAgent" in repr_str
        assert "Learner" in repr_str
