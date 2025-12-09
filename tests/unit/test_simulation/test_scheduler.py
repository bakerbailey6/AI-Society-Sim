"""Tests for simulation schedulers.

This module tests the scheduling strategies including:
- SequentialScheduler
- RandomScheduler
- PriorityScheduler
- RoundRobinScheduler
"""
import pytest
import sys
import os

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src')
sys.path.insert(0, src_path)

from simulation.scheduler import (
    SchedulingStrategy,
    SequentialScheduler,
    RandomScheduler,
    PriorityScheduler,
    RoundRobinScheduler,
    AdaptiveScheduler,
    PriorityLevel,
)


class MockAgent:
    """Mock agent for scheduler testing."""

    def __init__(self, agent_id: str, health: float = 100.0, max_health: float = 100.0,
                 energy: float = 100.0, max_energy: float = 100.0):
        self.agent_id = agent_id
        self.health = health
        self.max_health = max_health
        self.energy = energy
        self.max_energy = max_energy


class TestSequentialScheduler:
    """Tests for SequentialScheduler."""

    def test_sequential_order(self):
        """Test agents returned in list order."""
        scheduler = SequentialScheduler()
        agents = [MockAgent(f"agent{i}") for i in range(5)]

        result = list(scheduler.get_update_order(agents, None))

        assert len(result) == 5
        for i, agent in enumerate(result):
            assert agent.agent_id == f"agent{i}"

    def test_reverse_order(self):
        """Test agents returned in reverse order."""
        scheduler = SequentialScheduler(reverse=True)
        agents = [MockAgent(f"agent{i}") for i in range(5)]

        result = list(scheduler.get_update_order(agents, None))

        assert result[0].agent_id == "agent4"
        assert result[-1].agent_id == "agent0"

    def test_empty_list(self):
        """Test handling empty agent list."""
        scheduler = SequentialScheduler()
        result = list(scheduler.get_update_order([], None))
        assert result == []

    def test_get_name(self):
        """Test scheduler name."""
        scheduler = SequentialScheduler()
        assert "SequentialScheduler" in scheduler.get_name()


class TestRandomScheduler:
    """Tests for RandomScheduler."""

    def test_all_agents_included(self):
        """Test all agents are in result."""
        scheduler = RandomScheduler(seed=42)
        agents = [MockAgent(f"agent{i}") for i in range(5)]

        result = list(scheduler.get_update_order(agents, None))

        assert len(result) == 5
        agent_ids = {a.agent_id for a in result}
        assert agent_ids == {f"agent{i}" for i in range(5)}

    def test_reproducible_with_seed(self):
        """Test same seed gives same order."""
        agents = [MockAgent(f"agent{i}") for i in range(5)]

        scheduler1 = RandomScheduler(seed=42)
        result1 = list(scheduler1.get_update_order(agents, None))

        scheduler2 = RandomScheduler(seed=42)
        result2 = list(scheduler2.get_update_order(agents, None))

        for a1, a2 in zip(result1, result2):
            assert a1.agent_id == a2.agent_id

    def test_different_seeds_different_order(self):
        """Test different seeds give different orders."""
        agents = [MockAgent(f"agent{i}") for i in range(10)]

        scheduler1 = RandomScheduler(seed=42)
        result1 = [a.agent_id for a in scheduler1.get_update_order(agents, None)]

        scheduler2 = RandomScheduler(seed=99)
        result2 = [a.agent_id for a in scheduler2.get_update_order(agents, None)]

        # Very unlikely to be the same with different seeds
        assert result1 != result2

    def test_get_name(self):
        """Test scheduler name."""
        scheduler = RandomScheduler(seed=42)
        assert "RandomScheduler" in scheduler.get_name()
        assert "42" in scheduler.get_name()


