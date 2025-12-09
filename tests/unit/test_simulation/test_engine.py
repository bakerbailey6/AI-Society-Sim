"""Tests for simulation engine.

This module tests the simulation engine including:
- SimulationEngine lifecycle
- State management
- Observer notifications
- Configuration
"""
import pytest
import sys
import os

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src')
sys.path.insert(0, src_path)

from simulation.engine import (
    SimulationEngine,
    SimulationConfig,
    SimulationState,
    SimulationObserver,
    SimulationEvent,
    SimulationEventType,
    StepResult,
)
from simulation.scheduler import SequentialScheduler


class MockWorld:
    """Mock world for engine testing."""
    pass


class MockAgent:
    """Mock agent for engine testing."""

    def __init__(self, agent_id: str, health: float = 100.0):
        self.agent_id = agent_id
        self.name = f"Agent_{agent_id}"
        self.health = health
        self.max_health = 100.0
        self.energy = 100.0
        self.max_energy = 100.0


class MockSimulationObserver(SimulationObserver):
    """Mock observer for testing."""

    def __init__(self):
        self.events = []

    def on_event(self, event: SimulationEvent) -> None:
        self.events.append(event)


class TestSimulationConfig:
    """Tests for SimulationConfig."""

    def test_default_config(self):
        """Test default configuration values."""
        config = SimulationConfig()

        assert config.max_steps is None
        assert config.enable_analytics is True
        assert config.stop_on_extinction is True

    def test_custom_config(self):
        """Test custom configuration."""
        config = SimulationConfig(
            max_steps=100,
            step_delay_ms=10.0,
            enable_analytics=False
        )

        assert config.max_steps == 100
        assert config.step_delay_ms == 10.0
        assert config.enable_analytics is False


