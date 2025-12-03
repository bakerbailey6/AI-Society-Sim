"""
AggressivePolicy Module - Skeleton Strategy for Competitive Behavior

This module provides the AggressivePolicy class skeleton, demonstrating
the Strategy pattern design for conflict-oriented decision making.

Design Patterns:
    - Strategy: AggressivePolicy is a concrete strategy (skeleton)
    - Command: Will use AttackAction and territory control actions (future)

SOLID Principles:
    - Single Responsibility: Only implements aggressive decision logic
    - Open/Closed: Designed for extension when combat system exists
    - Dependency Inversion: Will depend on combat/conflict abstractions

Note:
    This is a skeleton implementation for design demonstration.
    Full implementation requires the social/conflict system (Issue #5).
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


class AggressivePolicy(DecisionPolicy):
    """
    Skeleton strategy for aggressive, competitive decisions.

    AggressivePolicy demonstrates the Strategy pattern design for
    decision algorithms that prioritize competition, conflict, and
    territorial expansion over cooperation.

    When fully implemented, decision priorities will be:
    1. **Territory Control**: Defend and expand controlled areas
    2. **Resource Denial**: Prevent enemies from accessing resources
    3. **Tactical Combat**: Attack vulnerable enemies
    4. **Intimidation**: Establish dominance through shows of force
    5. **Strategic Positioning**: Control key map locations

    This is a design skeleton to demonstrate the Strategy pattern.
    Full implementation requires:
    - Social/conflict system (Issue #5)
    - Combat mechanics
    - Territory/influence system
    - Threat assessment algorithms

    Examples:
        >>> # Design example (not yet functional)
        >>> policy = AggressivePolicy()
        >>> action = policy.choose_action(sensor_data, agent)
        >>> # Will raise NotImplementedError until combat system exists
    """

    def __init__(self) -> None:
        """Initialize an AggressivePolicy."""
        super().__init__(
            name="Aggressive",
            description="Prioritize competition, conflict, and territory control"
        )

    def choose_action(
        self,
        sensor_data: Any,
        agent: Agent
    ) -> Optional[Action]:
        """
        Choose action based on aggressive strategy.

        When implemented, will analyze:
        - Nearby enemies and vulnerabilities
        - Strategic positions and chokepoints
        - Resource competition
        - Opportunities for expansion

        Args:
            sensor_data (Any): Sensor information
            agent (Agent): The decision-making agent

        Returns:
            Optional[Action]: Chosen action

        Raises:
            NotImplementedError: Combat system not yet implemented
        """
        raise NotImplementedError(
            "AggressivePolicy requires the social/conflict system (Issue #5) "
            "and combat mechanics to be implemented. This is a design skeleton "
            "demonstrating the Strategy pattern structure."
            "\n\nWhen implemented, will prioritize:"
            "\n- Attacking weak enemies"
            "\n- Controlling strategic positions"
            "\n- Denying resources to competitors"
            "\n- Expanding territorial influence"
        )

    def __repr__(self) -> str:
        """String representation."""
        return f"AggressivePolicy(priority='combat,territory,expansion')"
