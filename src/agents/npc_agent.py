"""
NPCAgent Module - Scripted Behavior Agent

This module provides an agent with predefined, scripted behavior patterns
suitable for specific roles like guards, merchants, or workers.

Design Patterns:
    - Strategy Pattern: Behavior script is pluggable
    - Command Pattern: Scripts are sequences of callable behaviors
    - Template Method: BehaviorScript defines execution skeleton

SOLID Principles:
    - Single Responsibility: Executes scripted behaviors
    - Open/Closed: New scripts can be added without modification
    - Liskov Substitution: Can be used anywhere Agent is expected

Integration:
    - Uses actions/move.py for movement
    - Uses actions/gather.py for resource collection
    - Uses actions/trade.py for merchant behavior
    - Uses actions/attack.py for guard combat
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import Optional, List, Callable, Any, TYPE_CHECKING, Dict

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import Agent
from traits import AgentTraits
from world.position import Position

if TYPE_CHECKING:
    from world.world import World
    from actions.action import Action
    from policies.policy import DecisionPolicy


class ScriptState(Enum):
    """State of a behavior script execution."""
    RUNNING = auto()
    PAUSED = auto()
    COMPLETED = auto()
    INTERRUPTED = auto()


@dataclass
class ScriptContext:
    """
    Context information for script execution.

    Provides scripts with state information they need
    to make decisions.

    Attributes:
        step_count: Number of steps executed
        last_action: Last action taken
        last_success: Whether last action succeeded
        custom_data: Script-specific data storage
    """
    step_count: int = 0
    last_action: Optional[str] = None
    last_success: bool = True
    custom_data: Dict[str, Any] = field(default_factory=dict)


class BehaviorScript(ABC):
    """
    Abstract base for NPC behavior scripts.

    BehaviorScript defines the interface for scripted behaviors
    that NPCAgent can execute. Scripts can be simple sequences
    or complex state machines.

    Design Patterns:
        - Template Method: Defines execution skeleton
        - State: Scripts can have internal state

    Subclasses:
        - PatrolScript: Move between waypoints
        - GuardScript: Patrol and attack intruders
        - MerchantScript: Stay in place and trade
        - WorkerScript: Gather and deposit resources

    Examples:
        >>> script = PatrolScript([Position(0, 0), Position(10, 10)])
        >>> agent = NPCAgent("Guard", Position(0, 0), traits, script)
        >>> action = script.get_action(sensor_data, agent)
    """

    def __init__(self, name: str = "unnamed") -> None:
        """
        Initialize a BehaviorScript.

        Args:
            name: Script identifier
        """
        self._name = name
        self._state = ScriptState.RUNNING
        self._context = ScriptContext()

    @property
    def name(self) -> str:
        """Script name."""
        return self._name

    @property
    def state(self) -> ScriptState:
        """Current script state."""
        return self._state

    @property
    def context(self) -> ScriptContext:
        """Script execution context."""
        return self._context

    @abstractmethod
    def get_action(
        self,
        sensor_data: Any,
        agent: Agent
    ) -> Optional[Action]:
        """
        Get next action based on script logic.

        Args:
            sensor_data: Current perception
            agent: The NPC agent

        Returns:
            Optional[Action]: Next action or None
        """
        pass

    @abstractmethod
    def is_complete(self) -> bool:
        """
        Check if script has finished.

        Returns:
            bool: True if script is complete
        """
        pass

    @abstractmethod
    def reset(self) -> None:
        """Reset script to initial state."""
        pass

    def pause(self) -> None:
        """Pause script execution."""
        if self._state == ScriptState.RUNNING:
            self._state = ScriptState.PAUSED

    def resume(self) -> None:
        """Resume paused script."""
        if self._state == ScriptState.PAUSED:
            self._state = ScriptState.RUNNING

    def interrupt(self) -> None:
        """Interrupt script (for emergency behavior)."""
        self._state = ScriptState.INTERRUPTED

    def _update_context(self, action: Optional[Action], success: bool) -> None:
        """Update execution context after action."""
        self._context.step_count += 1
        self._context.last_action = type(action).__name__ if action else None
        self._context.last_success = success


class PatrolScript(BehaviorScript):
    """
    Script for patrolling between waypoints.

    Agent moves between a series of positions in order,
    optionally looping back to the start.

    Attributes:
        waypoints: List of positions to visit
        current_index: Current waypoint index
        loop: Whether to loop when reaching end

    Examples:
        >>> waypoints = [Position(0, 0), Position(10, 0), Position(10, 10)]
        >>> script = PatrolScript(waypoints, loop=True)
    """

    def __init__(
        self,
        waypoints: List[Position],
        loop: bool = True,
        name: str = "patrol"
    ) -> None:
        """
        Initialize PatrolScript.

        Args:
            waypoints: Positions to patrol between
            loop: Whether to loop continuously
            name: Script name

        Raises:
            ValueError: If waypoints list is empty
        """
        super().__init__(name)
        if not waypoints:
            raise ValueError("Waypoints list cannot be empty")

        self._waypoints = waypoints
        self._current_index = 0
        self._loop = loop

    @property
    def waypoints(self) -> List[Position]:
        """List of patrol waypoints."""
        return self._waypoints.copy()

    @property
    def current_waypoint(self) -> Position:
        """Current target waypoint."""
        return self._waypoints[self._current_index]

    def get_action(
        self,
        sensor_data: Any,
        agent: Agent
    ) -> Optional[Action]:
        """
        Get move action towards current waypoint.

        Returns MoveAction towards current waypoint. When waypoint
        is reached, advances to next waypoint.

        Args:
            sensor_data: Current perception
            agent: The NPC agent

        Returns:
            Optional[Action]: MoveAction or None if complete

        Note:
            Implementation would:
            1. Check if at current waypoint
            2. If yes, advance to next waypoint
            3. Return MoveAction towards waypoint
        """
        if self.is_complete():
            return None

        # Implementation would:
        # from actions.move import MoveAction
        #
        # target = self._waypoints[self._current_index]
        # if agent.position == target or agent.position.distance_to(target) < 1:
        #     self._advance_waypoint()
        #     if self.is_complete():
        #         return None
        #     target = self._waypoints[self._current_index]
        #
        # direction = self._get_direction_to(agent.position, target)
        # return MoveAction(direction)

        return None

    def is_complete(self) -> bool:
        """Check if patrol is complete (only if not looping)."""
        if self._loop:
            return False
        return self._current_index >= len(self._waypoints)

    def reset(self) -> None:
        """Reset patrol to first waypoint."""
        self._current_index = 0
        self._state = ScriptState.RUNNING
        self._context = ScriptContext()

    def _advance_waypoint(self) -> None:
        """Advance to next waypoint."""
        self._current_index += 1
        if self._loop and self._current_index >= len(self._waypoints):
            self._current_index = 0


class GuardScript(BehaviorScript):
    """
    Script for guard behavior: patrol and defend.

    Combines patrol behavior with attack response when
    enemies are detected in guarded area.

    Priority:
        1. Attack nearby enemies
        2. Return to patrol route
        3. Continue patrol

    Attributes:
        patrol_script: Underlying patrol behavior
        guard_radius: Distance to detect intruders
        attack_threshold: Health threshold to continue fighting

    Examples:
        >>> waypoints = [Position(5, 5), Position(15, 5)]
        >>> script = GuardScript(waypoints, guard_radius=5.0)
    """

    DEFAULT_GUARD_RADIUS: float = 5.0
    DEFAULT_ATTACK_THRESHOLD: float = 20.0

    def __init__(
        self,
        patrol_waypoints: List[Position],
        guard_radius: float = DEFAULT_GUARD_RADIUS,
        attack_threshold: float = DEFAULT_ATTACK_THRESHOLD,
        name: str = "guard"
    ) -> None:
        """
        Initialize GuardScript.

        Args:
            patrol_waypoints: Patrol route positions
            guard_radius: Detection radius
            attack_threshold: Min health to fight
            name: Script name
        """
        super().__init__(name)
        self._patrol_script = PatrolScript(patrol_waypoints, loop=True)
        self._guard_radius = guard_radius
        self._attack_threshold = attack_threshold
        self._current_target: Optional[str] = None

    @property
    def guard_radius(self) -> float:
        """Detection radius for intruders."""
        return self._guard_radius

    @property
    def is_engaged(self) -> bool:
        """Whether currently engaged with an enemy."""
        return self._current_target is not None

    def get_action(
        self,
        sensor_data: Any,
        agent: Agent
    ) -> Optional[Action]:
        """
        Get guard action based on situation.

        Decision Flow:
            1. Check health - retreat if too low
            2. Detect enemies in range
            3. If enemy found, attack
            4. Otherwise, continue patrol

        Args:
            sensor_data: Current perception
            agent: The NPC agent

        Returns:
            Optional[Action]: Combat or patrol action

        Note:
            Implementation would:
            1. Check if health < threshold, retreat/rest
            2. Find nearby enemies within guard_radius
            3. If enemy: return AttackAction
            4. Else: return patrol script action
        """
        # Implementation would:
        # from actions.attack import AttackAction
        #
        # # Check health
        # health_percent = (agent.health / agent.max_health) * 100
        # if health_percent < self._attack_threshold:
        #     self._current_target = None
        #     return RestAction()
        #
        # # Find enemies
        # nearby_agents = sensor_data.get('nearby_agents', [])
        # enemies = set(sensor_data.get('enemies', []))
        #
        # for agent_info in nearby_agents:
        #     agent_id, enemy, distance = agent_info
        #     if agent_id in enemies and distance <= self._guard_radius:
        #         self._current_target = agent_id
        #         return AttackAction(agent_id)
        #
        # # No enemy, patrol
        # self._current_target = None
        # return self._patrol_script.get_action(sensor_data, agent)

        return None

    def is_complete(self) -> bool:
        """Guards never complete (always on duty)."""
        return False

    def reset(self) -> None:
        """Reset guard state and patrol."""
        self._patrol_script.reset()
        self._current_target = None
        self._state = ScriptState.RUNNING
        self._context = ScriptContext()


class MerchantScript(BehaviorScript):
    """
    Script for merchant behavior: stay and trade.

    Merchant stays in a location and responds to trade
    requests from nearby agents. Can advertise wares
    and adjust prices based on supply/demand.

    Attributes:
        home_position: Location to stay at
        trade_radius: Distance for trade interactions
        price_multiplier: Markup on trades

    Examples:
        >>> script = MerchantScript(Position(25, 25), price_multiplier=1.2)
    """

    DEFAULT_TRADE_RADIUS: float = 3.0
    DEFAULT_PRICE_MULTIPLIER: float = 1.0

    def __init__(
        self,
        home_position: Position,
        trade_radius: float = DEFAULT_TRADE_RADIUS,
        price_multiplier: float = DEFAULT_PRICE_MULTIPLIER,
        name: str = "merchant"
    ) -> None:
        """
        Initialize MerchantScript.

        Args:
            home_position: Where merchant stays
            trade_radius: Range for trades
            price_multiplier: Price markup factor
            name: Script name
        """
        super().__init__(name)
        self._home_position = home_position
        self._trade_radius = trade_radius
        self._price_multiplier = price_multiplier

    @property
    def home_position(self) -> Position:
        """Merchant's home location."""
        return self._home_position

    @property
    def trade_radius(self) -> float:
        """Range for trade interactions."""
        return self._trade_radius

    def get_action(
        self,
        sensor_data: Any,
        agent: Agent
    ) -> Optional[Action]:
        """
        Get merchant action.

        Decision Flow:
            1. If not at home, move towards home
            2. If ally nearby, offer trade
            3. Otherwise, rest/wait

        Args:
            sensor_data: Current perception
            agent: The NPC agent

        Returns:
            Optional[Action]: Trade, move, or rest action

        Note:
            Implementation would:
            1. Check distance to home_position
            2. If > 1, return MoveAction towards home
            3. Find nearby allies
            4. If ally in range, return TradeAction
            5. Else return RestAction
        """
        # Implementation would:
        # from actions.move import MoveAction
        # from actions.trade import TradeAction
        # from actions.rest import RestAction
        #
        # # Return home if away
        # if agent.position.distance_to(self._home_position) > 1:
        #     direction = self._get_direction_to(agent.position, self._home_position)
        #     return MoveAction(direction)
        #
        # # Check for trade opportunities
        # nearby_agents = sensor_data.get('nearby_agents', [])
        # allies = set(sensor_data.get('allies', []))
        #
        # for agent_info in nearby_agents:
        #     agent_id, other, distance = agent_info
        #     if agent_id in allies and distance <= self._trade_radius:
        #         # Offer trade based on inventory
        #         return TradeAction(agent_id, self._get_offers(), {})
        #
        # return RestAction()

        return None

    def is_complete(self) -> bool:
        """Merchants never complete (always ready to trade)."""
        return False

    def reset(self) -> None:
        """Reset merchant state."""
        self._state = ScriptState.RUNNING
        self._context = ScriptContext()