class TestSimulationEngine:
    """Tests for SimulationEngine."""

    def test_initialization(self):
        """Test engine initialization."""
        engine = SimulationEngine()
        assert engine.state == SimulationState.UNINITIALIZED

    def test_initialization_with_world_and_agents(self):
        """Test initialization with world and agents."""
        world = MockWorld()
        agents = [MockAgent("a1"), MockAgent("a2")]

        engine = SimulationEngine(world=world, agents=agents)

        assert engine.world is world
        assert len(engine.agents) == 2

    def test_initialize(self):
        """Test initialize method."""
        world = MockWorld()
        engine = SimulationEngine(world=world)

        result = engine.initialize()

        assert result is True
        assert engine.state == SimulationState.INITIALIZED

    def test_initialize_without_world(self):
        """Test initialize fails without world."""
        engine = SimulationEngine()

        result = engine.initialize()

        assert result is False
        assert engine.state == SimulationState.ERROR

    def test_initialize_twice_raises(self):
        """Test initializing twice raises error."""
        world = MockWorld()
        engine = SimulationEngine(world=world)
        engine.initialize()

        with pytest.raises(RuntimeError):
            engine.initialize()

    def test_step_before_initialize(self):
        """Test step fails before initialization."""
        engine = SimulationEngine()

        with pytest.raises(RuntimeError):
            engine.step()

    def test_step_after_initialize(self):
        """Test step works after initialization."""
        world = MockWorld()
        config = SimulationConfig(stop_on_extinction=False)
        engine = SimulationEngine(world=world, config=config)
        engine.initialize()

        result = engine.step()

        assert isinstance(result, StepResult)
        assert result.step_number == 1
        assert engine.state == SimulationState.RUNNING

    def test_multiple_steps(self):
        """Test multiple steps increment correctly."""
        world = MockWorld()
        config = SimulationConfig(stop_on_extinction=False)
        engine = SimulationEngine(world=world, config=config)
        engine.initialize()

        for i in range(5):
            result = engine.step()
            assert result.step_number == i + 1

        assert engine.current_step == 5

    def test_pause_and_resume(self):
        """Test pausing and resuming simulation."""
        world = MockWorld()
        config = SimulationConfig(stop_on_extinction=False)
        engine = SimulationEngine(world=world, config=config)
        engine.initialize()
        engine.step()  # Start running

        assert engine.pause() is True
        assert engine.state == SimulationState.PAUSED

        assert engine.resume() is True
        assert engine.state == SimulationState.RUNNING

    def test_pause_when_not_running(self):
        """Test pause fails when not running."""
        world = MockWorld()
        engine = SimulationEngine(world=world)
        engine.initialize()

        assert engine.pause() is False

    def test_stop(self):
        """Test stop request."""
        world = MockWorld()
        engine = SimulationEngine(world=world)

        engine.stop()
        # Should not run any steps after stop
        # Note: This is tested more thoroughly in run tests

    def test_reset(self):
        """Test reset returns to uninitialized."""
        world = MockWorld()
        engine = SimulationEngine(world=world)
        engine.initialize()
        engine.step()

        engine.reset()

        assert engine.state == SimulationState.UNINITIALIZED
        assert engine.current_step == 0

    def test_add_agent(self):
        """Test adding agent."""
        engine = SimulationEngine()
        agent = MockAgent("a1")

        engine.add_agent(agent)

        assert len(engine.agents) == 1

    def test_add_agent_duplicate(self):
        """Test adding same agent twice."""
        engine = SimulationEngine()
        agent = MockAgent("a1")

        engine.add_agent(agent)
        engine.add_agent(agent)

        assert len(engine.agents) == 1

    def test_remove_agent(self):
        """Test removing agent."""
        agent = MockAgent("a1")
        engine = SimulationEngine(agents=[agent])

        result = engine.remove_agent(agent)

        assert result is True
        assert len(engine.agents) == 0

    def test_remove_nonexistent_agent(self):
        """Test removing agent not in list."""
        engine = SimulationEngine()
        agent = MockAgent("a1")

        result = engine.remove_agent(agent)

        assert result is False

    def test_get_agent(self):
        """Test getting agent by ID."""
        agent1 = MockAgent("a1")
        agent2 = MockAgent("a2")
        engine = SimulationEngine(agents=[agent1, agent2])

        found = engine.get_agent("a1")

        assert found is agent1

    def test_get_agent_not_found(self):
        """Test getting nonexistent agent."""
        engine = SimulationEngine()

        found = engine.get_agent("nonexistent")

        assert found is None

    def test_observer_notification(self):
        """Test observer receives events."""
        world = MockWorld()
        engine = SimulationEngine(world=world)
        observer = MockSimulationObserver()
        engine.add_observer(observer)

        engine.initialize()

        assert len(observer.events) == 1
        assert observer.events[0].event_type == SimulationEventType.INITIALIZED

    def test_observer_step_events(self):
        """Test observer receives step events."""
        world = MockWorld()
        engine = SimulationEngine(world=world)
        observer = MockSimulationObserver()
        engine.add_observer(observer)

        engine.initialize()
        engine.step()

        event_types = [e.event_type for e in observer.events]
        assert SimulationEventType.STARTED in event_types
        assert SimulationEventType.STEP_COMPLETED in event_types

    def test_remove_observer(self):
        """Test removing observer stops notifications."""
        world = MockWorld()
        engine = SimulationEngine(world=world)
        observer = MockSimulationObserver()
        engine.add_observer(observer)
        engine.remove_observer(observer)

        engine.initialize()

        assert len(observer.events) == 0

    def test_run_with_max_steps(self):
        """Test run respects max steps from config."""
        world = MockWorld()
        config = SimulationConfig(max_steps=5, stop_on_extinction=False)
        engine = SimulationEngine(world=world, config=config)

        result = engine.run()

        assert result["final_step"] == 5
        assert engine.state == SimulationState.COMPLETED

    def test_run_with_step_parameter(self):
        """Test run respects steps parameter."""
        world = MockWorld()
        config = SimulationConfig(stop_on_extinction=False)
        engine = SimulationEngine(world=world, config=config)

        result = engine.run(steps=3)

        assert result["steps_run"] == 3

    def test_run_auto_initializes(self):
        """Test run initializes if needed."""
        world = MockWorld()
        config = SimulationConfig(stop_on_extinction=False)
        engine = SimulationEngine(world=world, config=config)

        result = engine.run(steps=1)

        assert result["steps_run"] == 1

    def test_run_stops_on_extinction(self):
        """Test run stops when all agents die."""
        world = MockWorld()
        config = SimulationConfig(stop_on_extinction=True)
        engine = SimulationEngine(world=world, agents=[], config=config)

        result = engine.run(steps=10)

        # Should stop immediately with no agents
        assert engine.state == SimulationState.COMPLETED

    def test_get_summary(self):
        """Test getting simulation summary."""
        world = MockWorld()
        agents = [MockAgent("a1")]
        engine = SimulationEngine(world=world, agents=agents)
        engine.initialize()
        engine.step()

        summary = engine.get_summary()

        assert summary["state"] == "RUNNING"
        assert summary["current_step"] == 1
        assert summary["agent_count"] == 1

    def test_get_events(self):
        """Test getting simulation events."""
        world = MockWorld()
        engine = SimulationEngine(world=world)
        engine.initialize()
        engine.step()

        events = engine.get_events()

        assert len(events) > 0
        assert all(isinstance(e, SimulationEvent) for e in events)

    def test_get_events_filtered(self):
        """Test getting filtered events."""
        world = MockWorld()
        engine = SimulationEngine(world=world)
        engine.initialize()
        engine.step()

        events = engine.get_events(event_type=SimulationEventType.INITIALIZED)

        assert len(events) == 1
        assert events[0].event_type == SimulationEventType.INITIALIZED

    def test_set_scheduler(self):
        """Test setting scheduler."""
        engine = SimulationEngine()
        scheduler = SequentialScheduler()

        engine.set_scheduler(scheduler)
        # No assertion needed - just verify no error

    def test_set_world_while_running_fails(self):
        """Test cannot change world while running."""
        world = MockWorld()
        config = SimulationConfig(stop_on_extinction=False)
        engine = SimulationEngine(world=world, config=config)
        engine.initialize()
        engine.step()

        with pytest.raises(RuntimeError):
            engine.set_world(MockWorld())

    def test_repr(self):
        """Test string representation."""
        world = MockWorld()
        engine = SimulationEngine(world=world)

        repr_str = repr(engine)

        assert "SimulationEngine" in repr_str
        assert "UNINITIALIZED" in repr_str


class TestStepResult:
    """Tests for StepResult dataclass."""

    def test_step_result_creation(self):
        """Test StepResult creation."""
        result = StepResult(
            step_number=1,
            duration_ms=10.5,
            agents_updated=5,
            actions_taken=3
        )

        assert result.step_number == 1
        assert result.duration_ms == 10.5
        assert result.agents_updated == 5
        assert result.actions_taken == 3
        assert result.events == []
        assert result.statistics is None
