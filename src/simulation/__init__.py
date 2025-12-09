"""
Simulation Engine Package

This package provides the core simulation engine that orchestrates
agent behavior, world updates, and analytics collection.

Modules:
    - scheduler: Agent update scheduling strategies (Strategy Pattern)
    - analytics: Statistics collection and analysis (Observer Pattern)
    - engine: Main simulation orchestration (Facade Pattern)

Design Patterns:
    - Facade Pattern: SimulationEngine provides simple interface
    - Strategy Pattern: Interchangeable scheduling algorithms
    - Observer Pattern: Analytics observers for events

SOLID Principles:
    - Single Responsibility: Each module has one purpose
    - Open/Closed: Extensible schedulers and analyzers
    - Dependency Inversion: Depends on abstractions

Integration:
    - Uses agents/ for agent updates
    - Uses world/ for environment simulation
    - Uses economy/ for market simulation
    - Uses social/ for relationship updates
"""

from simulation.scheduler import (
    SchedulingStrategy,
    SequentialScheduler,
    RandomScheduler,
    PriorityScheduler,
    RoundRobinScheduler,
)
from simulation.analytics import (
    StepStatistics,
    AgentStatistics,
    FactionStatistics,
    AnalyticsCollector,
    WealthDistributionAnalyzer,
    FactionAnalyzer,
    SurvivalAnalyzer,
)
from simulation.engine import (
    SimulationState,
    SimulationConfig,
    SimulationObserver,
    SimulationEngine,
    StepResult,
)

__all__ = [
    # Scheduler
    "SchedulingStrategy",
    "SequentialScheduler",
    "RandomScheduler",
    "PriorityScheduler",
    "RoundRobinScheduler",
    # Analytics
    "StepStatistics",
    "AgentStatistics",
    "FactionStatistics",
    "AnalyticsCollector",
    "WealthDistributionAnalyzer",
    "FactionAnalyzer",
    "SurvivalAnalyzer",
    # Engine
    "SimulationState",
    "SimulationConfig",
    "SimulationObserver",
    "SimulationEngine",
    "StepResult",
]
