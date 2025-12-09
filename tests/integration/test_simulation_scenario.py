"""Integration tests for simulation scenarios.

This module tests complete simulation workflows involving:
- Engine initialization and lifecycle
- Multiple schedulers
- Analytics collection
- Observer integration
"""
import pytest
import sys
import os

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), '..', '..', 'src')
sys.path.insert(0, src_path)

from simulation.engine import (
    SimulationEngine,
    SimulationConfig,
    SimulationState,
    SimulationObserver,
    SimulationEvent,
    SimulationEventType,
)
from simulation.scheduler import (
    SequentialScheduler,
    RandomScheduler,
    PriorityScheduler,
    RoundRobinScheduler,
)
from simulation.analytics import (
    AnalyticsCollector,
    WealthDistributionAnalyzer,
    SurvivalAnalyzer,
)


class MockWorld:
    """Mock world for simulation testing."""

    def __init__(self, width=10, height=10):
        self.width = width
        self.height = height

    def update(self):
        """Update world state."""
        pass


class MockAgent:
    """Mock agent for simulation testing."""

    def __init__(self, agent_id: str, health: float = 100.0):
        self.agent_id = agent_id
        self.name = f"Agent_{agent_id}"
        self.health = health
        self.max_health = 100.0
        self.energy = 100.0
        self.max_energy = 100.0

    def sense(self, world):
        return {"world": world}

    def decide(self, sensor_data):
        return None

    def act(self, action, world):
        pass


class SimulationTracker(SimulationObserver):
    """Observer to track simulation events."""

    def __init__(self):
        self.events_by_type = {}
        self.total_events = 0

    def on_event(self, event: SimulationEvent) -> None:
        self.total_events += 1
        event_type = event.event_type.name
        if event_type not in self.events_by_type:
            self.events_by_type[event_type] = []
        self.events_by_type[event_type].append(event)


class TestSimulationLifecycle:
    """Tests for simulation lifecycle."""

    def test_complete_lifecycle(self):
        """Test complete simulation lifecycle."""
        world = MockWorld()
        agents = [MockAgent(f"agent{i}") for i in range(5)]
        config = SimulationConfig(max_steps=10)

        engine = SimulationEngine(
            world=world,
            agents=agents,
            config=config
        )

        # Initialize
        assert engine.initialize() is True
        assert engine.state == SimulationState.INITIALIZED

        # Run
        result = engine.run()

        assert result["final_step"] == 10
        assert engine.state == SimulationState.COMPLETED

    def test_pause_resume_cycle(self):
        """Test pausing and resuming simulation."""
        world = MockWorld()
        agents = [MockAgent("agent1")]
        engine = SimulationEngine(world=world, agents=agents)

        engine.initialize()
        engine.step()  # Start running

        # Pause
        engine.pause()
        assert engine.state == SimulationState.PAUSED

        # Resume
        engine.resume()
        assert engine.state == SimulationState.RUNNING

        # Step should work
        result = engine.step()
        assert result.step_number == 2


class TestSchedulerIntegration:
    """Tests for different schedulers with simulation."""

    @pytest.mark.parametrize("scheduler_class,seed", [
        (SequentialScheduler, None),
        (lambda: RandomScheduler(seed=42), None),
        (PriorityScheduler, None),
        (RoundRobinScheduler, None),
    ])
    def test_scheduler_works_with_engine(self, scheduler_class, seed):
        """Test each scheduler type works with engine."""
        world = MockWorld()
        agents = [MockAgent(f"agent{i}") for i in range(5)]

        scheduler = scheduler_class() if callable(scheduler_class) else scheduler_class

        engine = SimulationEngine(
            world=world,
            agents=agents,
            scheduler=scheduler
        )

        engine.initialize()
        result = engine.run(steps=5)

        assert result["steps_run"] == 5


class TestAnalyticsIntegration:
    """Tests for analytics integration with simulation."""

    def test_analytics_collection(self):
        """Test analytics are collected during simulation."""
        world = MockWorld()
        agents = [MockAgent(f"agent{i}") for i in range(5)]
        config = SimulationConfig(enable_analytics=True)

        engine = SimulationEngine(
            world=world,
            agents=agents,
            config=config
        )

        engine.initialize()
        engine.run(steps=10)

        # Check analytics
        analytics = engine.analytics
        assert analytics is not None

        summary = analytics.get_summary()
        assert summary["total_steps"] == 10
        assert summary["unique_agents"] == 5

    def test_analytics_disabled(self):
        """Test analytics can be disabled."""
        world = MockWorld()
        config = SimulationConfig(enable_analytics=False)

        engine = SimulationEngine(world=world, config=config)

        assert engine.analytics is None


