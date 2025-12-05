"""
CooperativePolicy Module - Skeleton Strategy for Group Benefit

This module provides the CooperativePolicy class skeleton, demonstrating
the Strategy pattern design for collaborative decision making.

Design Patterns:
    - Strategy: CooperativePolicy is a concrete strategy (skeleton)
    - Observer: Will use for coordinating group actions (future)

SOLID Principles:
    - Single Responsibility: Only implements cooperative decision logic
    - Open/Closed: Designed for extension when social system exists
    - Dependency Inversion: Will depend on social/faction abstractions

Note:
    This is a skeleton implementation for design demonstration.
    Full implementation requires the social/faction system (Issue #5).
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Optional, Any

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from policies.policy import DecisionPolicy

if TYPE_CHECKING:
    from agents.agent import Agent
    from actions.action import Action


class CooperativePolicy(DecisionPolicy):
    """
    Skeleton strategy for cooperative, group-focused decisions.

    CooperativePolicy demonstrates the Strategy pattern design for
    decision algorithms that prioritize group benefit and collaboration
    over individual gain.

    When fully implemented, decision priorities will be:
    1. **Group Survival**: Help struggling allies
    2. **Resource Sharing**: Trade surplus resources
    3. **Coordination**: Synchronize actions with faction
    4. **Alliance Building**: Form and maintain alliances
    5. **Collective Defense**: Protect group members

    This is a design skeleton to demonstrate the Strategy pattern.
    Full implementation requires:
    - Social/faction system (Issue #5)
    - Communication system for coordination
    - Relationship tracking
    - Shared resource pools

    Examples:
        >>> # Design example (not yet functional)
        >>> policy = CooperativePolicy()
        >>> action = policy.choose_action(sensor_data, agent)
        >>> # Will raise NotImplementedError until social system exists
    """

    def __init__(self) -> None:
        """Initialize a CooperativePolicy."""
        super().__init__(
            name="Cooperative",
            description="Prioritize group benefit and collaboration"
        )

    def choose_action(
        self,
        sensor_data: Any,
        agent: Agent
    ) -> Optional[Action]:
        """
        Choose action based on cooperative strategy.

        When implemented, will analyze:
        - Nearby allies and their needs
        - Group resources and deficits
        - Collective threats
        - Opportunities for collaboration

        Args:
            sensor_data (Any): Sensor information
            agent (Agent): The decision-making agent

        Returns:
            Optional[Action]: Chosen action

        Raises:
            NotImplementedError: Social system not yet implemented
        """
        raise NotImplementedError(
            "CooperativePolicy requires the social/faction system (Issue #5) "
            "to be implemented. This is a design skeleton demonstrating the "
            "Strategy pattern structure."
            "\n\nWhen implemented, will prioritize:"
            "\n- Helping low-health allies"
            "\n- Sharing surplus resources"
            "\n- Coordinating group actions"
            "\n- Maintaining alliances"
        )

    def __repr__(self) -> str:
        """String representation."""
        return f"CooperativePolicy(priority='group,sharing,coordination')"