class TestPriorityScheduler:
    """Tests for PriorityScheduler."""

    def test_critical_agents_first(self):
        """Test critical (low health) agents updated first."""
        scheduler = PriorityScheduler(shuffle_within_priority=False)

        agents = [
            MockAgent("healthy", health=90.0),
            MockAgent("critical", health=5.0),
            MockAgent("low", health=25.0),
        ]

        result = list(scheduler.get_update_order(agents, None))

        # Critical should be first
        assert result[0].agent_id == "critical"

    def test_priority_ordering(self):
        """Test agents ordered by priority."""
        scheduler = PriorityScheduler(shuffle_within_priority=False)

        agents = [
            MockAgent("high", health=90.0),
            MockAgent("critical", health=5.0),
            MockAgent("medium", health=50.0),
            MockAgent("low", health=25.0),
        ]

        result = list(scheduler.get_update_order(agents, None))

        # Critical (health < 10%) should be first
        assert result[0].agent_id == "critical"
        # Low (health < 30%) should be second
        assert result[1].agent_id == "low"

    def test_custom_priority_function(self):
        """Test custom priority function."""
        def custom_priority(agent, world):
            if agent.agent_id == "priority":
                return PriorityLevel.CRITICAL
            return PriorityLevel.NORMAL

        scheduler = PriorityScheduler(priority_function=custom_priority)

        agents = [
            MockAgent("normal1"),
            MockAgent("priority"),
            MockAgent("normal2"),
        ]

        result = list(scheduler.get_update_order(agents, None))
        assert result[0].agent_id == "priority"

    def test_get_name(self):
        """Test scheduler name."""
        scheduler = PriorityScheduler()
        assert "PriorityScheduler" in scheduler.get_name()


class TestRoundRobinScheduler:
    """Tests for RoundRobinScheduler."""

    def test_all_agents_updated(self):
        """Test all agents are updated."""
        scheduler = RoundRobinScheduler()
        agents = [MockAgent(f"agent{i}") for i in range(5)]

        result = list(scheduler.get_update_order(agents, None))

        assert len(result) == 5
        agent_ids = {a.agent_id for a in result}
        assert len(agent_ids) == 5

    def test_tracks_update_counts(self):
        """Test update counts are tracked."""
        scheduler = RoundRobinScheduler(track_updates=True)
        agents = [MockAgent(f"agent{i}") for i in range(3)]

        # First round
        list(scheduler.get_update_order(agents, None))

        for agent in agents:
            assert scheduler.get_update_count(agent) == 1

        # Second round
        list(scheduler.get_update_order(agents, None))

        for agent in agents:
            assert scheduler.get_update_count(agent) == 2

    def test_reset_counts(self):
        """Test reset clears counts."""
        scheduler = RoundRobinScheduler()
        agents = [MockAgent("agent1")]

        list(scheduler.get_update_order(agents, None))
        assert scheduler.get_update_count(agents[0]) == 1

        scheduler.reset_counts()
        assert scheduler.get_update_count(agents[0]) == 0

    def test_get_name(self):
        """Test scheduler name."""
        scheduler = RoundRobinScheduler()
        assert "RoundRobinScheduler" in scheduler.get_name()


class TestAdaptiveScheduler:
    """Tests for AdaptiveScheduler."""

    def test_initialization(self):
        """Test adaptive scheduler initializes with strategies."""
        scheduler = AdaptiveScheduler()
        assert "AdaptiveScheduler" in scheduler.get_name()

    def test_adapts_to_high_conflict(self):
        """Test switches to priority for high conflict."""
        scheduler = AdaptiveScheduler()

        # Many low-health agents = high conflict
        agents = [MockAgent(f"agent{i}", health=30.0) for i in range(10)]

        list(scheduler.get_update_order(agents, None))

        assert "priority" in scheduler.get_name().lower()

    def test_handles_many_agents(self):
        """Test switches to random for many agents."""
        scheduler = AdaptiveScheduler()

        # Many healthy agents
        agents = [MockAgent(f"agent{i}") for i in range(150)]

        list(scheduler.get_update_order(agents, None))

        assert "random" in scheduler.get_name().lower()

    def test_step_callbacks(self):
        """Test step start/end callbacks."""
        scheduler = AdaptiveScheduler()

        # Should not raise
        scheduler.on_step_start(1)
        scheduler.on_step_end(1)


class TestSchedulerInterface:
    """Tests for scheduler interface compliance."""

    @pytest.mark.parametrize("scheduler_class", [
        SequentialScheduler,
        lambda: RandomScheduler(seed=42),
        PriorityScheduler,
        RoundRobinScheduler,
        AdaptiveScheduler,
    ])
    def test_interface_compliance(self, scheduler_class):
        """Test all schedulers implement interface."""
        scheduler = scheduler_class() if callable(scheduler_class) else scheduler_class

        # Must have get_update_order
        assert hasattr(scheduler, 'get_update_order')

        # Must have get_name
        assert hasattr(scheduler, 'get_name')
        name = scheduler.get_name()
        assert isinstance(name, str)

        # get_update_order must be iterable
        agents = [MockAgent(f"agent{i}") for i in range(3)]
        result = scheduler.get_update_order(agents, None)
        assert hasattr(result, '__iter__')
