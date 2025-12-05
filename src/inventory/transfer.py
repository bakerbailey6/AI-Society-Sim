"""
Transfer Module - Resource Transfer Operations

This module provides high-level API for safely transferring resources
between inventories with atomicity guarantees.

Design Patterns:
    - Command: Transfer operations as objects
    - Transaction: Atomic transfers with rollback

SOLID Principles:
    - Single Responsibility: Only handles resource transfers
    - Open/Closed: Extensible with new transfer types
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional, TYPE_CHECKING
from enum import Enum

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from resources.resource import ResourceType
from inventory.exceptions import TransferException

if TYPE_CHECKING:
    from inventory.inventory import Inventory
    from agents.agent import Agent


class TransferError(Enum):
    """
    Enumeration of transfer error types.

    Attributes:
        INSUFFICIENT_RESOURCES: Source doesn't have enough resources
        DESTINATION_FULL: Destination at capacity
        REMOVAL_FAILED: Failed to remove from source
        ADDITION_FAILED: Failed to add to destination
        ACCESS_DENIED: Agent doesn't have permission
    """
    INSUFFICIENT_RESOURCES = "insufficient_resources"
    DESTINATION_FULL = "destination_full"
    REMOVAL_FAILED = "removal_failed"
    ADDITION_FAILED = "addition_failed"
    ACCESS_DENIED = "access_denied"


@dataclass
class TransferResult:
    """
    Result of a transfer operation.

    Attributes:
        success: Whether transfer succeeded
        error: Error type if failed (None if success)
        quantity_transferred: Actual amount transferred
    """
    success: bool
    error: Optional[TransferError]
    quantity_transferred: float


@dataclass
class TradeResult:
    """
    Result of a trade operation.

    Attributes:
        success: Whether trade succeeded
        error: Error message if failed (None if success)
    """
    success: bool
    error: Optional[str]


class TransferManager:
    """
    Manages resource transfers between inventories.

    Provides high-level API for moving resources with validation
    and atomicity guarantees.

    All transfers are atomic - they either fully succeed or fully fail
    with no partial state changes.

    Examples:
        >>> from inventory.transfer import TransferManager
        >>> result = TransferManager.transfer(
        ...     source=agent1._inventory,
        ...     destination=agent2._inventory,
        ...     resource_type=ResourceType.FOOD,
        ...     quantity=10.0
        ... )
        >>> if result.success:
        ...     print(f"Transferred {result.quantity_transferred} food")
    """

    @staticmethod
    def transfer(
        source: Inventory,
        destination: Inventory,
        resource_type: ResourceType,
        quantity: float
    ) -> TransferResult:
        """
        Transfer resources from source to destination.

        Atomic operation - either fully succeeds or fully fails.

        Args:
            source: Source inventory
            destination: Destination inventory
            resource_type: Type of resource to transfer
            quantity: Amount to transfer

        Returns:
            TransferResult: Success/failure with details

        Examples:
            >>> result = TransferManager.transfer(
            ...     my_inventory,
            ...     their_inventory,
            ...     ResourceType.MATERIAL,
            ...     50.0
            ... )
        """
        # Validate source has resources
        if not source.has_resource(resource_type, quantity):
            return TransferResult(
                success=False,
                error=TransferError.INSUFFICIENT_RESOURCES,
                quantity_transferred=0
            )

        # Remove from source
        stack = source.remove(resource_type, quantity)
        if not stack:
            return TransferResult(
                success=False,
                error=TransferError.REMOVAL_FAILED,
                quantity_transferred=0
            )

        # Try to add to destination
        if destination.add(stack):
            return TransferResult(
                success=True,
                error=None,
                quantity_transferred=quantity
            )
        else:
            # Rollback: return to source
            source.add(stack)
            return TransferResult(
                success=False,
                error=TransferError.DESTINATION_FULL,
                quantity_transferred=0
            )

    @staticmethod
    def trade(
        agent_a: Agent,
        agent_b: Agent,
        agent_a_gives: Dict[ResourceType, float],
        agent_b_gives: Dict[ResourceType, float]
    ) -> TradeResult:
        """
        Execute an atomic trade between two agents.

        Both sides of the trade are validated first. If either side
        cannot complete their transfer, the entire trade is rejected.

        This is a transactional operation - either both transfers
        succeed or both fail with no changes.

        Args:
            agent_a: First agent
            agent_b: Second agent
            agent_a_gives: Resources agent A is giving {type: quantity}
            agent_b_gives: Resources agent B is giving {type: quantity}

        Returns:
            TradeResult: Success/failure with error message

        Examples:
            >>> # Agent A gives 10 food for agent B's 20 materials
            >>> result = TransferManager.trade(
            ...     agent_a,
            ...     agent_b,
            ...     agent_a_gives={ResourceType.FOOD: 10.0},
            ...     agent_b_gives={ResourceType.MATERIAL: 20.0}
            ... )
            >>> if result.success:
            ...     print("Trade completed!")
        """
        # Validate both agents have required resources
        for resource_type, quantity in agent_a_gives.items():
            if not agent_a._inventory.has_resource(resource_type, quantity):
                return TradeResult(
                    success=False,
                    error=f"Agent A lacks {quantity} {resource_type.value}"
                )

        for resource_type, quantity in agent_b_gives.items():
            if not agent_b._inventory.has_resource(resource_type, quantity):
                return TradeResult(
                    success=False,
                    error=f"Agent B lacks {quantity} {resource_type.value}"
                )

        # Execute transfers with rollback on failure
        transferred_to_b = []
        transferred_to_a = []

        try:
            # Agent A gives to Agent B
            for resource_type, quantity in agent_a_gives.items():
                result = TransferManager.transfer(
                    agent_a._inventory,
                    agent_b._inventory,
                    resource_type,
                    quantity
                )
                if not result.success:
                    raise TransferException(f"Transfer A->B failed: {result.error.value}")
                transferred_to_b.append((resource_type, quantity))

            # Agent B gives to Agent A
            for resource_type, quantity in agent_b_gives.items():
                result = TransferManager.transfer(
                    agent_b._inventory,
                    agent_a._inventory,
                    resource_type,
                    quantity
                )
                if not result.success:
                    raise TransferException(f"Transfer B->A failed: {result.error.value}")
                transferred_to_a.append((resource_type, quantity))

            return TradeResult(success=True, error=None)

        except TransferException as e:
            # Rollback all transfers
            for resource_type, quantity in transferred_to_b:
                TransferManager.transfer(
                    agent_b._inventory,
                    agent_a._inventory,
                    resource_type,
                    quantity
                )

            for resource_type, quantity in transferred_to_a:
                TransferManager.transfer(
                    agent_a._inventory,
                    agent_b._inventory,
                    resource_type,
                    quantity
                )

            return TradeResult(success=False, error=str(e))

    @staticmethod
    def split_transfer(
        source: Inventory,
        destinations: list[Inventory],
        resource_type: ResourceType,
        quantity: float
    ) -> Dict[str, TransferResult]:
        """
        Split resources evenly across multiple destinations.

        Useful for distributing resources from stockpile to multiple agents.

        Args:
            source: Source inventory
            destinations: List of destination inventories
            resource_type: Type of resource
            quantity: Total amount to split

        Returns:
            Dict[str, TransferResult]: Results keyed by destination owner_id
        """
        if not destinations:
            return {}

        # Calculate per-destination amount
        per_dest = quantity / len(destinations)

        results = {}
        for dest in destinations:
            result = TransferManager.transfer(
                source,
                dest,
                resource_type,
                per_dest
            )
            results[dest.owner_id] = result

        return results


class TransferCommand:
    """
    Command object for resource transfers (Command pattern).

    Encapsulates a transfer request that can be executed, validated,
    and potentially undone.

    Attributes:
        source: Source inventory
        destination: Destination inventory
        resource_type: Type of resource
        quantity: Amount to transfer
    """

    def __init__(
        self,
        source: Inventory,
        destination: Inventory,
        resource_type: ResourceType,
        quantity: float
    ):
        """
        Initialize transfer command.

        Args:
            source: Source inventory
            destination: Destination inventory
            resource_type: Type of resource
            quantity: Amount to transfer
        """
        self.source = source
        self.destination = destination
        self.resource_type = resource_type
        self.quantity = quantity
        self._executed = False
        self._result: Optional[TransferResult] = None

    def can_execute(self) -> bool:
        """
        Check if transfer can be executed.

        Returns:
            bool: True if transfer is valid
        """
        return self.source.has_resource(self.resource_type, self.quantity)

    def execute(self) -> TransferResult:
        """
        Execute the transfer.

        Returns:
            TransferResult: Result of the transfer
        """
        if self._executed:
            raise RuntimeError("Transfer already executed")

        self._result = TransferManager.transfer(
            self.source,
            self.destination,
            self.resource_type,
            self.quantity
        )
        self._executed = True
        return self._result

    def undo(self) -> TransferResult:
        """
        Undo the transfer (reverse it).

        Returns:
            TransferResult: Result of the reversal

        Raises:
            RuntimeError: If transfer hasn't been executed or failed
        """
        if not self._executed:
            raise RuntimeError("Cannot undo non-executed transfer")

        if not self._result or not self._result.success:
            raise RuntimeError("Cannot undo failed transfer")

        # Reverse the transfer
        return TransferManager.transfer(
            self.destination,
            self.source,
            self.resource_type,
            self.quantity
        )
