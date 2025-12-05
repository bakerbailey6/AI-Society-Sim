"""
Policies Package - Strategy Pattern Implementation

This package provides the decision policy system for the AI Society Simulator,
demonstrating the Strategy pattern where decision algorithms are encapsulated
as interchangeable objects.

Design Patterns:
    - Strategy: Each policy is an interchangeable decision algorithm
    - Dependency Inversion: Policies depend on abstractions (Agent, SensorData)

SOLID Principles:
    - Single Responsibility: Each policy implements one strategy
    - Open/Closed: New policies can be added without modifying existing code
    - Liskov Substitution: All policies are substitutable for Policy base
    - Interface Segregation: Minimal policy interface (choose_action)
    - Dependency Inversion: Policies depend on abstractions

Exports:
    DecisionPolicy: Abstract base class for all decision policies
    SelfishPolicy: Prioritize individual survival and resource gathering
    CooperativePolicy: Prioritize group benefit and collaboration (skeleton)
    AggressivePolicy: Prioritize competition and conflict (skeleton)
"""

from .policy import DecisionPolicy
from .selfish import SelfishPolicy
from .cooperative import CooperativePolicy
from .aggressive import AggressivePolicy

__all__ = [
    "DecisionPolicy",
    "SelfishPolicy",
    "CooperativePolicy",
    "AggressivePolicy",
]