class WorkerScript(BehaviorScript):
    """
    Script for worker behavior: gather and deposit.

    Worker gathers resources and brings them back to
    a deposit location (e.g., faction stockpile).

    Phases:
        1. Move to resource location
        2. Gather resources
        3. Return to deposit
        4. Deposit resources
        5. Repeat

    Attributes:
        deposit_position: Where to deposit resources
        gather_positions: Locations to gather from
        capacity: Max resources to carry

    Examples:
        >>> script = WorkerScript(
        ...     deposit=Position(0, 0),
        ...     gather_positions=[Position(10, 10), Position(20, 20)]
        ... )
    """

    DEFAULT_CAPACITY: int = 10

    def __init__(
        self,
        deposit_position: Position,
        gather_positions: List[Position],
        capacity: int = DEFAULT_CAPACITY,
        name: str = "worker"
    ) -> None:
        """
        Initialize WorkerScript.

        Args:
            deposit_position: Deposit/home location
            gather_positions: Resource locations
            capacity: Max carry capacity
            name: Script name

        Raises:
            ValueError: If gather_positions is empty
        """
        super().__init__(name)
        if not gather_positions:
            raise ValueError("Gather positions cannot be empty")

        self._deposit_position = deposit_position
        self._gather_positions = gather_positions
        self._capacity = capacity
        self._current_gather_index = 0
        self._carrying: float = 0.0
        self._phase: str = "going_to_gather"  # or "gathering", "returning", "depositing"

    @property
    def deposit_position(self) -> Position:
        """Resource deposit location."""
        return self._deposit_position

    @property
    def current_phase(self) -> str:
        """Current work phase."""
        return self._phase

    @property
    def carrying(self) -> float:
        """Amount of resources being carried."""
        return self._carrying

    def get_action(
        self,
        sensor_data: Any,
        agent: Agent
    ) -> Optional[Action]:
        """
        Get worker action based on current phase.

        State Machine:
            going_to_gather -> gathering -> returning -> depositing -> going_to_gather

        Args:
            sensor_data: Current perception
            agent: The NPC agent

        Returns:
            Optional[Action]: Move, gather, or deposit action

        Note:
            Implementation would track phase and return appropriate action
        """
        # Implementation would be a state machine:
        # from actions.move import MoveAction
        # from actions.gather import GatherAction
        #
        # if self._phase == "going_to_gather":
        #     target = self._gather_positions[self._current_gather_index]
        #     if agent.position.distance_to(target) < 1:
        #         self._phase = "gathering"
        #     else:
        #         return MoveAction(direction_to(agent.position, target))
        #
        # elif self._phase == "gathering":
        #     # Check if at capacity or no more resources
        #     if self._carrying >= self._capacity:
        #         self._phase = "returning"
        #     else:
        #         return GatherAction()
        #
        # elif self._phase == "returning":
        #     if agent.position.distance_to(self._deposit_position) < 1:
        #         self._phase = "depositing"
        #     else:
        #         return MoveAction(direction_to(agent.position, self._deposit_position))
        #
        # elif self._phase == "depositing":
        #     # Deposit and reset
        #     self._carrying = 0
        #     self._advance_gather_position()
        #     self._phase = "going_to_gather"

        return None

    def is_complete(self) -> bool:
        """Workers never complete (always working)."""
        return False

    def reset(self) -> None:
        """Reset worker state."""
        self._current_gather_index = 0
        self._carrying = 0.0
        self._phase = "going_to_gather"
        self._state = ScriptState.RUNNING
        self._context = ScriptContext()

    def _advance_gather_position(self) -> None:
        """Move to next gather position."""
        self._current_gather_index = (
            (self._current_gather_index + 1) % len(self._gather_positions)
        )


