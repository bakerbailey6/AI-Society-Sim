"""
Inventory Exceptions Module

Custom exceptions for inventory system operations.

SOLID Principles:
    - Single Responsibility: Each exception represents one error type
"""

from __future__ import annotations


class InventoryException(Exception):
    """Base exception for all inventory-related errors."""
    pass


class InsufficientResourcesException(InventoryException):
    """Raised when attempting to remove more resources than available."""

    def __init__(self, resource_type: str, requested: float, available: float):
        self.resource_type = resource_type
        self.requested = requested
        self.available = available
        super().__init__(
            f"Insufficient {resource_type}: requested {requested}, "
            f"but only {available} available"
        )


class CapacityExceededException(InventoryException):
    """Raised when attempting to add items beyond capacity."""

    def __init__(self, message: str = "Inventory capacity exceeded"):
        super().__init__(message)


class InvalidStackException(InventoryException):
    """Raised when operating on an invalid resource stack."""

    def __init__(self, message: str = "Invalid resource stack operation"):
        super().__init__(message)


class TransferException(InventoryException):
    """Raised when a resource transfer fails."""

    def __init__(self, message: str = "Resource transfer failed"):
        super().__init__(message)
