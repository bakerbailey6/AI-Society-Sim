"""
NPCAgent Module - Scripted Behavior Agent

This module provides an agent with predefined, scripted behavior patterns
suitable for specific roles like guards, merchants, or workers.

Design Patterns:
    - Strategy Pattern: Behavior script is pluggable
    - Command Pattern: Scripts are sequences of callable behaviors

SOLID Principles:
    - Single Responsibility: Executes scripted behaviors
    - Open/Closed: New scripts can be added without modification
    - Liskov Substitution: Can be used anywhere Agent is expected
"""

from __future__ import annotations
from typing import Optional, List, Callable, Any, TYPE_CHECKING

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import Agent
from traits import AgentTraits
from world.position import Position

if TYPE_CHECKING:
    from world.world import World


class NPCAgent(Agent):
    """
    Scripted agent with predefined behavior patterns.

    NPCAgent follows a script (sequence of behaviors) that can be
    customized for specific roles. The script loops continuously,
    providing predictable, reliable behavior.

    Use cases:
    - Guards: Patrol route, attack intruders
    - Merchants: Stay in place, respond to trade requests
    - Workers: Gather resources, return to base
    - Companions: Follow player, assist in combat

    Attributes:
        behavior_script (List[Callable]): Sequence of behavior functions
        script_index (int): Current position in script
        loop_script (bool): Whether to loop back to start when done
    """

    def __init__(
        self,
        name: str,
        position: Position,
        traits: AgentTraits,
        behavior_script: Optional[List[Callable]] = None,
        loop_script: bool = True
    ) -> None:
        """
        Initialize an NPCAgent.

        Args:
            name (str): Agent's name
            position (Position): Starting position
            traits (AgentTraits): Agent characteristics
            behavior_script (Optional[List[Callable]]): Sequence of behavior functions
            loop_script (bool): Whether to loop script (default True)

        Examples:
            >>> from traits import TraitGenerator
            >>> traits = TraitGenerator.balanced_traits()
            >>> # Script will be list of callable behaviors
            >>> agent = NPCAgent("Guard", Position(30, 30), traits)
        """
        super().__init__(name, position, traits)

        self.behavior_script: List[Callable] = behavior_script or []
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

    def decide(self, sensor_data: Any) -> Optional[Any]:
        """
        Follow behavior script to decide action.

        Decision Process:
        1. Get current behavior from script at script_index
        2. Execute behavior function with sensor_data
        3. Advance script_index
        4. Loop back to start if at end and loop_script is True

        Args:
            sensor_data (Any): Sensed information (may be ignored by script)

        Returns:
            Optional[Any]: Scripted action (Action class once behavior system exists)

        Note:
            To be implemented once behavior system (Action classes) exists.
        """
        raise NotImplementedError(
            "decide() will be implemented once behavior system exists"
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

    def __repr__(self) -> str:
        """
        String representation of NPCAgent.

        Returns:
            str: Detailed representation
        """
        return (
            f"NPCAgent("
            f"name={self.name}, "
            f"pos={self.position}, "
            f"script_size={len(self.behavior_script)}, "
            f"index={self.script_index})"
        )
