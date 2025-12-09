"""Tests for FormAllianceAction.

This module tests the alliance formation action including:
- Alliance types
- Formation strategies
- Validation
"""
import pytest
import sys
import os

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src')
sys.path.insert(0, src_path)

from actions.alliance import (
    FormAllianceAction,
    AllianceType,
    AllianceFormationStrategy,
    StandardAllianceStrategy,
    AllianceProposal,
)
from world.position import Position


class MockAgent:
    """Mock agent for alliance testing."""

    def __init__(self, agent_id: str, sociability: int = 50,
                 position: Position = None):
        self.agent_id = agent_id
        self.name = f"Agent_{agent_id}"
        self.position = position or Position(0, 0)

        class MockTraits:
            pass
        self.traits = MockTraits()
        self.traits.sociability = sociability


class MockWorld:
    """Mock world for alliance testing."""
    pass


class TestAllianceType:
    """Tests for AllianceType enum."""

    def test_alliance_types_exist(self):
        """Test all alliance types exist."""
        assert AllianceType.FACTION is not None
        assert AllianceType.GROUP is not None
        assert AllianceType.TREATY is not None
        assert AllianceType.COALITION is not None


class TestAllianceProposal:
    """Tests for AllianceProposal dataclass."""

    def test_creation(self):
        """Test AllianceProposal creation."""
        proposal = AllianceProposal(
            proposer_id="agent1",
            target_ids=["agent2", "agent3"],
            alliance_name="Test Alliance",
            alliance_type=AllianceType.GROUP,
            governance=None,
            timestamp=100.0
        )

        assert proposal.proposer_id == "agent1"
        assert proposal.target_ids == ["agent2", "agent3"]
        assert proposal.alliance_name == "Test Alliance"
        assert proposal.alliance_type == AllianceType.GROUP
        assert proposal.timestamp == 100.0


class TestStandardAllianceStrategy:
    """Tests for StandardAllianceStrategy."""

    def test_can_form_alliance_high_sociability(self):
        """Test alliance can form with high sociability."""
        strategy = StandardAllianceStrategy()
        proposer = MockAgent("proposer", sociability=60, position=Position(0, 0))
        targets = [MockAgent("t1", position=Position(1, 0))]
        world = MockWorld()

        can_form = strategy.can_form_alliance(proposer, targets, world)

        assert can_form is True

    def test_cannot_form_alliance_low_sociability(self):
        """Test alliance cannot form with low sociability."""
        strategy = StandardAllianceStrategy()
        proposer = MockAgent("proposer", sociability=10, position=Position(0, 0))
        targets = [MockAgent("t1", position=Position(1, 0))]
        world = MockWorld()

        can_form = strategy.can_form_alliance(proposer, targets, world)

        assert can_form is False

    def test_cannot_form_alliance_too_far(self):
        """Test alliance cannot form when targets too far."""
        strategy = StandardAllianceStrategy()
        proposer = MockAgent("proposer", sociability=60, position=Position(0, 0))
        targets = [MockAgent("t1", position=Position(100, 100))]
        world = MockWorld()

        can_form = strategy.can_form_alliance(proposer, targets, world)

        assert can_form is False

    def test_get_required_sociability(self):
        """Test required sociability getter."""
        strategy = StandardAllianceStrategy()

        required = strategy.get_required_sociability()

        assert required == 30.0


class TestFormAllianceAction:
    """Tests for FormAllianceAction."""

    def test_initialization(self):
        """Test FormAllianceAction initialization."""
        action = FormAllianceAction(
            target_agent_ids=["agent1", "agent2"],
            alliance_name="Test Alliance"
        )

        assert action.target_agent_ids == ["agent1", "agent2"]
        assert action.alliance_name == "Test Alliance"

    def test_default_alliance_type(self):
        """Test default alliance type is GROUP."""
        action = FormAllianceAction(
            target_agent_ids=["agent1"],
            alliance_name="Test"
        )

        assert action.alliance_type == AllianceType.GROUP

    def test_custom_alliance_type(self):
        """Test custom alliance type."""
        action = FormAllianceAction(
            target_agent_ids=["agent1"],
            alliance_name="Test",
            alliance_type=AllianceType.FACTION
        )

        assert action.alliance_type == AllianceType.FACTION

    def test_energy_cost_calculation(self):
        """Test alliance formation energy cost calculation."""
        # Base 3.0 + 0.5 per member
        action_one = FormAllianceAction(
            target_agent_ids=["agent1"],
            alliance_name="Test"
        )
        action_three = FormAllianceAction(
            target_agent_ids=["agent1", "agent2", "agent3"],
            alliance_name="Test"
        )

        assert action_one.energy_cost == 3.5  # 3.0 + 0.5
        assert action_three.energy_cost == 4.5  # 3.0 + 1.5

    def test_action_name(self):
        """Test action name."""
        action = FormAllianceAction(
            target_agent_ids=["agent1"],
            alliance_name="Test"
        )

        assert action.name == "Form Alliance"

    def test_get_required_members_faction(self):
        """Test required members for faction."""
        action = FormAllianceAction(
            target_agent_ids=["agent1"],
            alliance_name="Test",
            alliance_type=AllianceType.FACTION
        )

        assert action.get_required_members() == 3

    def test_get_required_members_group(self):
        """Test required members for group."""
        action = FormAllianceAction(
            target_agent_ids=["agent1"],
            alliance_name="Test",
            alliance_type=AllianceType.GROUP
        )

        assert action.get_required_members() == 1

    def test_governance_type(self):
        """Test governance type property."""
        action = FormAllianceAction(
            target_agent_ids=["agent1"],
            alliance_name="Test",
            alliance_type=AllianceType.FACTION,
            governance_type="DEMOCRACY"
        )

        assert action.governance_type == "DEMOCRACY"

    def test_repr(self):
        """Test string representation."""
        action = FormAllianceAction(
            target_agent_ids=["agent1"],
            alliance_name="MyAlliance",
            alliance_type=AllianceType.FACTION
        )

        repr_str = repr(action)

        assert "FormAllianceAction" in repr_str
        assert "MyAlliance" in repr_str
        assert "faction" in repr_str