class NPCAgent(Agent):
    """
    Scripted agent with predefined behavior patterns.

    NPCAgent follows a BehaviorScript that determines its actions.
    Scripts can be simple patrols, complex guard behaviors, or
    merchant interactions.

    The agent can also have a fallback DecisionPolicy that takes
    over when the script is complete or interrupted.

    Use cases:
    - Guards: Patrol route, attack intruders (GuardScript)
    - Merchants: Stay in place, respond to trade requests (MerchantScript)
    - Workers: Gather resources, return to base (WorkerScript)
    - Patrols: Move between waypoints (PatrolScript)

    Attributes:
        behavior_script: Current BehaviorScript (or None)
        fallback_policy: Policy to use when script is unavailable
        legacy_script: Legacy callable-based script (deprecated)

    Design Patterns:
        - Strategy: BehaviorScript is pluggable
        - Template Method: Inherits sense-decide-act lifecycle
        - State: Script state machine

    Examples:
        >>> from traits import TraitGenerator
        >>> traits = TraitGenerator.balanced_traits()
        >>> waypoints = [Position(0, 0), Position(10, 10)]
        >>> script = GuardScript(waypoints, guard_radius=5.0)
        >>> agent = NPCAgent("Guard", Position(0, 0), traits, script)
    """

    def __init__(
        self,
        name: str,
        position: Position,
        traits: AgentTraits,
        behavior_script: Optional[BehaviorScript] = None,
        fallback_policy: Optional[DecisionPolicy] = None,
        legacy_script: Optional[List[Callable]] = None,
        loop_script: bool = True
    ) -> None:
        """
        Initialize an NPCAgent.

        Args:
            name: Agent's name
            position: Starting position
            traits: Agent characteristics
            behavior_script: BehaviorScript for scripted actions
            fallback_policy: Policy when script unavailable
            legacy_script: Deprecated callable-based script
            loop_script: Whether to loop legacy script

        Examples:
            >>> traits = TraitGenerator.balanced_traits()
            >>> script = PatrolScript([Position(0, 0), Position(10, 10)])
            >>> agent = NPCAgent("Patrol", Position(0, 0), traits, script)
        """
        super().__init__(name, position, traits)

        # New BehaviorScript system
        self._behavior_script: Optional[BehaviorScript] = behavior_script
        self._fallback_policy: Optional[DecisionPolicy] = fallback_policy

        # Legacy support for callable-based scripts
        self.behavior_script: List[Callable] = legacy_script or []
        self.script_index: int = 0
        self.loop_script: bool = loop_script

    def sense(self, world: World) -> Any:
        """
        Sense the environment.

        NPCs sense their environment similar to other agents,
        but their scripted behavior may ignore certain information.

        Args:
            world (World): The world instance

        Returns:
            Any: Perceived information (SensorData once behavior system exists)

        Note:
            To be implemented once behavior system exists.
        """
        raise NotImplementedError(
            "sense() will be implemented once behavior system exists"
        )

    def decide(self, sensor_data: Any) -> Optional[Action]:
        """
        Follow behavior script to decide action.

        Decision Process (BehaviorScript):
        1. Check if script is available and running
        2. Get action from script
        3. If script complete/unavailable, use fallback policy
        4. If no fallback, return None

        Legacy Process (callable script):
        1. Get current behavior from script at script_index
        2. Execute behavior function with sensor_data
        3. Advance script_index
        4. Loop back to start if at end and loop_script is True

        Args:
            sensor_data: Sensed information

        Returns:
            Optional[Action]: Scripted action

        Note:
            Implementation would:
            1. Try BehaviorScript first
            2. Fall back to legacy script
            3. Use fallback_policy if both unavailable
        """
        # Implementation would:
        #
        # # Try new BehaviorScript system first
        # if self._behavior_script is not None:
        #     if self._behavior_script.state == ScriptState.RUNNING:
        #         action = self._behavior_script.get_action(sensor_data, self)
        #         if action is not None:
        #             return action
        #
        #     # Script complete or returned None
        #     if self._behavior_script.is_complete():
        #         # Use fallback policy
        #         if self._fallback_policy is not None:
        #             return self._fallback_policy.choose_action(sensor_data, self)
        #         return None
        #
        # # Legacy callable-based script
        # if self.behavior_script:
        #     if self.script_index < len(self.behavior_script):
        #         behavior = self.behavior_script[self.script_index]
        #         action = behavior(sensor_data)
        #         self.script_index += 1
        #
        #         if self.script_index >= len(self.behavior_script) and self.loop_script:
        #             self.script_index = 0
        #
        #         return action
        #
        # # Fallback policy
        # if self._fallback_policy is not None:
        #     return self._fallback_policy.choose_action(sensor_data, self)
        #
        # return None

        raise NotImplementedError(
            "decide() - Interface design complete. "
            "Implementation requires integration with active simulation."
        )

    def act(self, action: Any, world: World) -> None:
        """
        Execute the scripted action.

        Args:
            action (Any): The action to execute
            world (World): The world instance

        Note:
            To be implemented once behavior system exists.
        """
        raise NotImplementedError(
            "act() will be implemented once behavior system exists"
        )

    def set_behavior_script(self, script: List[Callable]) -> None:
        """
        Set a new behavior script.

        Replaces current script and resets script index.

        Args:
            script (List[Callable]): New behavior sequence

        Examples:
            >>> def patrol_north(sensor_data):
            ...     return MoveAction(direction="north")
            >>> def patrol_south(sensor_data):
            ...     return MoveAction(direction="south")
            >>> agent.set_behavior_script([patrol_north, patrol_south])
        """
        self.behavior_script = script
        self.script_index = 0

    def add_behavior(self, behavior: Callable) -> None:
        """
        Append a behavior to the end of the script.

        Args:
            behavior (Callable): Behavior function to add
        """
        self.behavior_script.append(behavior)

    def insert_behavior(self, index: int, behavior: Callable) -> None:
        """
        Insert a behavior at a specific position in the script.

        Args:
            index (int): Position to insert at
            behavior (Callable): Behavior function to insert

        Raises:
            IndexError: If index is out of range
        """
        self.behavior_script.insert(index, behavior)

    def remove_behavior(self, index: int) -> Callable:
        """
        Remove and return a behavior from the script.

        Args:
            index (int): Position to remove from

        Returns:
            Callable: Removed behavior function

        Raises:
            IndexError: If index is out of range
        """
        return self.behavior_script.pop(index)

    def clear_script(self) -> None:
        """Clear all behaviors from the script."""
        self.behavior_script.clear()
        self.script_index = 0

    def reset_script_index(self) -> None:
        """Reset script execution to the beginning."""
        self.script_index = 0

    def get_script_progress(self) -> tuple[int, int]:
        """
        Get current script progress.

        Returns:
            tuple[int, int]: (current_index, total_behaviors)

        Examples:
            >>> current, total = agent.get_script_progress()
            >>> print(f"Progress: {current}/{total}")
        """
        return (self.script_index, len(self.behavior_script))

    def is_script_complete(self) -> bool:
        """
        Check if script has finished (only relevant if loop_script=False).

        Returns:
            bool: True if script_index >= script length
        """
        return self.script_index >= len(self.behavior_script)

    # New BehaviorScript management methods

    def set_script(self, script: BehaviorScript) -> None:
        """
        Set a new BehaviorScript.

        Replaces current script with the new one.

        Args:
            script: New BehaviorScript to use

        Examples:
            >>> agent.set_script(GuardScript(waypoints))
        """
        self._behavior_script = script

    def get_script(self) -> Optional[BehaviorScript]:
        """
        Get current BehaviorScript.

        Returns:
            Optional[BehaviorScript]: Current script or None
        """
        return self._behavior_script

    def clear_script(self) -> None:
        """Remove current BehaviorScript."""
        self._behavior_script = None

    def pause_script(self) -> None:
        """Pause current script execution."""
        if self._behavior_script is not None:
            self._behavior_script.pause()

    def resume_script(self) -> None:
        """Resume paused script execution."""
        if self._behavior_script is not None:
            self._behavior_script.resume()

    def interrupt_script(self) -> None:
        """Interrupt script for emergency behavior."""
        if self._behavior_script is not None:
            self._behavior_script.interrupt()

    def reset_script(self) -> None:
        """Reset current script to initial state."""
        if self._behavior_script is not None:
            self._behavior_script.reset()

    def set_fallback_policy(self, policy: DecisionPolicy) -> None:
        """
        Set fallback decision policy.

        Used when script is complete or unavailable.

        Args:
            policy: DecisionPolicy to use as fallback
        """
        self._fallback_policy = policy

    def get_script_state(self) -> Optional[ScriptState]:
        """
        Get current script state.

        Returns:
            Optional[ScriptState]: Script state or None if no script
        """
        if self._behavior_script is not None:
            return self._behavior_script.state
        return None

    def __repr__(self) -> str:
        """
        String representation of NPCAgent.

        Returns:
            str: Detailed representation
        """
        script_info = "None"
        if self._behavior_script is not None:
            script_info = f"{self._behavior_script.name}({self._behavior_script.state.name})"

        return (
            f"NPCAgent("
            f"name={self.name}, "
            f"pos={self.position}, "
            f"script={script_info})"
        )
