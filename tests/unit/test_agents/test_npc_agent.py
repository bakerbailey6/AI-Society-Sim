"""Tests for NPCAgent.

This module tests the scripted agent including:
- BehaviorScript interface
- PatrolScript, GuardScript, MerchantScript, WorkerScript
- Script management
"""
import pytest
import sys
import os

# Add src to path
src_path = os.path.join(os.path.dirname(__file__), '..', '..', '..', 'src')
sys.path.insert(0, src_path)

from world.position import Position
from agents.traits import AgentTraits
from agents.npc_agent import (
    NPCAgent,
    BehaviorScript,
    PatrolScript,
    GuardScript,
    MerchantScript,
    WorkerScript,
    ScriptState,
    ScriptContext,
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
def patrol_waypoints():
    """Provide patrol waypoints."""
    return [
        Position(0, 0),
        Position(10, 0),
        Position(10, 10),
        Position(0, 10),
    ]


class TestScriptContext:
    """Tests for ScriptContext."""

    def test_default_context(self):
        """Test default context values."""
        context = ScriptContext()

        assert context.step_count == 0
        assert context.last_action is None
        assert context.last_success is True
        assert context.custom_data == {}


class TestPatrolScript:
    """Tests for PatrolScript."""

    def test_initialization(self, patrol_waypoints):
        """Test patrol script initialization."""
        script = PatrolScript(patrol_waypoints)

        assert script.name == "patrol"
        assert len(script.waypoints) == 4
        assert script.state == ScriptState.RUNNING

    def test_initialization_empty_waypoints(self):
        """Test empty waypoints raises error."""
        with pytest.raises(ValueError):
            PatrolScript([])

    def test_initialization_no_loop(self, patrol_waypoints):
        """Test non-looping patrol."""
        script = PatrolScript(patrol_waypoints, loop=False)

        assert script.is_complete() is False

    def test_current_waypoint(self, patrol_waypoints):
        """Test getting current waypoint."""
        script = PatrolScript(patrol_waypoints)

        assert script.current_waypoint == patrol_waypoints[0]

    def test_waypoints_copy(self, patrol_waypoints):
        """Test waypoints returns copy."""
        script = PatrolScript(patrol_waypoints)

        waypoints = script.waypoints
        waypoints.append(Position(99, 99))

        assert len(script.waypoints) == 4  # Original unchanged

    def test_is_complete_looping(self, patrol_waypoints):
        """Test looping patrol never completes."""
        script = PatrolScript(patrol_waypoints, loop=True)

        assert script.is_complete() is False

    def test_reset(self, patrol_waypoints):
        """Test reset returns to initial state."""
        script = PatrolScript(patrol_waypoints)
        script._current_index = 2
        script._state = ScriptState.PAUSED

        script.reset()

        assert script._current_index == 0
        assert script.state == ScriptState.RUNNING


class TestGuardScript:
    """Tests for GuardScript."""

    def test_initialization(self, patrol_waypoints):
        """Test guard script initialization."""
        script = GuardScript(patrol_waypoints[:2])

        assert script.name == "guard"
        assert script.guard_radius == GuardScript.DEFAULT_GUARD_RADIUS

    def test_custom_guard_radius(self, patrol_waypoints):
        """Test custom guard radius."""
        script = GuardScript(patrol_waypoints[:2], guard_radius=10.0)

        assert script.guard_radius == 10.0

    def test_is_engaged_default(self, patrol_waypoints):
        """Test not engaged by default."""
        script = GuardScript(patrol_waypoints[:2])

        assert script.is_engaged is False

    def test_is_complete_never(self, patrol_waypoints):
        """Test guards never complete."""
        script = GuardScript(patrol_waypoints[:2])

        assert script.is_complete() is False

    def test_reset(self, patrol_waypoints):
        """Test reset clears target."""
        script = GuardScript(patrol_waypoints[:2])
        script._current_target = "enemy1"

        script.reset()

        assert script._current_target is None


class TestMerchantScript:
    """Tests for MerchantScript."""

    def test_initialization(self):
        """Test merchant script initialization."""
        script = MerchantScript(Position(25, 25))

        assert script.name == "merchant"
        assert script.home_position == Position(25, 25)
        assert script.trade_radius == MerchantScript.DEFAULT_TRADE_RADIUS

    def test_custom_trade_radius(self):
        """Test custom trade radius."""
        script = MerchantScript(Position(25, 25), trade_radius=5.0)

        assert script.trade_radius == 5.0

    def test_is_complete_never(self):
        """Test merchants never complete."""
        script = MerchantScript(Position(25, 25))

        assert script.is_complete() is False

    def test_reset(self):
        """Test reset restores state."""
        script = MerchantScript(Position(25, 25))
        script._state = ScriptState.PAUSED

        script.reset()

        assert script.state == ScriptState.RUNNING


class TestWorkerScript:
    """Tests for WorkerScript."""

    def test_initialization(self):
        """Test worker script initialization."""
        deposit = Position(0, 0)
        gather = [Position(10, 10), Position(20, 20)]
        script = WorkerScript(deposit, gather)

        assert script.name == "worker"
        assert script.deposit_position == deposit
        assert script.current_phase == "going_to_gather"

    def test_initialization_empty_gather(self):
        """Test empty gather positions raises error."""
        with pytest.raises(ValueError):
            WorkerScript(Position(0, 0), [])

    def test_carrying_default(self):
        """Test carrying starts at 0."""
        script = WorkerScript(Position(0, 0), [Position(10, 10)])

        assert script.carrying == 0.0

    def test_is_complete_never(self):
        """Test workers never complete."""
        script = WorkerScript(Position(0, 0), [Position(10, 10)])

        assert script.is_complete() is False

    def test_reset(self):
        """Test reset clears state."""
        script = WorkerScript(Position(0, 0), [Position(10, 10)])
        script._carrying = 5.0
        script._phase = "returning"

        script.reset()

        assert script.carrying == 0.0
        assert script.current_phase == "going_to_gather"


class TestScriptStateManagement:
    """Tests for script state management."""

    def test_pause(self, patrol_waypoints):
        """Test pausing script."""
        script = PatrolScript(patrol_waypoints)

        script.pause()

        assert script.state == ScriptState.PAUSED

    def test_pause_not_running(self, patrol_waypoints):
        """Test pause when not running does nothing."""
        script = PatrolScript(patrol_waypoints)
        script._state = ScriptState.COMPLETED

        script.pause()

        assert script.state == ScriptState.COMPLETED

    def test_resume(self, patrol_waypoints):
        """Test resuming script."""
        script = PatrolScript(patrol_waypoints)
        script.pause()

        script.resume()

        assert script.state == ScriptState.RUNNING

    def test_resume_not_paused(self, patrol_waypoints):
        """Test resume when not paused does nothing."""
        script = PatrolScript(patrol_waypoints)

        script.resume()

        assert script.state == ScriptState.RUNNING

    def test_interrupt(self, patrol_waypoints):
        """Test interrupting script."""
        script = PatrolScript(patrol_waypoints)

        script.interrupt()

        assert script.state == ScriptState.INTERRUPTED


class TestNPCAgentInitialization:
    """Tests for NPCAgent initialization."""

    def test_default_initialization(self, default_traits):
        """Test default initialization."""
        agent = NPCAgent(
            name="Guard",
            position=Position(0, 0),
            traits=default_traits
        )

        assert agent.name == "Guard"
        assert agent.get_script() is None

    def test_with_script(self, default_traits, patrol_waypoints):
        """Test initialization with script."""
        script = PatrolScript(patrol_waypoints)
        agent = NPCAgent(
            name="Patrol",
            position=Position(0, 0),
            traits=default_traits,
            behavior_script=script
        )

        assert agent.get_script() is script


class TestNPCAgentScriptManagement:
    """Tests for NPCAgent script management."""

    def test_set_script(self, default_traits, patrol_waypoints):
        """Test setting script."""
        agent = NPCAgent(
            name="Test",
            position=Position(0, 0),
            traits=default_traits
        )

        script = PatrolScript(patrol_waypoints)
        agent.set_script(script)

        assert agent.get_script() is script

    def test_clear_script(self, default_traits, patrol_waypoints):
        """Test clearing script."""
        script = PatrolScript(patrol_waypoints)
        agent = NPCAgent(
            name="Test",
            position=Position(0, 0),
            traits=default_traits,
            behavior_script=script
        )

        agent.clear_script()

        assert agent.get_script() is None

    def test_pause_script(self, default_traits, patrol_waypoints):
        """Test pausing script through agent."""
        script = PatrolScript(patrol_waypoints)
        agent = NPCAgent(
            name="Test",
            position=Position(0, 0),
            traits=default_traits,
            behavior_script=script
        )

        agent.pause_script()

        assert script.state == ScriptState.PAUSED

    def test_resume_script(self, default_traits, patrol_waypoints):
        """Test resuming script through agent."""
        script = PatrolScript(patrol_waypoints)
        agent = NPCAgent(
            name="Test",
            position=Position(0, 0),
            traits=default_traits,
            behavior_script=script
        )
        script.pause()

        agent.resume_script()

        assert script.state == ScriptState.RUNNING

    def test_interrupt_script(self, default_traits, patrol_waypoints):
        """Test interrupting script through agent."""
        script = PatrolScript(patrol_waypoints)
        agent = NPCAgent(
            name="Test",
            position=Position(0, 0),
            traits=default_traits,
            behavior_script=script
        )

        agent.interrupt_script()

        assert script.state == ScriptState.INTERRUPTED

    def test_reset_script(self, default_traits, patrol_waypoints):
        """Test resetting script through agent."""
        script = PatrolScript(patrol_waypoints)
        agent = NPCAgent(
            name="Test",
            position=Position(0, 0),
            traits=default_traits,
            behavior_script=script
        )
        script._current_index = 2

        agent.reset_script()

        assert script._current_index == 0

    def test_get_script_state(self, default_traits, patrol_waypoints):
        """Test getting script state."""
        script = PatrolScript(patrol_waypoints)
        agent = NPCAgent(
            name="Test",
            position=Position(0, 0),
            traits=default_traits,
            behavior_script=script
        )

        state = agent.get_script_state()

        assert state == ScriptState.RUNNING

    def test_get_script_state_no_script(self, default_traits):
        """Test getting script state with no script."""
        agent = NPCAgent(
            name="Test",
            position=Position(0, 0),
            traits=default_traits
        )

        state = agent.get_script_state()

        assert state is None


class TestNPCAgentRepr:
    """Tests for string representation."""

    def test_repr_no_script(self, default_traits):
        """Test repr without script."""
        agent = NPCAgent(
            name="Test",
            position=Position(0, 0),
            traits=default_traits
        )

        repr_str = repr(agent)

        assert "NPCAgent" in repr_str
        assert "Test" in repr_str
        assert "None" in repr_str

    def test_repr_with_script(self, default_traits, patrol_waypoints):
        """Test repr with script."""
        script = PatrolScript(patrol_waypoints)
        agent = NPCAgent(
            name="Guard",
            position=Position(5, 5),
            traits=default_traits,
            behavior_script=script
        )

        repr_str = repr(agent)

        assert "NPCAgent" in repr_str
        assert "Guard" in repr_str
        assert "patrol" in repr_str
