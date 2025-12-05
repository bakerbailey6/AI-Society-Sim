"""
Stockpile Module - Shared Storage Locations

This module provides stockpile functionality for centralized resource storage
that multiple agents can access.

Design Patterns:
    - Facade: Simplifies inventory access for shared storage
    - Strategy: Access control strategies

SOLID Principles:
    - Single Responsibility: Manages only shared storage
    - Open/Closed: Extensible via access control strategies
    - Dependency Inversion: Depends on abstract access control
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Optional, List, Tuple
from dataclasses import dataclass

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from world.position import Position
from resources.resource import ResourceType
from inventory.inventory import Inventory
from inventory.capacity_strategy import CapacityStrategy, UnlimitedCapacity
from inventory.resource_stack import ResourceStack


class AccessControlStrategy(ABC):
    """
    Abstract strategy for stockpile access control.

    Defines who can deposit to and withdraw from a stockpile.
    """

    @abstractmethod
    def can_deposit(self, agent_id: str, stockpile: Stockpile) -> bool:
        """
        Check if agent can deposit to stockpile.

        Args:
            agent_id: Agent's unique identifier
            stockpile: The stockpile to check

        Returns:
            bool: True if deposit is allowed
        """
        pass

    @abstractmethod
    def can_withdraw(self, agent_id: str, stockpile: Stockpile) -> bool:
        """
        Check if agent can withdraw from stockpile.

        Args:
            agent_id: Agent's unique identifier
            stockpile: The stockpile to check

        Returns:
            bool: True if withdrawal is allowed
        """
        pass


class PublicAccess(AccessControlStrategy):
    """
    Public access strategy - anyone can deposit and withdraw.

    Useful for communal storage or resource nodes.
    """

    def can_deposit(self, agent_id: str, stockpile: Stockpile) -> bool:
        """Always allows deposits."""
        return True

    def can_withdraw(self, agent_id: str, stockpile: Stockpile) -> bool:
        """Always allows withdrawals."""
        return True


class PrivateAccess(AccessControlStrategy):
    """
    Private access strategy - only owner can access.

    Attributes:
        owner_id: ID of the owning agent
    """

    def __init__(self, owner_id: str):
        """
        Initialize private access.

        Args:
            owner_id: Agent ID of the owner
        """
        self.owner_id = owner_id

    def can_deposit(self, agent_id: str, stockpile: Stockpile) -> bool:
        """Only owner can deposit."""
        return agent_id == self.owner_id

    def can_withdraw(self, agent_id: str, stockpile: Stockpile) -> bool:
        """Only owner can withdraw."""
        return agent_id == self.owner_id


class FactionAccess(AccessControlStrategy):
    """
    Faction-based access strategy - only faction members can access.

    Attributes:
        faction_id: ID of the faction
        allowed_agent_ids: Set of agent IDs in the faction
    """

    def __init__(self, faction_id: str):
        """
        Initialize faction access.

        Args:
            faction_id: Faction's unique identifier
        """
        self.faction_id = faction_id
        self.allowed_agent_ids: set = set()

    def add_member(self, agent_id: str) -> None:
        """
        Add agent to faction.

        Args:
            agent_id: Agent to add
        """
        self.allowed_agent_ids.add(agent_id)

    def remove_member(self, agent_id: str) -> None:
        """
        Remove agent from faction.

        Args:
            agent_id: Agent to remove
        """
        self.allowed_agent_ids.discard(agent_id)

    def can_deposit(self, agent_id: str, stockpile: Stockpile) -> bool:
        """Only faction members can deposit."""
        return agent_id in self.allowed_agent_ids

    def can_withdraw(self, agent_id: str, stockpile: Stockpile) -> bool:
        """Only faction members can withdraw."""
        return agent_id in self.allowed_agent_ids


@dataclass
class StockpileTransaction:
    """
    Record of a stockpile transaction.

    Attributes:
        agent_id: ID of agent involved
        resource_type: Type of resource
        quantity: Amount transferred
        timestamp: When transaction occurred
        is_deposit: True for deposit, False for withdrawal
    """
    agent_id: str
    resource_type: ResourceType
    quantity: float
    timestamp: float
    is_deposit: bool


class Stockpile:
    """
    Shared storage location for groups or factions.

    Stockpiles are stationary storage locations that multiple agents
    can deposit to and withdraw from, with optional access control.

    Stockpiles track transaction history for auditing and analysis.

    Attributes:
        stockpile_id: Unique identifier
        position: World position of the stockpile
        inventory: The underlying inventory
        access_control: Strategy for who can access
        name: Human-readable name

    Examples:
        >>> from inventory import Stockpile, PublicAccess, UnlimitedCapacity
        >>> stockpile = Stockpile(
        ...     "sp_001",
        ...     Position(10, 10),
        ...     UnlimitedCapacity(),
        ...     PublicAccess(),
        ...     name="Village Storage"
        ... )
        >>> stockpile.deposit("agent_1", food_stack, 100.0)
        True
    """

    def __init__(
        self,
        stockpile_id: str,
        position: Position,
        capacity_strategy: CapacityStrategy = None,
        access_control: AccessControlStrategy = None,
        name: str = "Stockpile"
    ):
        """
        Initialize a stockpile.

        Args:
            stockpile_id: Unique identifier
            position: World position
            capacity_strategy: Capacity limits (default: unlimited)
            access_control: Access control strategy (default: public)
            name: Human-readable name
        """
        self._stockpile_id = stockpile_id
        self._position = position
        self._name = name

        # Default to unlimited capacity and public access
        capacity = capacity_strategy if capacity_strategy else UnlimitedCapacity()
        self._access_control = access_control if access_control else PublicAccess()

        # Create underlying inventory
        self._inventory = Inventory(stockpile_id, capacity, f"{name} Storage")

        # Transaction history
        self._transactions: List[StockpileTransaction] = []

    # --- Properties ---

    @property
    def stockpile_id(self) -> str:
        """Get the stockpile's unique identifier."""
        return self._stockpile_id

    @property
    def position(self) -> Position:
        """Get stockpile position."""
        return self._position

    @property
    def inventory(self) -> Inventory:
        """
        Get the inventory (read-only access).

        Returns:
            Inventory: The underlying inventory
        """
        return self._inventory

    @property
    def name(self) -> str:
        """Get the stockpile name."""
        return self._name

    # --- Access Control ---

    def can_deposit(self, agent_id: str) -> bool:
        """
        Check if agent can deposit to this stockpile.

        Args:
            agent_id: Agent's identifier

        Returns:
            bool: True if deposit is allowed
        """
        return self._access_control.can_deposit(agent_id, self)

    def can_withdraw(self, agent_id: str) -> bool:
        """
        Check if agent can withdraw from this stockpile.

        Args:
            agent_id: Agent's identifier

        Returns:
            bool: True if withdrawal is allowed
        """
        return self._access_control.can_withdraw(agent_id, self)

    # --- Operations ---

    def deposit(
        self,
        agent_id: str,
        stack: ResourceStack,
        timestamp: float
    ) -> bool:
        """
        Deposit resources into stockpile.

        Args:
            agent_id: Agent making the deposit
            stack: Resources to deposit
            timestamp: Current simulation time

        Returns:
            bool: True if deposited successfully

        Examples:
            >>> success = stockpile.deposit("agent_1", food_stack, 100.0)
            >>> if success:
            ...     print("Deposited successfully")
        """
        if not self.can_deposit(agent_id):
            return False

        if self._inventory.add(stack):
            # Record transaction
            transaction = StockpileTransaction(
                agent_id=agent_id,
                resource_type=stack.resource_type,
                quantity=stack.quantity,
                timestamp=timestamp,
                is_deposit=True
            )
            self._transactions.append(transaction)
            return True

        return False

    def withdraw(
        self,
        agent_id: str,
        resource_type: ResourceType,
        quantity: float,
        timestamp: float
    ) -> Optional[ResourceStack]:
        """
        Withdraw resources from stockpile.

        Args:
            agent_id: Agent making the withdrawal
            resource_type: Type of resource to withdraw
            quantity: Amount to withdraw
            timestamp: Current simulation time

        Returns:
            Optional[ResourceStack]: Withdrawn resources, or None if failed

        Examples:
            >>> stack = stockpile.withdraw("agent_1", ResourceType.FOOD, 10.0, 101.0)
            >>> if stack:
            ...     print(f"Withdrew {stack.quantity} food")
        """
        if not self.can_withdraw(agent_id):
            return None

        stack = self._inventory.remove(resource_type, quantity)
        if stack:
            # Record transaction
            transaction = StockpileTransaction(
                agent_id=agent_id,
                resource_type=stack.resource_type,
                quantity=stack.quantity,
                timestamp=timestamp,
                is_deposit=False
            )
            self._transactions.append(transaction)

        return stack

    # --- Query Methods ---

    def get_quantity(self, resource_type: ResourceType) -> float:
        """
        Get quantity of a resource in stockpile.

        Args:
            resource_type: Type of resource

        Returns:
            float: Total quantity
        """
        return self._inventory.get_quantity(resource_type)

    def has_resource(self, resource_type: ResourceType, quantity: float = 1.0) -> bool:
        """
        Check if stockpile has enough of a resource.

        Args:
            resource_type: Type of resource
            quantity: Minimum quantity required

        Returns:
            bool: True if stockpile has >= quantity
        """
        return self._inventory.has_resource(resource_type, quantity)

    def get_transaction_history(
        self,
        agent_id: Optional[str] = None,
        resource_type: Optional[ResourceType] = None
    ) -> List[StockpileTransaction]:
        """
        Get transaction history with optional filtering.

        Args:
            agent_id: Filter by agent (None = all agents)
            resource_type: Filter by resource type (None = all types)

        Returns:
            List[StockpileTransaction]: Filtered transaction history
        """
        filtered = self._transactions

        if agent_id:
            filtered = [t for t in filtered if t.agent_id == agent_id]

        if resource_type:
            filtered = [t for t in filtered if t.resource_type == resource_type]

        return filtered

    def get_deposits_by_agent(self, agent_id: str) -> List[StockpileTransaction]:
        """Get all deposits made by a specific agent."""
        return [
            t for t in self._transactions
            if t.agent_id == agent_id and t.is_deposit
        ]

    def get_withdrawals_by_agent(self, agent_id: str) -> List[StockpileTransaction]:
        """Get all withdrawals made by a specific agent."""
        return [
            t for t in self._transactions
            if t.agent_id == agent_id and not t.is_deposit
        ]

    def get_net_contribution(self, agent_id: str) -> Dict[ResourceType, float]:
        """
        Calculate net contribution by agent (deposits - withdrawals).

        Args:
            agent_id: Agent to analyze

        Returns:
            Dict[ResourceType, float]: Net contribution by resource type
        """
        net = {}
        for transaction in self._transactions:
            if transaction.agent_id != agent_id:
                continue

            res_type = transaction.resource_type
            if res_type not in net:
                net[res_type] = 0.0

            if transaction.is_deposit:
                net[res_type] += transaction.quantity
            else:
                net[res_type] -= transaction.quantity

        return net

    # --- String Representation ---

    def __repr__(self):
        """Developer-friendly representation."""
        return (
            f"Stockpile({self._name}, "
            f"pos={self._position}, "
            f"{self._inventory.stack_count} stacks, "
            f"{len(self._transactions)} transactions)"
        )

    def __str__(self):
        """User-friendly representation."""
        return f"{self._name} @ {self._position}"
