"""
GatherAction Module - Concrete Command for Resource Collection

This module provides the GatherAction class, demonstrating the Command
pattern for agents collecting resources from their current cell.

Design Patterns:
    - Command: GatherAction is a concrete command
    - Template Method: Inherits execution structure from Action base

SOLID Principles:
    - Single Responsibility: Only handles resource gathering
    - Open/Closed: Can extend gathering behavior without modification
    - Liskov Substitution: Substitutable for Action base class
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from actions.action import Action

if TYPE_CHECKING:
    from agents.agent import Agent
    from world.world import World
    from resources.resource import Resource


class GatherAction(Action):
    """
    Concrete command for gathering resources from the current cell.

    GatherAction demonstrates the Command pattern by encapsulating
    the resource gathering request as an object. The action:
    - Validates resources are available in the current cell
    - Removes resource from cell
    - Adds resource to agent inventory (placeholder)
    - Consumes energy

    This action is not reversible in the current design (resources
    are consumed), but could be made reversible by implementing
    a "drop resource" undo operation.

    Attributes:
        resource_type (Optional[str]): Specific resource type to gather,
                                       or None to gather any available

    Examples:
        >>> # Gather any available resource
        >>> action = GatherAction()
        >>> if action.can_execute(agent, world):
        ...     success = action.execute(agent, world)
        ...
        >>> # Gather specific resource type
        >>> action = GatherAction(resource_type="Food")
        >>> success = action.execute(agent, world)
    """

    def __init__(self, resource_type: Optional[str] = None) -> None:
        """
        Initialize a GatherAction.

        Args:
            resource_type (Optional[str]): Specific resource type to gather,
                                          or None for any resource
        """
        desc = f"Gather {resource_type}" if resource_type else "Gather resource"
        super().__init__(
            name="Gather",
            description=desc
        )
        self._resource_type: Optional[str] = resource_type
        self._gathered_resource: Optional[Resource] = None

    @property
    def resource_type(self) -> Optional[str]:
        """Get the target resource type."""
        return self._resource_type

    def execute(self, agent: Agent, world: World) -> bool:
        """
        Execute the gather action.

        Collects a resource from the agent's current cell and adds it
        to the agent's inventory.

        Args:
            agent (Agent): The agent gathering resources
            world (World): The world containing resources

        Returns:
            bool: True if resource gathered successfully, False otherwise

        Note:
            This method demonstrates the Command pattern's execute().
            It:
            1. Validates preconditions
            2. Consumes energy
            3. Finds and removes resource from cell
            4. Adds resource to agent inventory
            5. Restores energy (if food resource)
        """
        # Validate can execute
        if not self.can_execute(agent, world):
            return False

        # Consume energy
        if not agent.consume_energy(self.energy_cost):
            return False

        # Get current cell
        current_cell = world.get_cell(agent.position)
        if not current_cell:
            return False

        # Find resource to gather
        resource = None
        if self._resource_type:
            # Look for specific type
            for res in current_cell.resources:
                if res.__class__.__name__ == self._resource_type:
                    resource = res
                    break
        else:
            # Take any available resource
            if current_cell.resources:
                resource = current_cell.resources[0]

        if not resource:
            return False

        # Remove resource from cell
        current_cell.remove_resource(resource)
        self._gathered_resource = resource

        # Add to agent inventory (placeholder - will integrate with inventory system)
        # For now, just store in agent's inventory dict
        resource_name = resource.__class__.__name__
        if resource_name not in agent._inventory:
            agent._inventory[resource_name] = 0
        agent._inventory[resource_name] += resource.amount

        # If it's food, restore energy
        if resource_name == "Food":
            agent.restore_energy(resource.amount * 2.0)  # Food restores 2x its amount

        return True

    def can_execute(self, agent: Agent, world: World) -> bool:
        """
        Check if gather action can be executed.

        Validates:
        - Agent is alive
        - Agent has sufficient energy
        - Current cell has resources
        - If specific type requested, that type exists

        Args:
            agent (Agent): The agent attempting to gather
            world (World): The world context

        Returns:
            bool: True if gathering is valid, False otherwise
        """
        # Check agent is alive
        if not agent.is_alive():
            return False

        # Check energy
        if agent.energy < self.energy_cost:
            return False

        # Get current cell
        current_cell = world.get_cell(agent.position)
        if not current_cell:
            return False

        # Check for resources
        if not current_cell.resources:
            return False

        # If specific type requested, check it exists
        if self._resource_type:
            found = any(
                res.__class__.__name__ == self._resource_type
                for res in current_cell.resources
            )
            if not found:
                return False

        return True

    @property
    def energy_cost(self) -> float:
        """
        Get the energy cost of gathering.

        Gathering has a moderate energy cost.

        Returns:
            float: Energy cost (2.0)
        """
        return 2.0

    def __repr__(self) -> str:
        """
        String representation.

        Returns:
            str: Detailed representation
        """
        return (
            f"GatherAction(type={self._resource_type}, "
            f"cost={self.energy_cost})"
        )