class TestObserverIntegration:
    """Tests for observer integration."""

    def test_observer_receives_all_events(self):
        """Test observer receives expected events."""
        world = MockWorld()
        agents = [MockAgent("agent1")]
        config = SimulationConfig(max_steps=5)

        engine = SimulationEngine(
            world=world,
            agents=agents,
            config=config
        )

        tracker = SimulationTracker()
        engine.add_observer(tracker)

        engine.initialize()
        engine.run()

        # Should have received initialize, start, step_completed (x5), completed
        assert "INITIALIZED" in tracker.events_by_type
        assert "STARTED" in tracker.events_by_type
        assert "STEP_COMPLETED" in tracker.events_by_type
        assert "COMPLETED" in tracker.events_by_type

        assert len(tracker.events_by_type["STEP_COMPLETED"]) == 5

    def test_multiple_observers(self):
        """Test multiple observers all receive events."""
        world = MockWorld()
        engine = SimulationEngine(world=world)

        tracker1 = SimulationTracker()
        tracker2 = SimulationTracker()
        engine.add_observer(tracker1)
        engine.add_observer(tracker2)

        engine.initialize()
        engine.step()

        assert tracker1.total_events == tracker2.total_events
        assert tracker1.total_events > 0


class TestAgentManagement:
    """Tests for agent management during simulation."""

    def test_add_agent_during_simulation(self):
        """Test adding agent during simulation."""
        world = MockWorld()
        engine = SimulationEngine(world=world)

        engine.initialize()
        engine.step()

        # Add new agent
        new_agent = MockAgent("new_agent")
        engine.add_agent(new_agent)

        assert len(engine.agents) == 1
        assert engine.get_agent("new_agent") is new_agent

    def test_remove_agent_during_simulation(self):
        """Test removing agent during simulation."""
        agent = MockAgent("agent1")
        engine = SimulationEngine(world=MockWorld(), agents=[agent])

        engine.initialize()

        result = engine.remove_agent(agent)

        assert result is True
        assert len(engine.agents) == 0


class TestStopConditions:
    """Tests for simulation stop conditions."""

    def test_stop_on_max_steps(self):
        """Test simulation stops at max steps."""
        world = MockWorld()
        config = SimulationConfig(max_steps=5, stop_on_extinction=False)

        engine = SimulationEngine(world=world, config=config)
        engine.initialize()

        result = engine.run()

        assert result["final_step"] == 5
        assert engine.state == SimulationState.COMPLETED

    def test_stop_on_extinction(self):
        """Test simulation stops when no agents remain."""
        world = MockWorld()
        config = SimulationConfig(stop_on_extinction=True, max_steps=100)

        engine = SimulationEngine(world=world, agents=[], config=config)
        engine.initialize()

        result = engine.run()

        assert engine.state == SimulationState.COMPLETED


class TestSimulationSummary:
    """Tests for simulation summary."""

    def test_summary_content(self):
        """Test summary contains expected information."""
        world = MockWorld()
        agents = [MockAgent(f"agent{i}") for i in range(3)]
        config = SimulationConfig(max_steps=5, enable_analytics=True)

        engine = SimulationEngine(
            world=world,
            agents=agents,
            config=config
        )

        engine.initialize()
        engine.run()

        summary = engine.get_summary()

        assert summary["state"] == "COMPLETED"
        assert summary["current_step"] == 5
        assert summary["agent_count"] == 3
        assert "analytics" in summary


class TestWealthAnalyzerIntegration:
    """Tests for wealth analyzer with simulation data."""

    def test_gini_calculation(self):
        """Test Gini coefficient calculation."""
        analyzer = WealthDistributionAnalyzer()

        # Simulate wealth distribution
        wealth_values = [10, 20, 30, 40, 100]  # Unequal

        gini = analyzer.calculate_gini(wealth_values)

        assert 0 < gini < 1  # Valid range
        assert gini > 0.2  # Somewhat unequal

    def test_distribution_summary(self):
        """Test distribution summary."""
        analyzer = WealthDistributionAnalyzer()

        wealth_values = [50, 100, 150, 200, 250]

        summary = analyzer.get_distribution_summary(wealth_values)

        assert summary["count"] == 5
        assert summary["total"] == 750
        assert summary["mean"] == 150
        assert summary["median"] == 150


class TestSurvivalAnalyzerIntegration:
    """Tests for survival analyzer."""

    def test_survival_rate_calculation(self):
        """Test survival rate calculation."""
        from simulation.analytics import AgentStatistics

        analyzer = SurvivalAnalyzer()

        agent_stats = {
            "a1": AgentStatistics(agent_id="a1", name="Agent1"),
            "a2": AgentStatistics(agent_id="a2", name="Agent2", death_step=5),
            "a3": AgentStatistics(agent_id="a3", name="Agent3"),
        }

        rate = analyzer.get_survival_rate(agent_stats)

        assert rate == pytest.approx(0.667, rel=0.01)  # 2/3
